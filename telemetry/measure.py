"""Short render-only comparison. No inference, tuning or diagnostic commands."""
import argparse,csv,datetime,json,os,subprocess,time
from pathlib import Path
import numpy as np
from factory.activity import Sampler
ROOT=Path(__file__).resolve().parent.parent

def run(label,binary):
 out=ROOT/'reports/stage2/raw'/label;out.mkdir(parents=True,exist_ok=False)
 cmd=[str(ROOT/binary),'-screen-fullscreen','0','-screen-width','1600','-screen-height','900','-logFile',str(out/'player.log'),'--focused-inspection','true','--profile','1','--frame-target','60','--measurement','true','--duration','35','--data-path',str(out),'--screenshot',str(ROOT/'reports/stage2'/f'{label}.png'),'--screenshot-after','7']
 cmd+=['--presentation','true','--disable-explanations','true','--comparison-camera','true']
 if label.startswith('after'):cmd+=['--plc-demo','true','--telemetry-view','combined']
 sampler=Sampler('http://127.0.0.1:11434');previous=None;samples=[];start=time.monotonic()
 with (out/'console.txt').open('w') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  while proc.poll() is None:
   record=sampler.sample();record['wall_seconds']=time.monotonic()-start
   try:
    fields=Path('/proc',str(proc.pid),'stat').read_text().rsplit(')',1)[1].split();ticks=int(fields[11])+int(fields[12]);now=time.monotonic()
    record['native_rss_bytes']=int(fields[21])*os.sysconf('SC_PAGE_SIZE')
    record['native_cpu_one_core_percent']=None if previous is None else (ticks-previous[0])/os.sysconf('SC_CLK_TCK')/(now-previous[1])*100
    previous=(ticks,now)
   except OSError:pass
   samples.append(record);time.sleep(.5)
  exitcode=proc.returncode
 rows=list(csv.DictReader(next(out.glob('frames-*.csv')).open()));dt=[float(r['wall_frame_interval_ms']) for r in rows if float(r['wall_seconds'])>=5]
 def stats(values):
  a=np.array([v for v in values if v is not None],float)
  return None if not len(a) else {'n':len(a),'mean':float(a.mean()),'p50':float(np.percentile(a,50)),'p95':float(np.percentile(a,95)),'p99':float(np.percentile(a,99)),'max':float(a.max())}
 steady=[s for s in samples if s['wall_seconds']>=5]
 report={'label':label,'exit':exitcode,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd,'warmup_seconds':5,'duration_seconds':35,'frames_ms':stats(dt),'mean_fps':1000/np.mean(dt),'host_cpu_percent':stats([s['host_cpu_percent'] for s in steady]),'native_cpu_one_core_percent':stats([s.get('native_cpu_one_core_percent') for s in steady]),'native_rss_bytes':stats([s.get('native_rss_bytes') for s in steady]),'gpu_device_busy_percent':stats([s['gpu'].get('gpu_busy_percent') for s in steady]),'host_mem_available_bytes':stats([s.get('MemAvailable') for s in steady]),'run':json.loads(next(out.glob('run-*.json')).read_text()),'inference_calls':0,'scope':'healthy common-view rendering with telemetry, no inference; background service remains running; GPU counter is device-wide'}
 (out/'resources.json').write_text(json.dumps(samples,indent=2));(ROOT/'reports/stage2'/f'{label}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
 if exitcode:raise RuntimeError('Native run failed')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('label');p.add_argument('binary');a=p.parse_args();run(a.label,a.binary)
