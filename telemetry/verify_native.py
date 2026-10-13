"""Stage 2 native inputs and audited contract; no inference or hidden repair."""
import json,time,shutil
from pathlib import Path
from tools.unity_ui import Player,x,t
ROOT=Path.cwd();RUNTIME=ROOT/'runtime/stage2-native';OUT=ROOT/'reports/stage2'
def audit():return json.loads((RUNTIME/'telemetry-audit.json').read_text())
def wait(check,seconds=8):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  try:
   v=audit()
   if check(v):return v
  except (OSError,ValueError):pass
  time.sleep(.1)
 raise RuntimeError('Native state did not meet expectation')
def click(p,px,py):
 t.XTestFakeMotionEvent(p.d,-1,p.left+int(px*p.width/1600),p.top+int(py*p.height/900),0);x.XFlush(p.d);time.sleep(.18);p.click(px,py)
def shot(p,name):
 time.sleep(1.1);before=set(RUNTIME.glob('screen-*.png'));p.key('F12')
 end=time.monotonic()+4
 while time.monotonic()<end:
  new=set(RUNTIME.glob('screen-*.png'))-before
  if new:
   src=max(new,key=lambda p:p.stat().st_mtime);dest=OUT/(name+'.png');shutil.copyfile(src,dest);return str(dest)
  time.sleep(.1)
 raise RuntimeError('Screenshot missing')
def main():
 checks=[];screens=[];snapshots={};
 def check(label,b):
  checks.append({'name':label,'pass':bool(b)});print(label,bool(b),flush=True)
  if not b:raise AssertionError(label)
 def capture(name):snapshots[name]=audit();screens.append(shot(Player(),name))
 try:
  wait(lambda s:time.time()-(RUNTIME/'telemetry-audit.json').stat().st_mtime<1);p=Player();p.key('R');wait(lambda s:s['sim_time']<43);p.key('space');held=wait(lambda s:s['paused']);time.sleep(2)
  check('Pause keeps source process time and fresh paused heartbeat',audit()['sim_time']==held['sim_time'] and audit()['frame']['source_time']==held['sim_time'] and audit()['frame']['simulation_paused'] and audit()['fresh'])
  for mode,px in [('data',240),('twin',790),('combined',1300)]:
   click(p,px,102);s=wait(lambda s:s['mode']==mode);check('Actual mode button: '+mode,s['mode']==mode);capture(mode+'-'+str(p.width))
  p.key('1');wait(lambda s:s['mode']=='data');click(p,165,450);s=wait(lambda s:s['selected']=='conveyor');check('Clicking Conveyor tag associates machine',s['selected']=='conveyor')
  p.key('3');p.key('F5');s=wait(lambda s:s['selected']=='line');click(p,s['filler_screen_x']*1600/p.width,s['filler_screen_y']*900/p.height);s=wait(lambda s:s['selected']=='filler');check('Actual 3D machine click selects matching tag group',s['selected']=='filler')
  for product,px in [('LAGER',75),('IPA',170),('STOUT',265)]:
   click(p,px,180);s=wait(lambda s:s['product']==product);check('Product switch '+product+' preserves paused clock',s['sim_time']==held['sim_time'])
  for key,asset in [('F6','filler'),('F7','capper'),('F8','inspection'),('F5','line')]:
   p.key(key);check('Existing presentation view '+asset,wait(lambda s:s['selected']==asset)['selected']==asset)
  p.key('space');wait(lambda s:not s['paused']);p.key('B');start=wait(lambda s:s['blocked']);capture('blockage-start-'+str(p.width));check('Blockage begins before threshold accumulation',start['buffer']<15)
  click(p,803,140);peak=wait(lambda s:s['buffer']>=15,35);check('Existing process queue accumulates',peak['buffer']>=15)
  upstream=wait(lambda s:s['infeed_state']=='Blocked' or s['filler_state']=='Waiting',25);check('Upstream delay is observed, not instant blanket stop',upstream['blocked']);p.key('F5');p.key('space');wait(lambda s:s['paused']);capture('blockage-'+str(p.width));p.key('space');wait(lambda s:not s['paused']);p.key('C');wait(lambda s:not s['blocked']);recovered=wait(lambda s:s['buffer']<15 and s['packed']>peak['packed']+10,40);check('Clear recovers throughput and buffer',recovered['packed']>peak['packed']);capture('recovery-'+str(p.width))
  p.key('F9');wait(lambda s:s['suspended'] and not s['fresh']);old=audit();time.sleep(.9);now=audit();check('Stale telemetry withholds state and freezes mechanism, while process continues',now['filler_state']=='Stale' and now['capper_angle']==old['capper_angle'] and now['sim_time']>old['sim_time']);capture('stale-'+str(p.width));p.key('F9');wait(lambda s:not s['suspended'] and s['fresh']);
  p.key('F10');s=wait(lambda s:s['missing'] and s['filler_state']=='Unknown');check('Missing filler is Unknown, not Running/zero',all(not v['has_value'] for v in s['frame']['tags'] if v['asset']=='filler'));p.key('F6');capture('missing-'+str(p.width));p.key('F10');wait(lambda s:not s['missing']);old_session=audit()['session'];p.key('R');reset=wait(lambda s:s['session']!=old_session);check('Reset creates new session, clears outage/blockage/timeline and preserves product',not reset['blocked'] and reset['product']=='STOUT' and len(reset['timeline'])==1 and reset['sim_time']<43);click(p,75,180);p.key('F5');p.key('3');capture('review-'+str(p.width))
 finally:
  report={'checks':checks,'all_pass':bool(checks) and all(c['pass'] for c in checks),'screenshots':screens,'snapshots':snapshots,'resolution':[p.width,p.height],'method':'Actual native inputs and exported adapter/mapping state; screenshot readability assessed separately','inference_requests':0};(OUT/('native-'+str(p.width)+'.json')).write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
