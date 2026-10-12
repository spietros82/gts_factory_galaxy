"""Loopback focused inspection and bounded local explanations; no control endpoints."""
import argparse,base64,datetime,hashlib,json,queue,re,threading,time
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from io import BytesIO
from dataclasses import asdict
from PIL import Image
from .backend import LearnedBackend,ClassicalBackend,DecisionPolicy,localize,WORDING
from factory.model import ModelRequest,OllamaAdapter,ASSIST_SCHEMA,validate_response,ollama_payload
ROOT=Path(__file__).resolve().parent.parent

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def validate_input(body):
 allowed={'contract','frame_id','capture_utc','target_id','session','association','target_count','observations_available','roi','image'}
 if not isinstance(body,dict) or set(body)!=allowed:raise ValueError('Exact focused-frame schema required; hidden truth/unsupported metadata rejected')
 if body['contract']!='gts.focused-frame/1':raise ValueError('Unsupported contract')
 for key in ['frame_id','target_id','session']:
  if not isinstance(body[key],str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,90}',body[key]):raise ValueError('Bounded neutral identifiers required')
 if type(body['target_count'])!=int or type(body['observations_available'])!=bool:raise ValueError('Invalid association fields')
 capture=datetime.datetime.fromisoformat(body['capture_utc'])
 if capture.tzinfo is None:raise ValueError('Timezone required')
 pixels=base64.b64decode(body['image'],validate=True)
 if len(pixels)>1500000 or not pixels.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Bounded PNG required')
 with Image.open(BytesIO(pixels)) as original:
  if original.size!=(512,384):raise ValueError('Fixed inspection frame size required')
  frame=original.convert('RGB')
 crop=localize(frame,body['roi'])
 return pixels,crop,{k:v for k,v in body.items() if k!='image'}|{'capture_epoch':capture.timestamp()}

class State:
 def __init__(self,cfg,backend=None,adapter=None):
  self.cfg=cfg;policy=json.loads((ROOT/cfg['policy_path']).read_text());self.policy=DecisionPolicy(policy)
  self.backend=backend or (LearnedBackend(ROOT/cfg['model_path'],policy) if cfg['backend']=='learned-rf' else ClassicalBackend(policy))
  self.data=ROOT/cfg['data_path'];(self.data/'frames').mkdir(parents=True,exist_ok=True);(self.data/'crops').mkdir(exist_ok=True)
  self.lock=threading.RLock();self.jobs=queue.Queue(cfg['queue_capacity']);self.explanations=queue.Queue(1);self.adapter=adapter or OllamaAdapter(cfg['ollama_endpoint'],cfg['timeout_seconds'])
  self.started=time.monotonic();self.session='';self.generation=0;self.seen=set();self.result=None;self.running=False
  self.counts={k:0 for k in ['captured','queued','inspected','uncertain','dropped','stale','explanation_calls']};self.explaining=False;self.assistant_text='No explanation requested';self.assistant_state='idle';self.assistant_evidence={};self.assistant_wall=0;self.records=[]
  evalpath=ROOT/'reports/inspection/locked-evaluation.json';self.eval=json.loads(evalpath.read_text()) if evalpath.exists() else None
  self.evaluation_summary='Synthetic evaluation unavailable; experimental' if not self.eval else 'Synthetic test: '+('demo targets passed' if self.eval['runs']['learned']['metrics']['all_targets_pass'] else 'TARGETS FAILED — experimental; do not rely on inspection')+'; physical validation absent'
  self.procedures=json.loads((ROOT/'inspection/procedures.json').read_text());self.prompt=(ROOT/'inspection/EXPLANATION_PROMPT.txt').read_text()
  threading.Thread(target=self.worker,daemon=True).start();threading.Thread(target=self.language_worker,daemon=True).start()
 def append(self,name,record):
  with self.lock:
   with (self.data/name).open('a') as f:f.write(json.dumps(record)+'\n')
 def submit(self,body):
  pixels,crop,meta=validate_input(body)
  with self.lock:
   if meta['frame_id'] in self.seen:return {'state':'duplicate ignored'}
   if self.session!=meta['session']:self.session=meta['session'];self.generation+=1;self.result=None;self.assistant_text='New replay; previous explanations withheld';self.assistant_state='idle';self.assistant_evidence={};self.assistant_wall=0
   self.seen.add(meta['frame_id']);self.counts['captured']+=1
   (self.data/'frames'/(meta['frame_id']+'.png')).write_bytes(pixels);crop.save(self.data/'crops'/(meta['frame_id']+'.png'))
   record={'input':meta,'image_sha256':hashlib.sha256(pixels).hexdigest(),'crop_sha256':hashlib.sha256((self.data/'crops'/(meta['frame_id']+'.png')).read_bytes()).hexdigest(),'received_utc':utc()}
   self.append('frames.jsonl',record)
   try:self.jobs.put_nowait({'meta':meta,'crop':crop,'queued':time.monotonic(),'generation':self.generation})
   except queue.Full:self.counts['dropped']+=1;self.append('drops.jsonl',{'frame_id':meta['frame_id'],'reason':'bounded queue full'});return {'state':'dropped'}
   self.counts['queued']+=1;return {'state':'queued'}
 def worker(self):
  while True:
   job=self.jobs.get();start=time.monotonic()
   with self.lock:self.running=True
   meta=job['meta']
   try:
    assessment=self.policy.decide(self.backend,job['crop'],meta,time.time())
    result={k:meta[k] for k in ['frame_id','capture_utc','target_id','association']}|{'decision':assessment.label,'wording':WORDING[assessment.label],'score':assessment.score,'reason':assessment.reason,'backend':assessment.backend,'completed_utc':utc(),'latency_seconds':time.time()-meta['capture_epoch'],'queue_seconds':start-job['queued'],'classifier_seconds':time.monotonic()-start,'status':'complete','crop_url':'/crop/'+meta['frame_id']}
   except Exception as error:
    result={k:meta[k] for k in ['frame_id','capture_utc','target_id','association']}|{'decision':'uncertain','wording':WORDING['uncertain'],'score':0,'reason':'Inspection failure: '+str(error),'backend':getattr(self.backend,'name','unavailable'),'completed_utc':utc(),'latency_seconds':time.time()-meta['capture_epoch'],'queue_seconds':start-job['queued'],'classifier_seconds':time.monotonic()-start,'status':'failed'}
   with self.lock:
    self.counts['inspected']+=1
    if result['decision']=='uncertain':self.counts['uncertain']+=1
    if result['latency_seconds']>self.cfg['maximum_capture_age_seconds']:self.counts['stale']+=1
    old=job['generation']!=self.generation
    if not old:self.result=result
    self.records.append(result);self.append('inspections.jsonl',result|{'old_session':old,'session':meta['session']});self.running=False
   self.jobs.task_done()
 def fallback(self,result):
  if not result:return 'APPLICATION FACTUAL FALLBACK — Insufficient evidence; capture a fresh single-target image.'
  return 'APPLICATION FACTUAL FALLBACK — '+result['wording']+'. '+result['reason']+'. Experimental synthetic result; review target crop and reacquire if unclear. Evidence '+result['frame_id']+' captured '+result['capture_utc']+'. Visual evidence alone does not confirm physical attachment properties. Demo procedure IP-CHECK-1.'
 def explain(self):
  with self.lock:
   if self.explaining or not self.explanations.empty():raise ValueError('One explanation pending; no duplicate request')
   if self.counts['explanation_calls']>=self.cfg['explanation_budget']:raise ValueError('Explicit six-call budget exhausted')
   if not self.result or time.time()-datetime.datetime.fromisoformat(self.result['capture_utc']).timestamp()>2:
    self.assistant_state='fallback';self.assistant_text=self.fallback(None);return {'state':'fallback','reason':'No fresh inspection evidence; no model call'}
   result=dict(self.result);evidence={'inspection':result,'evaluation':self.evaluation_summary,'scope':'visual presence/placement only; synthetic, experimental','procedures':self.procedures}
   req=ModelRequest('assistant',self.cfg['assistant_model'],[{'role':'system','content':self.prompt},{'role':'user','content':json.dumps(evidence)}],ASSIST_SCHEMA)
   self.counts['explanation_calls']+=1;self.assistant_state='queued';self.assistant_text='Local explanation requested; inspection decision remains authoritative';self.explanations.put_nowait({'request':req,'result':result,'generation':self.generation,'number':self.counts['explanation_calls']})
   return {'state':'queued'}
 def language_worker(self):
  while True:
   job=self.explanations.get()
   with self.lock:self.explaining=True;self.assistant_state='running'
   start=utc();req=job['request'];response=self.adapter.execute(req)
   record={'number':job['number'],'started_utc':start,'completed_utc':utc(),'request':ollama_payload(req),'raw_response':response.raw,'wall_seconds':response.wall_seconds,'backend':response.backend,'error':response.error,'evidence':job['result']}
   try:
    validated=validate_response('assistant',response,[job['result']['frame_id']],[p['id'] for p in self.procedures]);joined=' '.join(validated[k] for k in ['explanation','next_check','uncertainty'])
    # Conservative output safety gate: even quoted/negated forbidden wording is withheld.
    if re.search(r'\b(torqu\w*|seal\w*|leak\w*|secure\w*|attach\w*|fasten\w*|tight\w*|firm\w*|guarantee\w*|safe(?:ty)?|failure (?:time|deadline))\b',joined,re.I):raise ValueError('Outside visual scope wording withheld; raw reply preserved')
    if not validated['evidence_ids'] or not validated['procedure_ids']:raise ValueError('Missing evidence/procedure citation')
    rendered='LOCAL MODEL DRAFT / experimental — '+validated['explanation']+'\nNext check: '+validated['next_check']+'\nUncertainty: '+validated['uncertainty']+'\nEvidence: '+', '.join(validated['evidence_ids'])+'; '+', '.join(validated['procedure_ids'])
    record['validation']='schema/references/scope-wording only; factual review required';state='complete'
   except Exception as e:
    record['validation']='failed';record['validation_error']=str(e);rendered=self.fallback(job['result'])+'\nLocal model rejected/unavailable: '+str(e);state='fallback'
   with self.lock:
    old=job['generation']!=self.generation;record['old_session']=old
    if not old:self.assistant_text=rendered;self.assistant_state=state;self.assistant_evidence=job['result'];self.assistant_wall=response.wall_seconds
    self.append('explanations.jsonl',record);self.explaining=False
   self.explanations.task_done()
 def snapshot(self):
  with self.lock:
   elapsed=time.monotonic()-self.started;result=dict(self.result) if self.result else None
   if result and time.time()-datetime.datetime.fromisoformat(result['capture_utc']).timestamp()>2:result['status']='historical-stale'
   return self.counts|{'session':self.session,'state':'running' if self.running else 'idle','backend':getattr(self.backend,'name','unavailable'),'result':result,'queue_depth':self.jobs.qsize(),'elapsed_seconds':elapsed,'inspection_rate':self.counts['inspected']/max(elapsed,.001),'evaluation_summary':self.evaluation_summary,'assistant_state':self.assistant_state,'assistant_text':self.assistant_text,'assistant_capture_utc':self.assistant_evidence.get('capture_utc',''),'assistant_frame_id':self.assistant_evidence.get('frame_id',''),'assistant_target_id':self.assistant_evidence.get('target_id',''),'assistant_wall_seconds':self.assistant_wall,'assistant_age_seconds':max(0,time.time()-datetime.datetime.fromisoformat(self.assistant_evidence['capture_utc']).timestamp()) if self.assistant_evidence else 0}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--config',default='inspection/config.local.json');args=parser.parse_args();cfg=json.loads((ROOT/args.config).read_text())
 if cfg['host']!='127.0.0.1':raise ValueError('Loopback required')
 state=State(cfg)
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def reply(self,value,status=200):
   data=json.dumps(value).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  def do_GET(self):
   if self.path=='/state':self.reply(state.snapshot())
   elif self.path=='/health':self.reply({'state':'ready','backend':state.backend.name,'contract':'gts.focused-frame/1'})
   elif self.path.startswith('/crop/'):
    ident=self.path.split('/')[-1]
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,90}',ident):return self.reply({'error':'Invalid frame ID'},400)
    p=state.data/'crops'/(ident+'.png')
    if not p.exists():return self.reply({'error':'No recorded crop'},404)
    data=p.read_bytes();self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
   else:self.reply({'error':'Unsupported path'},404)
  def do_POST(self):
   if self.headers.get('Origin') or self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.reply({'error':'Native local JSON client required'},403)
   try:
    size=int(self.headers.get('Content-Length',0))
    if size<1 or size>2100000:raise ValueError('Bounded request required')
    body=json.loads(self.rfile.read(size))
    if self.path=='/frame':self.reply(state.submit(body),202)
    elif self.path=='/explain' and body=={}:self.reply(state.explain(),202)
    else:self.reply({'error':'Unsupported path/body'},404)
   except Exception as e:self.reply({'error':str(e)},400)
 ThreadingHTTPServer((cfg['host'],cfg['port']),Handler).serve_forever()
if __name__=='__main__':main()
