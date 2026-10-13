"""1Hz unprivileged counters; no process attribution from device-wide GPU busy."""
import os,time
from pathlib import Path
class Monitor:
 def __init__(self):self.previous=None;self.native_previous={}
 def sample(self):
  start=time.perf_counter();cpu=list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:9]));total=sum(cpu);idle=cpu[3]+cpu[4];fields=Path('/proc/self/stat').read_text().rsplit(')',1)[1].split();ticks=int(fields[11])+int(fields[12]);now=time.monotonic();host=process=-1
  if self.previous:
   wall=now-self.previous[0];host=100*(1-(idle-self.previous[2])/max(1,total-self.previous[1]));process=100*(ticks-self.previous[3])/os.sysconf('SC_CLK_TCK')/wall
  self.previous=(now,total,idle,ticks);mem={l.split(':')[0]:int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith(('MemAvailable:','MemTotal:'))}
  out={'host_cpu_percent':host,'service_cpu_percent':process,'service_rss_mb':int(fields[21])*os.sysconf('SC_PAGE_SIZE')/1e6,'available_memory_gb':mem['MemAvailable']/2**30,'gpu_busy_percent':-1,'temperature_c':-1}
  for p in Path('/sys/class/drm').glob('card[0-9]*/device/gpu_busy_percent'):
   try:out['gpu_busy_percent']=float(p.read_text())
   except OSError:pass
  for root in Path('/sys/class/hwmon').glob('hwmon*'):
   try:
    if (root/'name').read_text().strip()=='amdgpu':out['temperature_c']=float((root/'temp1_input').read_text())/1000
   except OSError:pass
  out['native_cpu_percent']=-1;out['native_rss_mb']=-1
  for proc in Path('/proc').iterdir():
   if not proc.name.isdigit():continue
   try:
    command=(proc/'cmdline').read_bytes()
    if b'/builds/stage3/FactoryGalaxy.x86_64' not in command or b'--stage3' not in command:continue
    fields=(proc/'stat').read_text().rsplit(')',1)[1].split();t=int(fields[11])+int(fields[12]);out['native_rss_mb']=int(fields[21])*os.sysconf('SC_PAGE_SIZE')/1e6;old=self.native_previous.get(proc.name)
    if old:out['native_cpu_percent']=100*(t-old[1])/os.sysconf('SC_CLK_TCK')/(now-old[0])
    self.native_previous[proc.name]=(now,t)
   except (OSError,ValueError):pass
  out['monitor_ms']=(time.perf_counter()-start)*1000;return out
