"""Exactly one bounded 300s native run; up to three serial fixed-template explanation calls."""
import datetime,json,subprocess,time,urllib.request,os
from pathlib import Path
from factory.activity import Sampler
ROOT=Path.cwd();OUT=ROOT/'reports/inspection/live';OUT.mkdir(parents=True,exist_ok=True)

def api(path,body=None):
 req=urllib.request.Request('http://127.0.0.1:8810'+path,None if body is None else json.dumps(body).encode(),{'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(req,timeout=3))
def main():
 protocol={'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_duration_seconds':300,'frame_warmup_seconds':5,'resolution':[1600,900],'frame_target':60,'vsync':0,'msaa':4,'seed':42,'scenario':'existing cap-placement scenario','profile':2,'inspection':'per-bottle x2.92 trigger, fixed camera','queue_capacity':2,'maximum_captures':1000,'language_call_times_seconds':[45,135,225],'model':'qwen3:8b','prompt':'inspection/EXPLANATION_PROMPT.txt','retry':False,'backend':'sklearn RF CPU; Unity OpenGLCore GPU','baseline_services':'initial factory/streaming units inactive; none stopped'}
 (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2));cfg=json.loads((ROOT/'inspection/config.example.json').read_text());cfg['data_path']='reports/inspection/live/service'
 (ROOT/'inspection/config.live.json').write_text(json.dumps(cfg,indent=2))
 native=OUT/'native';native.mkdir(exist_ok=True)
 env=os.environ.copy();env.update({'OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2'})
 service=subprocess.Popen([str(ROOT/'.venv/bin/python'),'-m','inspection.service','--config','inspection/config.live.json'],env=env,stdout=(OUT/'service-console.txt').open('w'),stderr=subprocess.STDOUT)
 try:
  ready=False
  for _ in range(50):
   if service.poll() is not None:raise RuntimeError('Inspection service exited')
   try:api('/health');ready=True;break
   except Exception:time.sleep(.2)
  if not ready:raise RuntimeError('Inspection service unavailable')
  commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
  command=[str(ROOT/'builds/inspection/FactoryGalaxy.x86_64'),'-screen-fullscreen','0','-screen-width','1600','-screen-height','900','-logFile',str(OUT/'native-player.log'),'--focused-inspection','true','--inspection-endpoint','http://127.0.0.1:8810','--data-path',str(native),'--profile','2','--scenario','cap','--frame-target','60','--measurement','true','--duration','300','--screenshot',str(OUT/'native-evidence.png'),'--screenshot-after','60']
  player=subprocess.Popen(command,stdout=(OUT/'native-stdout.txt').open('w'),stderr=subprocess.STDOUT)
  sampler=Sampler('http://127.0.0.1:11434');started=time.monotonic();asked=0;status=[];hardware=[];requests=[];next_sample=0
  while player.poll() is None and time.monotonic()-started<320:
   elapsed=time.monotonic()-started
   if elapsed>=next_sample:
    next_sample=elapsed+2
    try:state=api('/state');status.append({'elapsed_seconds':elapsed,'state':state})
    except Exception as e:state={};status.append({'elapsed_seconds':elapsed,'error':str(e)})
    record=sampler.sample();record['elapsed_seconds']=elapsed
    for name,pid in [('native',player.pid),('inspection_service',service.pid)]:
     try:
      fields=Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split();rss=int(fields[21])*os.sysconf('SC_PAGE_SIZE');ticks=int(fields[11])+int(fields[12]);record[name]={'pid':pid,'rss_bytes':rss,'cpu_ticks_total':ticks}
     except (OSError,ValueError):record[name]={'pid':pid,'status':'unavailable'}
    hardware.append(record)
    if asked<3 and elapsed>=protocol['language_call_times_seconds'][asked]:
     if state.get('assistant_state') not in ['queued','running']:
      # At most one request per scheduled slot, including any refusal. No retry.
      try:reply=api('/explain',{});requests.append({'elapsed':elapsed,'reply':reply})
      except Exception as e:requests.append({'elapsed':elapsed,'error':str(e)})
      asked+=1
   time.sleep(.1)
  if player.poll() is None:player.terminate();player.wait(10)
  # Drain only existing queued explanation; never generate an additional request.
  deadline=time.monotonic()+125
  while time.monotonic()<deadline:
   final=api('/state')
   if final.get('assistant_state') not in ['queued','running']:break
   time.sleep(.5)
  (OUT/'states.json').write_text(json.dumps(status,indent=2));(OUT/'hardware.json').write_text(json.dumps(hardware,indent=2));(OUT/'final.json').write_text(json.dumps({'tested_commit':commit,'native_returncode':player.returncode,'monitor_wall_seconds':time.monotonic()-started,'requests':requests,'final_state':final,'native_command':command},indent=2))
  print(json.dumps({'exit':player.returncode,'samples':len(status),'requests':requests,'final':final},indent=2))
 finally:
  service.terminate();service.wait(10)
if __name__=='__main__':main()
