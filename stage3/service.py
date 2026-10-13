"""Loopback bounded image-only work queue; no diagnostic/control execution."""
import base64,copy,hashlib,json,queue,threading,time,uuid,re
from datetime import datetime,timezone
from pathlib import Path
from io import BytesIO
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit,parse_qs
from PIL import Image
from stage3.backend import NeuralBackend,STATIONS,WORDS,LABELS
from stage3.monitor import Monitor
from factory.model import OllamaAdapter,ModelRequest,ASSIST_SCHEMA,ollama_payload,validate_response

def utc():return datetime.now(timezone.utc).isoformat()
def validate_batch(value):
 required={'contract','line_id','session_id','bottle_id','batch_id','capture_utc','source_time','target_count','observations_available','frames','product'}
 if not isinstance(value,dict) or set(value)!=required or value['contract']!='gts.three-frame/1':raise ValueError('Unsupported batch schema / extra metadata')
 for key in ['line_id','session_id','bottle_id','batch_id']:
  if not isinstance(value[key],str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',value[key]):raise ValueError('Invalid identity')
 if type(value['observations_available'])!=bool or type(value['target_count'])!=int:raise ValueError('Invalid association quality')
 if value['product'] not in ['LAGER','IPA','STOUT']:raise ValueError('Unknown product')
 if not isinstance(value['source_time'],(float,int)):raise ValueError('Invalid process time')
 when=datetime.fromisoformat(value['capture_utc']);
 if when.tzinfo is None:raise ValueError('Capture timestamp needs timezone')
 if len(value['frames'])!=3 or {f['station_id'] for f in value['frames']}!=set(STATIONS):raise ValueError('Three distinct station views required')
 if len({f['frame_id'] for f in value['frames']})!=3:raise ValueError('Distinct frame IDs required')
 images=[]
 for f in value['frames']:
  if set(f)!={'station_id','frame_id','image','roi'} or not re.fullmatch('[a-f0-9]{32}',f['frame_id']):raise ValueError('Invalid frame schema/identity')
  raw=base64.b64decode(f['image'],validate=True)
  if len(raw)>500_000:raise ValueError('Image too large')
  image=Image.open(BytesIO(raw));
  if image.size!=(256,256) or image.format!='PNG' or not isinstance(f['roi'],list) or len(f['roi'])!=4 or any(type(v)!=int for v in f['roi']) or f['roi'][2:]!=[160,160] or not(0<=f['roi'][0]<=96 and 0<=f['roi'][1]<=96):raise ValueError('Frozen frame/ROI dimensions required')
  image.load();images.append((f,raw,image.convert('RGB').crop((f['roi'][0],f['roi'][1],f['roi'][0]+160,f['roi'][1]+160))))
 return when.timestamp(),images

def explain_request(record,model):
 facts={k:record[k] for k in ['frame_id','station_id','capture_utc','completed_utc','decision','wording','reason','device','backend','score']};facts['score_scope']='uncalibrated; not evidence of correctness';facts['source']='recorded synthetic camera assessment, simulator-assisted association'
 proc=json.loads(Path('stage3/procedures.json').read_text())
 return ModelRequest('assistant',model,[{'role':'system','content':Path('stage3/EXPLANATION_PROMPT.txt').read_text()},{'role':'user','content':json.dumps({'recorded_event':facts,'demo_procedures':proc})}],ASSIST_SCHEMA)
def validate_explanation(response,record):
 v=validate_response('assistant',response,[record['frame_id']],['S3-DEMO-1'])
 if v['evidence_ids']!=[record['frame_id']] or v['procedure_ids']!=['S3-DEMO-1']:raise ValueError('Required exact references missing')
 joined=' '.join(v[k] for k in ['explanation','next_check','uncertainty'])
 if len(joined)>900 or re.search(r"\b\d+(?:\.\d+)?\s*m[lL]\b|\bmL\b",joined) or re.search(r'\b(torque|seal\w*|leak.tight|secure\w*|attach\w*|millilit\w*|readab\w*|volume|root cause|hours|days)\b',joined,re.I):raise ValueError('Unsupported scope or length')
 return v
class Engine:
 def __init__(self,cfg,adapter=None):
  self.cfg=cfg;self.root=Path(cfg['data_path']);self.root.mkdir(parents=True,exist_ok=True);(self.root/'frames').mkdir(exist_ok=True);(self.root/'crops').mkdir(exist_ok=True);self.jobs=queue.Queue(cfg['queue_capacity']);self.lock=threading.RLock();self.selected=cfg['device'];self.actual='unavailable';self.gpu_status='Not yet probed';self.ready=threading.Event();self.records=[];self.reviews=[];self.ids=set();self.session='';self.started=time.monotonic();self.queued=self.completed=self.dropped=self.stale=self.missed=0;self.monitor=Monitor();self.metrics={};self.pending_explanation=False;self.assistant_state='idle';self.assistant_text='No explanation requested';self.assistant_event_id='';self.adapter=adapter or OllamaAdapter(cfg['ollama_endpoint'],cfg['assistant_timeout_seconds']);self.ledger=self.root/'stage3-qwen-ledger.jsonl';self.calls=sum(1 for l in self.ledger.read_text().splitlines()) if self.ledger.exists() else 0
  self.quality_summary='Synthetic quality evaluation not yet available'
  p=Path('reports/stage3/quality-summary.txt')
  if p.exists():self.quality_summary=p.read_text().strip()
  if (self.root/'results.jsonl').exists():
   history=[json.loads(l) for l in (self.root/'results.jsonl').read_text().splitlines()];self.records=history[-200:];self.reviews=[r for r in history if r['decision'] not in ['aligned','within_range']][-60:];self.ids={r['batch_id'] for r in self.records}
  threading.Thread(target=self.worker,daemon=True).start()
  if cfg.get('monitoring',True):threading.Thread(target=self.monitor_loop,daemon=True).start()
 def append(self,name,value):
  with (self.root/name).open('a') as f:f.write(json.dumps(value)+'\n')
 def monitor_loop(self):
  while True:
   try:self.metrics=self.monitor.sample()
   except Exception:self.metrics={}
   time.sleep(1)
 def submit(self,value):
  when,images=validate_batch(value)
  with self.lock:
   if value['line_id']!=self.cfg.get('line_id','Line01'):raise ValueError('Unsupported line instance')
   if value['batch_id'] in self.ids:raise ValueError('Duplicate batch')
   if any((self.root/'frames'/(f['frame_id']+'.png')).exists() for f in value['frames']):raise ValueError('Frame identity already recorded')
   if self.jobs.full():self.dropped+=3;raise ValueError('Inspection queue full')
   self.ids.add(value['batch_id']);self.queued+=3;self.jobs.put_nowait((copy.deepcopy(value),when,images,time.time()));return {'accepted':True,'batch_id':value['batch_id']}
 def worker(self):
  self.backends={};cold={}
  try:
   self.backends['cpu']=NeuralBackend(self.cfg['model_path'],'cpu');cold['cpu_ms']=self.backends['cpu'].cold_start_ms
   try:
    self.backends['gpu']=NeuralBackend(self.cfg['model_path'],'gpu');cold['gpu_ms']=self.backends['gpu'].cold_start_ms;self.gpu_status='Verified AMD OpenGL compute: '+self.backends['gpu'].renderer
   except Exception as e:self.gpu_status='GPU unavailable: '+str(e)
   self.actual=self.selected if self.selected in self.backends else 'unavailable';self.append('cold-start.jsonl',cold)
  except Exception as e:self.gpu_status='Model unavailable: '+str(e)
  self.ready.set()
  while True:
   value,when,images,queued=self.jobs.get();self.actual=self.selected if self.selected in self.backends else 'unavailable';backend=self.backends.get(self.actual)
   for f,raw,image in images:
    began=time.time();age=began-when;self.append('requests.jsonl',{k:v for k,v in value.items() if k!='frames'}|{'station_id':f['station_id'],'frame_id':f['frame_id'],'image_sha256':hashlib.sha256(raw).hexdigest()})
    (self.root/'frames'/(f['frame_id']+'.png')).write_bytes(raw);image.save(self.root/'crops'/(f['frame_id']+'.png'))
    reason=''
    if value['target_count']!=1 or not value['observations_available']:reason='Ambiguous association or missing observations'
    elif age<-.1 or age>self.cfg['max_age_seconds']:reason='Stale capture; current inspection withheld';self.stale+=1
    elif backend is None:reason='Requested inference device unavailable; no silent CPU fallback'
    try:
     result=backend.predict(f['station_id'],image) if not reason else {}
    except Exception as e:reason='Inference failed: '+str(e);result={}
    if reason:result.update(decision='uncertain',wording=WORDS[f['station_id']][3],reason=reason,score=0,device=self.actual,backend='Unavailable / withheld',model_sha256='',preprocess_ms=0,transfer_ms=0,inference_ms=0,gpu_elapsed_ms=0)
    result.update({k:value[k] for k in ['line_id','session_id','bottle_id','batch_id','capture_utc','source_time','product']});result.update(station_id=f['station_id'],frame_id=f['frame_id'],completed_utc=utc(),queue_ms=(began-queued)*1000,end_to_end_ms=(time.time()-when)*1000,crop_url='/crop/'+f['frame_id'])
    if result['end_to_end_ms']>2000:self.missed+=1
    with self.lock:self.completed+=1;self.records.append(result);self.records=self.records[-200:];self.append('results.jsonl',result)
    if result['decision'] not in ['aligned','within_range']:
     with self.lock:self.reviews.append(copy.deepcopy(result));self.reviews=self.reviews[-60:]
   self.jobs.task_done()
   self.prune_files()
 def prune_files(self):
  # Keep bounded image history; persistent structured audit remains on disk.
  for directory in ['frames','crops']:
   paths=sorted((self.root/directory).glob('*.png'),key=lambda p:p.stat().st_mtime)
   protected={r['frame_id'] for r in self.reviews};unprotected=[p for p in paths if p.stem not in protected]
   for p in unprotected[:max(0,len(paths)-600)]:p.unlink(missing_ok=True)
 def view(self,session=''):
  with self.lock:
   recent=copy.deepcopy(self.records[-60:]);events=list({r['frame_id']:r for r in recent+copy.deepcopy(self.reviews)}.values());events.sort(key=lambda r:r['capture_utc']);results=[];matching=[r for r in recent if r['session_id']==session]
   batch=matching[-1]['batch_id'] if matching else ''
   for r in events:r['age_seconds']=max(0,time.time()-datetime.fromisoformat(r['capture_utc']).timestamp());r['historical']=r['session_id']!=session or r['age_seconds']>3
   results=[r for r in events if r['batch_id']==batch]
   return {'selected_device':self.selected,'actual_device':self.actual,'gpu_status':self.gpu_status,'status':('processing' if self.jobs.unfinished_tasks else 'idle / ready') if self.ready.is_set() and self.actual!='unavailable' else 'unavailable','results':results,'events':list(reversed(events)),'queued':self.queued,'completed':self.completed,'dropped':self.dropped,'stale':self.stale,'missed_deadlines':self.missed,'queue_depth':self.jobs.qsize(),'elapsed_seconds':time.monotonic()-self.started,'inspection_rate':self.completed/max(.001,time.monotonic()-self.started),'assistant_state':self.assistant_state,'assistant_text':self.assistant_text,'assistant_event_id':self.assistant_event_id,'explanation_calls':self.calls,'quality_summary':self.quality_summary,**self.metrics}
 def switch(self,device):
  if device not in ['cpu','gpu']:raise ValueError('CPU/GPU only')
  if device not in self.backends:raise ValueError(self.gpu_status if device=='gpu' else 'CPU model unavailable')
  self.selected=device
  # The running batch retains its backend; the next batch applies this choice.
  if self.jobs.unfinished_tasks==0:self.actual=device
 def explain(self,id):
  with self.lock:
   matches=[r for r in self.records+self.reviews if r['frame_id']==id]
   if not matches:raise ValueError('Unknown recorded event')
   if self.pending_explanation:raise ValueError('One explanation already pending')
   if self.calls>=self.cfg['explanation_budget']:raise ValueError('Persistent Stage3 six-call budget exhausted')
   record=copy.deepcopy(matches[0]);request=explain_request(record,self.cfg['assistant_model']);self.calls+=1;number=self.calls;self.pending_explanation=True;self.assistant_state='processing';self.assistant_event_id=id
   # Reserve the request in the durable ledger before executing, including failures.
   self.append('stage3-qwen-ledger.jsonl',{'number':number,'started_utc':utc(),'frame_id':id,'request':ollama_payload(request)})
  def run():
   response=self.adapter.execute(request);valid=False
   try:
    v=validate_explanation(response,record);text='LOCAL QWEN DRAFT: '+v['explanation']+' '+v['uncertainty']+' Next: '+v['next_check'];valid=True
   except Exception as e:text='APPLICATION FACTUAL FALLBACK: '+record['wording']+'. '+record['reason']+' Review the recorded synthetic crop; physical properties and cause remain unproven.';error=str(e)
   self.append('explanations.jsonl',{'number':number,'completed_utc':utc(),'frame_id':id,'raw_response':response.raw,'wall_seconds':response.wall_seconds,'error':response.error,'validation':'pass' if valid else 'fail','validation_error':'' if valid else error,'displayed_text':text})
   with self.lock:self.assistant_text=text;self.assistant_state='complete' if valid else 'failed / factual fallback';self.pending_explanation=False
  threading.Thread(target=run,daemon=True).start()

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--config',default='stage3/config.example.json');a=p.parse_args();cfg=json.loads(Path(a.config).read_text())
 if cfg['host']!='127.0.0.1' or urlsplit(cfg['ollama_endpoint']).hostname not in ['127.0.0.1','localhost']:raise SystemExit('Local service and Ollama endpoints only')
 engine=Engine(cfg);engine.ready.wait(20)
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def reply(self,value,status=200):
   data=json.dumps(value).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  def do_GET(self):
   path=urlsplit(self.path)
   if path.path=='/health':self.reply({'contract':'gts.three-frame/1','ready':engine.ready.is_set(),'actual':engine.actual})
   elif path.path=='/state':self.reply(engine.view(parse_qs(path.query).get('session_id',[''])[0]))
   elif re.fullmatch('/crop/[a-f0-9]{32}',path.path):
    p=engine.root/'crops'/(path.path.split('/')[-1]+'.png')
    if not p.exists():self.reply({'error':'Evidence image expired/unavailable'},404);return
    data=p.read_bytes();self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
   else:self.reply({'error':'Unsupported path'},404)
  def do_POST(self):
   try:
    length=int(self.headers.get('Content-Length','0'))
    if not 0<length<=2_000_000:raise ValueError('Bounded JSON body required')
    value=json.loads(self.rfile.read(length))
    if self.path=='/batch':reply=engine.submit(value)
    elif self.path=='/device':engine.switch(value['device']);reply={'selected':engine.selected,'applies':'between batches'}
    elif self.path=='/session':engine.session=value['session_id'];reply={'session':engine.session,'history':'retained'}
    elif self.path=='/explain':engine.explain(value['frame_id']);reply={'queued':True,'frame_id':value['frame_id']}
    else:raise ValueError('Unsupported operation')
    self.reply(reply)
   except Exception as e:self.reply({'error':str(e)},400)
 ThreadingHTTPServer((cfg['host'],cfg['port']),Handler).serve_forever()
if __name__=='__main__':main()
