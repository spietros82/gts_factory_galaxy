"""Frozen validation crops only. Bounded replay queue, no physical camera claim."""
import json,queue,threading,time
from pathlib import Path
from PIL import Image
from stage3.backend import NeuralBackend
from stage3.bench import stats
from stage3.monitor import Monitor
ROOT=Path('stage3/dataset');OUT=Path('reports/stage3/performance');rows=json.loads((ROOT/'validation.json').read_text());images={s:[Image.open(ROOT/'crops'/(r['id']+'.png')).convert('RGB') for r in rows if r['station']==s][:8] for s in ['cap','fill','label']}
def run(device,rate,monitor=False,duration=10):
 jobs=queue.Queue(2);done=[];dropped=0;ready=threading.Event();stop=threading.Event();metadata={};sampling=Monitor()
 def worker():
  b=NeuralBackend(device=device);metadata.update(cold_ms=b.cold_start_ms,renderer=getattr(b,'renderer',None))
  for s in images:b.predict(s,images[s][0])
  ready.set()
  while not stop.is_set() or not jobs.empty():
   try:i,queued=jobs.get(timeout=.1)
   except queue.Empty:continue
   results=[b.predict(s,images[s][i%8]) for s in images];elapsed=(time.perf_counter()-queued)*1000;done.append({'latency_ms':elapsed,'results':results});jobs.task_done()
 thread=threading.Thread(target=worker);thread.start();ready.wait(20);start=time.perf_counter();next_sample=start;index=0;queue_peak=0
 while time.perf_counter()-start<duration:
  due=start+index/rate
  if time.perf_counter()<due:time.sleep(min(.001,due-time.perf_counter()));continue
  try:jobs.put_nowait((index,time.perf_counter()));queue_peak=max(queue_peak,jobs.qsize())
  except queue.Full:dropped+=1;break
  index+=1
  if monitor and time.perf_counter()>=next_sample:sampling.sample();next_sample+=1
  if done and done[-1]['latency_ms']>2000:break
 stop.set();thread.join(10);wall=time.perf_counter()-start
 return {'device':device,'requested_batches_per_second':rate,'wall_seconds':wall,'submitted':index,'completed_batches':len(done),'completed_inspections':len(done)*3,'throughput_inspections_per_second':len(done)*3/wall,'queue_peak_batches':queue_peak,'dropped_batches':dropped,'deadline_misses':sum(r['latency_ms']>2000 for r in done),'latency_ms':stats([r['latency_ms'] for r in done]),'inference_ms':stats([r['inference_ms'] for batch in done for r in batch['results']]),'monitoring':monitor,'cold':metadata}
def main():
 results=[];start=time.monotonic()
 for device in ['cpu','gpu']:
  for rate in [2,10,50,100]:
   r=run(device,rate);results.append(r);print(device,rate,r['completed_batches'],r['dropped_batches'],flush=True)
   if r['dropped_batches'] or r['deadline_misses']:break
 # Monitoring overhead is a small replay comparison, not a rendering benchmark.
 overhead=[run('cpu',50,monitor=m,duration=10) for m in [False,True]]
 (OUT/'replay-summary.json').write_text(json.dumps({'runs':results,'monitoring_comparison':overhead,'total_replay_wall_seconds':time.monotonic()-start,'scope':'Replay of saved validation crops; no camera capture, Unity rendering, HTTP transfer or disk evidence writes'},indent=2))
if __name__=='__main__':main()
