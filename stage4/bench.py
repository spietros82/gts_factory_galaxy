"""One bounded adaptive capacity cycle. No Qwen, no training. Raw phase data retained."""
import csv,json,os,subprocess,time,urllib.request,datetime,hashlib,socket,sys
from pathlib import Path
import numpy as np
ROOT=Path.cwd();OUT=ROOT/'reports/stage4/capacity';PORT=8831;BUDGET=2700.;global_start=0.;summaries=[]
def api(path='/state',value=None):
 request=urllib.request.Request('http://127.0.0.1:'+str(PORT)+path,None if value is None else json.dumps(value).encode(),{'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(request,timeout=2))
def stats(values):
 a=np.asarray([v for v in values if v is not None and v>=0],float)
 return {} if not len(a) else dict(n=int(len(a)),mean=float(a.mean()),p50=float(np.percentile(a,50)),p95=float(np.percentile(a,95)),p99=float(np.percentile(a,99)),max=float(a.max()))
def save():
 (OUT/'summary.json').write_text(json.dumps({'wall_elapsed_seconds':time.monotonic()-global_start,'budget_seconds':BUDGET,'phases':summaries},indent=2))
def run(mode,device,count,iteration='explore',warm=10,measure=20,rate=.667,acquisition='Normal'):
 if time.monotonic()-global_start+warm+measure+25>BUDGET:raise TimeoutError('Global45minute budget')
 name=f'{mode}-{device}-{count}-{iteration}';out=OUT/name;out.mkdir(parents=True,exist_ok=False);native=out/'native';native.mkdir();cfg=json.loads((ROOT/'stage4/config.example.json').read_text());cfg.update(port=PORT,data_path=str(out/'service'),device=device);(out/'config.json').write_text(json.dumps(cfg));env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2');phase_start=time.monotonic();service=None;player=None;supervisor=None;samples=[];failure=''
 try:
  service=subprocess.Popen([str(ROOT/'stage3/.venv/bin/python'),'-m','stage4.service','--config',str(out/'config.json')],env=env,stdout=(out/'service-console.txt').open('w'),stderr=subprocess.STDOUT)
  for _ in range(100):
   try:
    if api('/health')['ready']:break
   except Exception:pass
   time.sleep(.1)
  else:raise RuntimeError('Service startup failed')
  cmd=[str(ROOT/'builds/stage4/FactoryGalaxy.x86_64'),'-screen-fullscreen','1','-screen-width','1920','-screen-height','1080','-logFile',str(out/'player.log'),'--stage4','true','--stage4-endpoint','http://127.0.0.1:'+str(PORT),'--data-path',str(native),'--line-count',str(count),'--vision-device',device,'--measurement','true','--inspection-disabled','true' if mode=='render' else 'false','--duration',str(warm+measure),'--phase',name,'--acquisition',acquisition,'--capture-rate',str(rate)]
  (out/'command.json').write_text(json.dumps(cmd));begin=time.monotonic();player=subprocess.Popen(cmd,env=env,stdout=(out/'console.txt').open('w'),stderr=subprocess.STDOUT);supervisor=subprocess.Popen([sys.executable,'-m','stage4.supervisor','--pid',str(player.pid),'--native',str(native),'--limit',str(warm+measure+60)],stdout=(out/'supervisor-console.txt').open('w'),stderr=subprocess.STDOUT)
  while player.poll() is None:
   if time.monotonic()-global_start>BUDGET or time.monotonic()-begin>warm+measure+65:failure='Duration guard';player.terminate();break
   try:
    v=api();v.pop('results',None);v.pop('events',None);samples.append({'monotonic':time.monotonic(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':v})
    if v.get('stop_reason'):failure=v['stop_reason'];player.terminate();break
   except Exception as e:samples.append({'error':str(e)})
   time.sleep(.5)
  try:player.wait(10)
  except subprocess.TimeoutExpired:player.kill();player.wait();failure='Owned player did not stop gracefully'
  if (native/'supervisor-stop.json').exists():failure=json.loads((native/'supervisor-stop.json').read_text())['reason']
  if not (native/'run.json').exists():raise RuntimeError('No complete native measurement: '+failure)
  metadata=json.loads((native/'run.json').read_text());rows=list(csv.DictReader((native/'frames.csv').open()));steady_rows=[r for r in rows if warm<=float(r['wall_seconds'])<warm+measure];frames=[float(r['frame_interval_ms']) for r in steady_rows];epoch=datetime.datetime.fromisoformat(metadata['started_utc']).timestamp();window=[r['state'] for r in samples if 'state'in r and warm<=r['state'].get('native',{}).get('wall_seconds',-1)<warm+measure]
  records=[]
  for file in sorted((out/'service').glob('results.jsonl*')):
   records.extend(json.loads(l) for l in file.read_text().splitlines())
  steady=[r for r in records if epoch+warm<=datetime.datetime.fromisoformat(r['completed_utc']).timestamp()<epoch+warm+measure]
  final=api();final.pop('events',None);final.pop('results',None);first=min([r['monotonic'] for r in samples if r.get('state',{}).get('native',{}).get('active_lines')==count],default=begin)
  perline={f'Line{i+1:02}':sum(r['line_id']==f'Line{i+1:02}' for r in steady) for i in range(count)};fstats=stats(frames);fps=1000/fstats['mean'] if fstats else 0;renderpass=bool(fstats and fps>=57 and fstats['p95']<=20 and fstats['p99']<=33.34);counts=final['counts'];nativefinal=final.get('native',{});drops=nativefinal.get('native_drops',0);deadlines=sum(r['end_to_end_ms']>2000 for r in steady);insppass=mode=='render' or bool(steady and all(v>=3 for v in perline.values()) and not drops and not deadlines and all(r['device']==device for r in steady));passed=renderpass and insppass and not failure and metadata['width']==1920 and metadata['height']==1080
  capture_records=[]
  for file in native.glob('captures.jsonl*'):capture_records.extend(json.loads(l) for l in file.read_text().splitlines())
  capture_window=[r for r in capture_records if epoch+warm<=datetime.datetime.fromisoformat(r['capture_utc']).timestamp()<epoch+warm+measure]
  summary={'name':name,'mode':mode,'device':device,'line_count':count,'iteration':iteration,'warmup_seconds':warm,'measurement_seconds':measure,'configured_acquisition':acquisition,'configured_batch_rate_per_line':rate,'cold_to_first_native_heartbeat_s':first-begin,'native_metadata':metadata,'passed':passed,'render_pass':renderpass,'inspection_pass':insppass,'failure':failure,'fps':fps,'frames_ms':fstats,'component_frame_ms':{k:stats([float(r[k]) for r in steady_rows]) for k in ['simulation_tick_ms','visual_update_ms','camera_render_ms','readback_ms','encode_ms']},'active_camera_frames_ms':{k:stats([float(r[k]) for r in steady_rows if float(r['camera_render_ms'])>0]) for k in ['camera_render_ms','readback_ms','encode_ms']},'completed_images':len(steady),'completed_images_per_s':len(steady)/measure,'completed_three_view_batches_s':len(steady)/3/measure,'actual_offered_images_s':len(capture_window)*3/measure,'accepted_images_s':sum(r['accepted'] for r in capture_window)*3/measure,'acquisition_wait_ms':stats([r['acquisition_wait_ms'] for r in capture_window]),'transport_ms':stats([r['transport_ms'] for r in capture_window]),'per_line_completed_images':perline,'end_to_end_ms':stats([r['end_to_end_ms'] for r in steady]),'queue_ms':stats([r['queue_ms'] for r in steady]),'classifier_ms':stats([r.get('classifier_ms',0) for r in steady]),'preprocess_ms':stats([r['preprocess_ms'] for r in steady]),'transfer_ms':stats([r['transfer_ms'] for r in steady]),'inference_ms':stats([r['inference_ms'] for r in steady]),'storage_ms':stats([r.get('storage_ms',0) for r in steady]),'gpu_shader_ms':stats([r['gpu_elapsed_ms'] for r in steady]),'drops_total':drops,'missed_deadlines_steady':deadlines,'queue_max':max([0]+[r.get('queue_depth',0) for r in window]),'native_pending_capture_max':max([0]+[r.get('native',{}).get('pending_capture',0) for r in window]),'resources':{k:stats([r.get(k,-1) for r in window]) for k in ['host_cpu_percent','service_cpu_percent','native_cpu_percent','service_rss_mb','native_rss_mb','gpu_busy_percent','temperature_c','cpu_temperature_c','available_memory_gb','monitor_ms']},'final':final,'phase_wall_seconds':time.monotonic()-phase_start}
  (out/'samples.json').write_text(json.dumps(samples));(out/'summary.json').write_text(json.dumps(summary,indent=2));summaries.append(summary);save();print(name,'PASS'if passed else'FAIL',round(fps,2),'FPS',round(summary['completed_images_per_s'],2),'images/s',flush=True);return summary
 finally:
  for child in [player,supervisor,service]:
   if child and child.poll() is None:
    child.terminate()
    try:child.wait(5)
    except subprocess.TimeoutExpired:child.kill();child.wait()

def abort_on_guard(result):
 if result.get('failure'):raise RuntimeError('Cycle stopped by guard: '+result['failure'])

def main():
 global global_start
 OUT.mkdir(parents=True,exist_ok=False)
 with socket.socket() as s:s.bind(('127.0.0.1',PORT))
 global_start=time.monotonic();(OUT/'background-processes.txt').write_text(subprocess.check_output(['ps','-eo','pid,comm'],text=True));(OUT/'frozen-protocol.md').write_bytes((ROOT/'stage4/PROTOCOL.md').read_bytes());(OUT/'freeze.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'models':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'stage3/models').glob('*')},'resolution':[1920,1080],'qwen_calls':0,'budget_seconds':BUDGET},indent=2));boundaries={}
 try:
  for mode,device in [('full','cpu'),('full','gpu'),('render','cpu')]:
   passed=[];failed=None
   for count in [1,3,6,12,24,48]:
    result=run(mode,device,count)
    abort_on_guard(result)
    if result['passed']:passed.append(count)
    else:failed=count;break
   boundaries[mode+'-'+device]={'highest_exploratory_pass':max(passed)if passed else None,'first_exploratory_failure':failed,'ceiling':48 if failed is None else None}
  (OUT/'boundaries.json').write_text(json.dumps(boundaries,indent=2))
  for mode,device in [('full','cpu'),('full','gpu'),('render','cpu')]:
   boundary=boundaries[mode+'-'+device];counts=list(dict.fromkeys([c for c in [boundary['highest_exploratory_pass'],boundary['first_exploratory_failure']] if c]))
   for count in counts:
    for i in [1,2]:abort_on_guard(run(mode,device,count,'confirm'+str(i),10,60))
  for device in ['cpu','gpu']:
   for rate in [1,2,4,8]:
    result=run('rate',device,3,'rate'+str(rate),5,15,rate,'Benchmark')
    abort_on_guard(result)
    if not result['passed']:break
  from stage4.replay import run_replay
  replay=[]
  for device in ["cpu","gpu"]:
   for rate in [10,50,100,200,400]:
    if time.monotonic()-global_start+15>BUDGET:raise TimeoutError("Global45minute replay budget")
    result=run_replay(OUT/("replay-"+device+"-"+str(rate)),device,rate);replay.append(result)
    (OUT/"replay-summary.json").write_text(json.dumps(replay,indent=2))
    if not result["passed"]:break
  # Any remaining common CPU/GPU counts already have matched explore runs; confirmations
  # need not fabricate repeats beyond the frozen boundary confirmation plan.
 except Exception as e:
  (OUT/'cycle-error.json').write_text(json.dumps({'error':str(e),'elapsed_seconds':time.monotonic()-global_start}));print('CYCLE ERROR',repr(e),flush=True);raise
 finally:
  save();(OUT/'duration.json').write_text(json.dumps({'total_wall_seconds':time.monotonic()-global_start,'budget_seconds':BUDGET,'new_qwen_calls':0}))
if __name__=='__main__':main()
