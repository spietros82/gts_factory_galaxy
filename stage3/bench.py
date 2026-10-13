"""Bounded native 3-condition comparison, no Qwen calls; frozen workload/settings."""
import csv,json,os,subprocess,time,urllib.request,datetime
from pathlib import Path
import numpy as np
ROOT=Path.cwd();OUT=ROOT/os.environ.get('STAGE3_BENCHMARK_OUTPUT','reports/stage3/performance')
def api(port,path='/state'):
 return json.load(urllib.request.urlopen('http://127.0.0.1:'+str(port)+path,timeout=2))
def stats(values):
 a=np.array([v for v in values if v is not None and v>=0],float)
 return {} if not len(a) else dict(n=len(a),mean=float(a.mean()),p50=float(np.percentile(a,50)),p95=float(np.percentile(a,95)),p99=float(np.percentile(a,99)),max=float(a.max()))
def run(condition,index):
 out=OUT/f'{condition}-{index}';out.mkdir(parents=True,exist_ok=False);cfg=json.loads((ROOT/'stage3/config.example.json').read_text());cfg.update(port=8821,data_path=str(out/'service'),device='gpu' if condition=='gpu' else 'cpu');(out/'config.json').write_text(json.dumps(cfg));env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2');started=time.monotonic();service=subprocess.Popen([str(ROOT/'stage3/.venv/bin/python'),'-m','stage3.service','--config',str(out/'config.json')],env=env,stdout=(out/'service-console.txt').open('w'),stderr=subprocess.STDOUT)
 try:
  for _ in range(60):
   try:
    if api(8821,'/health')['ready']:break
   except Exception:pass
   time.sleep(.2)
  else:raise RuntimeError('Benchmark service unavailable')
  native=out/'native';native.mkdir();cmd=[str(ROOT/'builds/stage3/FactoryGalaxy.x86_64'),'-screen-fullscreen','0','-screen-width','1920','-screen-height','1080','-logFile',str(out/'player.log'),'--data-path',str(native),'--profile','1','--presentation','true','--plc-demo','true','--stage3','true','--stage3-endpoint','http://127.0.0.1:8821','--frame-target','60','--duration','70','--measurement','true','--product-mix','true','--inspection-disabled','true' if condition=='disabled' else 'false']
  begin=time.monotonic();player=subprocess.Popen(cmd,stdout=(out/'console.txt').open('w'),stderr=subprocess.STDOUT);samples=[]
  while player.poll() is None and time.monotonic()-begin<85:
   try:samples.append({'wall_seconds':time.monotonic()-begin,'state':api(8821)})
   except Exception as e:samples.append({'error':str(e)})
   time.sleep(1)
  if player.poll() is None:player.terminate();player.wait(10);raise RuntimeError('Bounded player exceeded duration')
  rows=list(csv.DictReader(next(native.glob('frames-*.csv')).open()));frames=[float(r['wall_frame_interval_ms']) for r in rows if float(r['wall_seconds'])>=10 and float(r['wall_seconds'])<70];results=[json.loads(l) for l in (out/'service/results.jsonl').read_text().splitlines()] if (out/'service/results.jsonl').exists() else []
  run=json.loads(next(native.glob('run-*.json')).read_text());epoch=datetime.datetime.fromisoformat(run['started_utc']).timestamp()
  steady=[r for r in results if epoch+10<=datetime.datetime.fromisoformat(r['completed_utc']).timestamp()<epoch+70]
  resource=[r['state'] for r in samples if r.get('wall_seconds',0)>=10 and 'state' in r]
  summary={'condition':condition,'iteration':index,'native_exit':player.returncode,'command':cmd,'model_policy_sha256':__import__('hashlib').sha256(Path('stage3/models/policy.json').read_bytes()).hexdigest(),'warmup_seconds':10,'measured_render_seconds':60,'frames_ms':stats(frames),'fps':1000/np.mean(frames),'inspection_measurement_note':'Common UTC window10–70s from Unity startup. Captures beginning in warmup but finishing in steady interval included; full raw captures retained','inspections':len(steady),'capture_to_result_ms':stats([r['end_to_end_ms'] for r in steady]),'preprocessing_ms':stats([r['preprocess_ms'] for r in steady]),'transfer_ms':stats([r['transfer_ms'] for r in steady]),'inference_ms':stats([r['inference_ms'] for r in steady]),'gpu_shader_ms':stats([r['gpu_elapsed_ms'] for r in steady]),'queue_ms':stats([r['queue_ms'] for r in steady]),'completion_rate_wall_60s':len(steady)/60,'resources':{k:stats([s.get(k) for s in resource]) for k in ['host_cpu_percent','service_cpu_percent','service_rss_mb','native_cpu_percent','native_rss_mb','gpu_busy_percent','temperature_c','available_memory_gb','monitor_ms']},'final':api(8821),'wall_seconds':time.monotonic()-started}
  summary['final'].pop('events',None);summary['final'].pop('results',None);(out/'samples.json').write_text(json.dumps(samples));(out/'summary.json').write_text(json.dumps(summary,indent=2));print(condition,index,'FPS',summary['fps'],'inspections',len(steady),flush=True)
 finally:service.terminate();service.wait(10)
def main():
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'background-processes.txt').write_text(subprocess.check_output(['ps','-eo','pid,comm'],text=True));(OUT/'protocol.json').write_text(json.dumps({'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'conditions':['disabled','cpu','gpu'],'iterations':2,'resolution':[1920,1080],'native_duration':70,'warmup':10,'frame_target':60,'vsync':0,'msaa':4,'seed':42,'product_schedule':'20s cycle LAGER/IPA/STOUT','queue_capacity_batches':2,'capture_cadence_seconds':1.5,'new_llm_calls':0},indent=2))
 start=time.monotonic()
 for condition in ['disabled','cpu','gpu']:
  for i in [1,2]:
   if time.monotonic()-start>900:raise RuntimeError('Performance budget guard')
   run(condition,i)
 (OUT/'duration.json').write_text(json.dumps({'total_native_benchmark_wall_seconds':time.monotonic()-start}))
if __name__=='__main__':main()
