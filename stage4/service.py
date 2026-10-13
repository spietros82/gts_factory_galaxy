"""Bounded fair independent-line registry. Pixels-only frozen backend; loopback only."""
import argparse,copy,json,threading,time,hashlib,re,os,signal
from collections import OrderedDict,deque,Counter
from pathlib import Path
from datetime import datetime,timezone
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit,parse_qs
import numpy as np
from stage3.backend import NeuralBackend,STATIONS,WORDS
from stage3.service import validate_batch,explain_request,validate_explanation,utc
from stage3.monitor import Monitor
from stage4.timing import combined_timings
from factory.model import OllamaAdapter,ollama_payload

def percentiles(v):
 return dict(zip(['p50','p95','p99'],map(float,np.percentile(v,[50,95,99])))) if v else {'p50':0.,'p95':0.,'p99':0.}

class Engine:
 def __init__(self,cfg,backends=None):
  self.cfg=cfg;self.root=Path(cfg['data_path']);self.root.mkdir(parents=True,exist_ok=True)
  for d in ['frames','crops']:(self.root/d).mkdir(exist_ok=True)
  self.lock=threading.RLock();self.condition=threading.Condition(self.lock);self.active={};self.jobs=OrderedDict();self.busy=set();self.running={};self.running_since={};self.selected=cfg['device'];self.actual='unavailable';self.backends={};self.ready=False;self.gpu_status='initialising';self.counts=Counter();self.lines={};self.records=deque(maxlen=4096);self.reviews=deque(maxlen=192);self.ids=deque(maxlen=8192);self.ids_set=set();self.frame_ids=deque(maxlen=24576);self.frame_ids_set=set();self.joined_ids=deque(maxlen=8192);self.joined_set=set();self.trigger_latencies=deque(maxlen=20000);self.image_order=deque();self.latencies=deque(maxlen=20000);self.timing_samples=deque(maxlen=20000);self.started=time.monotonic();self.native={};self.native_wall=0;self.metrics={};self.stop_reason='';self.guard_since={};self.assistant_state='idle';self.assistant_text='No request; optional Qwen disabled in benchmark';self.assistant_event_id='';self.pending_explanation=False;self.ledger=Path(cfg['assistant_ledger']);self.calls=len(self.ledger.read_text().splitlines()) if self.ledger.exists() else 0;self.external_backends=backends;self.running_device='unavailable'
  self.monitor=Monitor();self.native_previous=None
  self.thread=threading.Thread(target=self.worker,daemon=True);self.thread.start()
  if cfg.get('monitoring',True):threading.Thread(target=self.monitor_loop,daemon=True).start()
 def append(self,name,value):
  # Bounded rotation; raw exact records remain in phase outputs until their explicit retention limit.
  with self.lock:
   p=self.root/name;limit=self.cfg['audit_segment_bytes'];segments=self.cfg['audit_segments']
   if p.exists() and p.stat().st_size>=limit:
    for i in range(segments-1,0,-1):
     src=p if i==1 else self.root/(name+'.'+str(i-1));dst=self.root/(name+'.'+str(i))
     if src.exists():src.replace(dst)
   with p.open('a') as f:f.write(json.dumps(value,allow_nan=False)+'\n')
 def register(self,values):
  if not isinstance(values,list) or not 1<=len(values)<=self.cfg['max_lines']:raise ValueError('1–48 lines required')
  active={}
  for v in values:
   if set(v)!={'line_id','session_id'} or any(not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',v[k]) for k in v):raise ValueError('Invalid registry')
   if v['line_id'] in active or v['session_id'] in active.values():raise ValueError('Duplicate line/session')
   active[v['line_id']]=v['session_id']
  with self.condition:
   self.active=active
   for line in list(self.jobs):
    if active.get(line)!=self.jobs[line][0]['session_id']:
     self.jobs.pop(line);self.counts['cancelled']+=3;self.busy.discard(line)
   for line,session in active.items():
    if self.lines.get(line,{}).get('session_id')!=session:self.lines[line]={'line_id':line,'session_id':session,'accepted':0,'completed':0,'dropped':0,'last_completed':0.,'latency_ms':0.}
   self.append('registry.jsonl',{'utc':utc(),'lines':values});self.condition.notify_all()
  return {'registered':len(active)}
 def submit(self,value):
  start=time.perf_counter();when,images=validate_batch(value);decode=(time.perf_counter()-start)*1000;line=value['line_id']
  with self.condition:
   self.counts['offered']+=3
   if self.active.get(line)!=value['session_id']:self.counts['rejected_session']+=3;raise ValueError('Removed/retired line session')
   if value['batch_id'] in self.ids_set:self.counts['duplicate']+=3;raise ValueError('Duplicate batch')
   if any(f['frame_id'] in self.frame_ids_set or (self.root/'frames'/(f['frame_id']+'.png')).exists() for f in value['frames']):raise ValueError('Reused frame ID')
   if line in self.busy or len(self.jobs)>=self.cfg['queue_capacity']:
    self.counts['dropped']+=3;self.lines[line]['dropped']+=3;raise ValueError('Backpressure: one pending/running batch per line; bounded global queue')
   if len(self.ids)==self.ids.maxlen:self.ids_set.discard(self.ids[0])
   self.ids.append(value['batch_id']);self.ids_set.add(value['batch_id'])
   for f in value['frames']:
    if len(self.frame_ids)==self.frame_ids.maxlen:self.frame_ids_set.discard(self.frame_ids[0])
    self.frame_ids.append(f['frame_id']);self.frame_ids_set.add(f['frame_id'])
   self.busy.add(line);self.jobs[line]=(copy.deepcopy(value),when,images,time.time(),decode);self.counts['accepted']+=3;self.lines[line]['accepted']+=3;self.condition.notify()
  return {'accepted':True,'batch_id':value['batch_id']}
 def worker(self):
  try:
   if self.external_backends is not None:self.backends=self.external_backends
   else:
    self.backends['cpu']=NeuralBackend(self.cfg['model_path'],'cpu')
    try:self.backends['gpu']=NeuralBackend(self.cfg['model_path'],'gpu');self.gpu_status='Verified AMD hardware GLSL compute: '+self.backends['gpu'].renderer
    except Exception as e:self.gpu_status='Unavailable: '+str(e)
   self.actual=self.selected if self.selected in self.backends else 'unavailable';self.append('cold-start.jsonl',{'utc':utc(),'cold_ms':{k:getattr(v,'cold_start_ms',0) for k,v in self.backends.items()},'gpu_status':self.gpu_status})
  except Exception as e:self.gpu_status='Model unavailable: '+str(e)
  self.ready=True
  while True:
   with self.condition:
    while not self.jobs:self.condition.wait()
    line,job=self.jobs.popitem(last=False);self.running[line]=job[0]['session_id'];self.running_since[line]=job[3];device=self.selected;self.running_device=device
   value,when,images,queued,decode=job;backend=self.backends.get(device);self.actual=device if backend else 'unavailable'
   for f,raw,image in images:
    with self.lock:
     if self.active.get(line)!=value['session_id']:self.counts['cancelled']+=1;continue
    began=time.time();age=began-when;reason=''
    if value['target_count']!=1 or not value['observations_available']:reason='Ambiguous association / missing observation'
    elif age<-.1 or age>self.cfg['max_age_seconds']:reason='Stale capture; no current judgement';self.counts['stale']+=1
    elif backend is None:reason='Selected backend unavailable; no CPU fallback'
    try:result=backend.predict(f['station_id'],image) if not reason else {}
    except Exception as e:reason='Inference failed: '+str(e);result={};self.counts['inference_errors']+=1
    if reason:result.update(decision='uncertain',wording=WORDS[f['station_id']][3],reason=reason,score=0.,device=device if backend else 'unavailable',backend='withheld / unavailable',model_sha256='',preprocess_ms=0.,transfer_ms=0.,inference_ms=0.,gpu_elapsed_ms=0.,classifier_ms=0.)
    io=time.perf_counter();(self.root/'frames'/(f['frame_id']+'.png')).write_bytes(raw);image.save(self.root/'crops'/(f['frame_id']+'.png'));storage=(time.perf_counter()-io)*1000
    result.update({k:value[k] for k in ['line_id','session_id','bottle_id','batch_id','capture_utc','source_time','product']});result.update(station_id=f['station_id'],frame_id=f['frame_id'],completed_utc=utc(),queue_ms=(began-queued)*1000,decode_crop_ms=decode,storage_ms=storage,end_to_end_ms=(time.time()-when)*1000,crop_url='/crop/'+f['frame_id'])
    with self.lock:
     self.image_order.append(f['frame_id'])
     while len(self.image_order)>self.cfg['image_limit']:
      old=self.image_order.popleft()
      for d in ['frames','crops']:(self.root/d/(old+'.png')).unlink(missing_ok=True)
     # Recheck after inference: old results retained as audit only, never attached to new session.
     result['retired']=self.active.get(line)!=value['session_id']
     self.append('requests.jsonl',{k:v for k,v in value.items() if k!='frames'}|{'frame_id':f['frame_id'],'station_id':f['station_id'],'image_sha256':hashlib.sha256(raw).hexdigest(),'roi':f['roi']})
     self.append('results.jsonl',result)
     if result['retired']:self.counts['cancelled']+=1;continue
     self.records.append(result);self.counts['completed']+=1;self.lines[line]['completed']+=1;self.lines[line]['last_completed']=time.time();self.lines[line]['latency_ms']=result['end_to_end_ms'];self.latencies.append(result['end_to_end_ms']);self.timing_samples.append(result)
     if result['end_to_end_ms']>2000:self.counts['missed_deadlines']+=1
     if result['decision'] not in ['aligned','within_range']:self.reviews.append(copy.deepcopy(result))
   with self.condition:
    self.running.pop(line,None);self.running_since.pop(line,None)
    if line not in self.jobs:self.busy.discard(line)
 def switch(self,device):
  if device not in self.backends:raise ValueError(self.gpu_status if device=='gpu' else 'CPU unavailable')
  with self.lock:self.selected=device
  return {'selected_device':device,'effective':'next complete three-view batch','actual_device':self.actual}
 def heartbeat(self,native):
  if not isinstance(native,dict) or len(json.dumps(native))>60000:raise ValueError('Invalid native heartbeat')
  with self.lock:
   self.native=native;self.native_wall=time.monotonic()
   for timing in combined_timings(self.records,native.get('capture_timings',[])):
    if timing['frame_id'] in self.joined_set:continue
    if len(self.joined_ids)==self.joined_ids.maxlen:self.joined_set.discard(self.joined_ids[0])
    self.joined_ids.append(timing['frame_id']);self.joined_set.add(timing['frame_id']);self.trigger_latencies.append(timing['trigger_to_result_ms'])
  return {'stop_reason':self.stop_reason}
 def monitor_loop(self):
  while True:
   try:
    sample_start=time.perf_counter();metrics=self.monitor.sample();now=time.monotonic();metrics['native_cpu_percent']=-1;metrics['native_rss_mb']=-1;metrics['cpu_temperature_c']=-1
    pid=self.native.get('pid',0)
    if isinstance(pid,int) and pid>0:
     proc=Path('/proc')/str(pid)
     command=(proc/'cmdline').read_bytes()
     if b'--stage4' in command and b'FactoryGalaxy.x86_64' in command:
      fields=(proc/'stat').read_text().rsplit(')',1)[1].split();ticks=int(fields[11])+int(fields[12]);metrics['native_rss_mb']=int(fields[21])*os.sysconf('SC_PAGE_SIZE')/1e6
      if self.native_previous and self.native_previous[0]==pid:metrics['native_cpu_percent']=100*(ticks-self.native_previous[2])/os.sysconf('SC_CLK_TCK')/(now-self.native_previous[1])
      self.native_previous=(pid,now,ticks)
    for root in Path('/sys/class/hwmon').glob('hwmon*'):
     try:
      if (root/'name').read_text().strip()=='k10temp':metrics['cpu_temperature_c']=float((root/'temp1_input').read_text())/1000
     except OSError:pass
    metrics['monitor_total_ms']=(time.perf_counter()-sample_start)*1000;self.metrics=metrics
    if self.native.get('benchmark',False):
     conditions={'memory':metrics['available_memory_gb']<self.cfg['minimum_available_gib'],'GPU temperature':metrics['temperature_c']>=self.cfg['maximum_temperature_c'],'CPU temperature':metrics['cpu_temperature_c']>=self.cfg['maximum_cpu_temperature_c'],'unresponsive':self.native_wall and now-self.native_wall>self.cfg['native_stall_seconds']}
     for name,bad in conditions.items():
      if bad:self.guard_since.setdefault(name,now)
      else:self.guard_since.pop(name,None)
      if bad and (name in ['memory','unresponsive'] or now-self.guard_since[name]>=self.cfg['sustained_guard_seconds']):self.stop_reason='Resource guard: '+name
   except Exception as e:self.append('errors.jsonl',{'utc':utc(),'monitor_error':str(e)})
   time.sleep(1)
 def view(self,line=''):
  with self.lock:
   elapsed=max(.001,time.monotonic()-self.started);current=[r for r in self.records if self.active.get(r['line_id'])==r['session_id']];matching=[r for r in current if r['line_id']==line];batch=matching[-1]['batch_id'] if matching else '';results=copy.deepcopy([r for r in matching if r['batch_id']==batch]);events=copy.deepcopy([r for r in self.reviews if r['line_id']==line][-36:])
   for r in results+events:r['age_seconds']=max(0,time.time()-datetime.fromisoformat(r['capture_utc']).timestamp());r['historical']=self.active.get(r['line_id'])!=r['session_id'] or r['age_seconds']>3 or self.native.get('paused',False)
   perline=[dict(v,inspection_rate=v['completed']/elapsed) for k,v in self.lines.items() if k in self.active];lat=percentiles(list(self.latencies));trigger=percentiles(list(self.trigger_latencies));oldest=max([0]+[time.time()-v[3] for v in self.jobs.values()]+[max(0,time.time()-stamp) for stamp in self.running_since.values()])
   return {'contract':'gts.multi-state/1','ready':self.ready,'selected_device':self.selected,'actual_device':self.actual,'gpu_status':self.gpu_status,'status':('unavailable' if self.actual=='unavailable' else 'processing' if self.running else 'idle / ready'),'active_lines':len(self.active),'active_views':len(self.active)*3 if self.native.get('inspection',True) else 0,'queue_depth':len(self.jobs),'oldest_request_age_seconds':oldest,'worst_line_latency_ms':max([0]+[v['latency_ms'] for v in perline]),'end_to_end_p50_ms':lat['p50'],'end_to_end_p95_ms':lat['p95'],'end_to_end_p99_ms':lat['p99'],'trigger_to_result_p50_ms':trigger['p50'],'trigger_to_result_p95_ms':trigger['p95'],'trigger_to_result_p99_ms':trigger['p99'],'trigger_timing_samples':len(self.trigger_latencies),'elapsed_seconds':elapsed,'offered_rate':self.counts['offered']/elapsed,'accepted_rate':self.counts['accepted']/elapsed,'inspection_rate':self.counts['completed']/elapsed,'bottle_batches_rate':self.counts['completed']/3/elapsed,'lines':perline,'counts':dict(self.counts),'results':results,'events':list(reversed(events)),'native':self.native,'stop_reason':self.stop_reason,'assistant_state':self.assistant_state,'assistant_text':self.assistant_text,'assistant_event_id':self.assistant_event_id,'explanation_calls':self.calls,**dict(self.counts),**self.metrics}
 def explain(self,frame_id):
  with self.lock:
   if self.native.get('benchmark',False):raise ValueError('Qwen disabled during capacity testing')
   if self.pending_explanation:raise ValueError('Explanation already running')
   # Preserve the original global Stage3 budget, never create a fresh Stage4 budget.
   self.calls=len(self.ledger.read_text().splitlines()) if self.ledger.exists() else 0
   if self.calls>=self.cfg['explanation_budget']:raise ValueError('Preserved six-request budget exhausted')
   record=next((copy.deepcopy(r) for r in list(self.records)+list(self.reviews) if r['frame_id']==frame_id),None)
   if not record:raise ValueError('Recorded event missing')
   self.pending_explanation=True;self.assistant_state='processing';self.assistant_event_id=frame_id
  def run():
   import fcntl
   request=explain_request(record,self.cfg['assistant_model']);payload=ollama_payload(request);error='';text='';reply=None;number=0
   self.ledger.parent.mkdir(parents=True,exist_ok=True)
   with self.ledger.open('a+') as file:
    fcntl.flock(file,fcntl.LOCK_EX);file.seek(0);used=len(file.readlines())
    if used>=self.cfg['explanation_budget']:error='Preserved budget exhausted; no request sent'
    else:
     number=used+1;file.seek(0,2);file.write(json.dumps({'number':number,'started_utc':utc(),'stage':'stage4','frame_id':frame_id,'request':payload})+'\n');file.flush();os.fsync(file.fileno());self.calls=number
    fcntl.flock(file,fcntl.LOCK_UN)
   if not error:
    try:
     adapter=OllamaAdapter(self.cfg['ollama_endpoint'],self.cfg['assistant_timeout_seconds']);reply=adapter.execute(request);v=validate_explanation(reply,record);text='LOCAL QWEN DRAFT: '+v['explanation']+' '+v['uncertainty']+' Next check: '+v['next_check']
    except Exception as e:error=str(e)
    self.append('explanations.jsonl',{'number':number,'completed_utc':utc(),'frame_id':frame_id,'raw_response':reply.raw if reply else {},'wall_seconds':reply.wall_seconds if reply else 0,'validation_error':error,'validation':'fail' if error else 'pass'})
   with self.lock:self.assistant_state='failed / deterministic wording' if error else 'complete';self.assistant_text=('APPLICATION FACTUAL FALLBACK: '+record['wording']+'. '+record['reason']+' Visual appearance only. Local explanation failed: '+error) if error else text;self.pending_explanation=False
  threading.Thread(target=run,daemon=True).start();return {'accepted':True}

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,status,value):
  raw=json.dumps(value,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_GET(self):
  path=urlsplit(self.path);query=parse_qs(path.query);e=self.server.engine
  if path.path=='/health':self.send(200,{'contract':'gts.multi-state/1','ready':e.ready,'backends':list(e.backends)});return
  if path.path=='/state':self.send(200,e.view(query.get('line_id',[''])[0]));return
  if path.path.startswith('/crop/'):
   fid=path.path[6:]
   if re.fullmatch('[a-f0-9]{32}',fid):
    p=e.root/'crops'/(fid+'.png')
    if p.exists():
     raw=p.read_bytes();self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
  self.send(404,{'error':'Unavailable / expired evidence'})
 def do_POST(self):
  try:
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<=2_000_000:raise ValueError('Bounded2MB request required')
   value=json.loads(self.rfile.read(length));e=self.server.engine
   if self.path=='/registry':result=e.register(value['lines'])
   elif self.path=='/batch':result=e.submit(value)
   elif self.path=='/device':result=e.switch(value['device'])
   elif self.path=='/native':result=e.heartbeat(value)
   elif self.path=='/explain':result=e.explain(value['frame_id'])
   elif self.path=='/stop':e.stop_reason='Operator Stop benchmark';result={'stopping':True}
   else:self.send(404,{'error':'Unsupported operation'});return
   self.send(200,result)
  except (ValueError,KeyError,TypeError) as error:self.send(400,{'error':str(error)})

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--config',default='stage4/config.local.json');args=parser.parse_args();cfg=json.loads(Path(args.config).read_text())
 if cfg['host']!='127.0.0.1':raise SystemExit('Loopback only')
 server=ThreadingHTTPServer((cfg['host'],cfg['port']),Handler);server.daemon_threads=True;server.engine=Engine(cfg);server.serve_forever()
if __name__=='__main__':main()
