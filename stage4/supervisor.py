"""Independent guard for ONE owned benchmark child. No unrelated process control."""
import argparse,json,time,os,signal
from pathlib import Path

def supervise(pid,native,limit):
 started=time.monotonic();hot={};low=0.;last=None;native=Path(native)
 def stop(reason):
  (native/'supervisor-stop.json').write_text(json.dumps({'reason':reason,'wall_seconds':time.monotonic()-started}))
  try:
   command=(Path('/proc')/str(pid)/'cmdline').read_bytes()
   if b'--stage4' not in command or str(native).encode() not in command:return
   os.kill(pid,signal.SIGTERM)
   time.sleep(3)
   if (Path('/proc')/str(pid)/'cmdline').exists() and (Path('/proc')/str(pid)/'cmdline').read_bytes()==command:os.kill(pid,signal.SIGKILL)
  except (OSError,ProcessLookupError):pass
 while (Path('/proc')/str(pid)/'cmdline').exists():
  now=time.monotonic();reason=''
  if now-started>limit:reason='Owned phase duration limit'
  try:
   mem={l.split(':')[0]:int(l.split()[1])/2**20 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')}
   if mem['MemAvailable']<16:reason='Available memory below16GiB'
   for root in Path('/sys/class/hwmon').glob('hwmon*'):
    try:
     name=(root/'name').read_text().strip()
     if name not in ['amdgpu','k10temp']:continue
     temp=float((root/'temp1_input').read_text())/1000;threshold=85 if name=='amdgpu' else 90
     if temp>=threshold:hot.setdefault(name,now)
     else:hot.pop(name,None)
     if name in hot and now-hot[name]>=10:reason='Sustained temperature guard: '+name
    except OSError:pass
   if (native/'benchmark-stop.txt').exists():reason='Operator stop'
   p=native/'stage4-audit.json'
   if p.exists():
    if time.time()-p.stat().st_mtime>8:reason='Native heartbeat older than8s'
    v=json.loads(p.read_text())
    if v['wall_seconds']>10 and v['fps']<10:
     if not low:low=now
     elif now-low>=3:reason='Native responsiveness below10FPS for3s'
    else:low=0
  except (OSError,ValueError,KeyError):pass
  if reason:stop(reason);return
  time.sleep(.5)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--native',required=True);p.add_argument('--limit',type=float,required=True);a=p.parse_args();supervise(a.pid,a.native,a.limit)
