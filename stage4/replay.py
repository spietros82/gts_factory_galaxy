"""Bounded frozen-crop vision-only load: excludes rendering/acquisition/HTTP/storage."""
import json,queue,threading,time
from pathlib import Path
from PIL import Image
from stage3.backend import NeuralBackend
from stage4.bench import stats

def run_replay(out,device,rate,warm=2,measure=8):
 from stage4.monitoring import sample_host
 out=Path(out);out.mkdir(parents=True,exist_ok=False);source=Path('reports/stage4/integration/review.json');records=json.loads(source.read_text())['results'];batches=[]
 for product in ['LAGER','IPA','STOUT']:
  group=next(r['id'] for r in records if r['product']==product and r['expected']=='aligned' and r['station_id']=='cap')
  rows=[r for r in records if r['id']==group];batches.append([(r['station_id'],Image.open(Path('reports/stage4/integration/crops')/(r['frame_id']+'.png')).convert('RGB')) for r in rows])
 jobs=queue.Queue(48);ready=threading.Event();stop=threading.Event();results=[];errors=[];cold={};depth=[];samples=[]
 def worker():
  try:backend=NeuralBackend('stage3/models',device);cold.update(cold_start_ms=backend.cold_start_ms,backend=backend.backend,actual_device=backend.device,renderer=getattr(backend,'renderer','CPU NumPy'))
  except Exception as e:errors.append(str(e));ready.set();return
  ready.set()
  while not stop.is_set() or not jobs.empty():
   try:sequence,offered,scheduled=jobs.get(timeout=.05)
   except queue.Empty:continue
   begin=time.perf_counter();predictions=[backend.predict(station,image) for station,image in batches[sequence%3]];end=time.perf_counter();results.append({'sequence':sequence,'offered':offered,'scheduled':scheduled,'completed':end,'end_to_end_ms':(end-offered)*1000,'queue_ms':(begin-offered)*1000,'classifier_ms':sum(p['classifier_ms'] for p in predictions),'devices':[p['device'] for p in predictions],'decisions':[p['decision'] for p in predictions]});jobs.task_done()
 thread=threading.Thread(target=worker,daemon=True);thread.start();ready.wait(10)
 if errors:raise RuntimeError(errors[0])
 start=time.perf_counter();sequence=offered=dropped=0;next_sample=0
 while time.perf_counter()-start<warm+measure:
  scheduled=start+sequence/rate;now=time.perf_counter()
  if now<scheduled:time.sleep(min(.005,scheduled-now));continue
  offered+=1
  try:jobs.put_nowait((sequence,now,scheduled))
  except queue.Full:dropped+=1
  depth.append(jobs.qsize());sequence+=1
  if now>=next_sample:next_sample=now+1;samples.append(sample_host())
 stop.set();thread.join(3);steady=[r for r in results if start+warm<=r['completed']<start+warm+measure];accepted=offered-dropped;actual=len(steady)/measure;deadlines=sum(r['end_to_end_ms']>2000 for r in steady)
 summary={'mode':'vision-only saved-crop replay','device':device,'offered_batch_rate':rate,'actual_offered_batches_s':offered/(warm+measure),'accepted_batch_rate':accepted/(warm+measure),'completed_batches_s':actual,'completed_images_s':actual*3,'warmup_seconds':warm,'measure_seconds':measure,'drops':dropped,'deadlines':deadlines,'queue_max':max(depth,default=0),'queue_remaining':jobs.qsize(),'end_to_end_ms':stats([r['end_to_end_ms'] for r in steady]),'queue_ms':stats([r['queue_ms'] for r in steady]),'classifier_batch_ms':stats([r['classifier_ms'] for r in steady]),'cold':cold,'passed':not dropped and not deadlines and actual>=rate*.95 and not thread.is_alive(),'resources':samples,'scope':'nine newly captured crops, identical frozen weights; excludes live cameras, Unity, transport and evidence storage'}
 (out/'summary.json').write_text(json.dumps(summary,indent=2));(out/'results.json').write_text(json.dumps(results));print('replay',device,rate,'PASS'if summary['passed']else'FAIL',round(actual,2),'batches/s',flush=True);return summary
