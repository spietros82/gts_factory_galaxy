"""Actual native UI checks; no explanation button or model request."""
import json,shutil,time,urllib.request
from pathlib import Path
from tools.unity_ui import Player,x,t
ROOT=Path.cwd();OUT=ROOT/'reports/stage1';RUNTIME=ROOT/'runtime/stage1-native'
def audit():return json.loads((RUNTIME/'presentation-audit.json').read_text())
def wait(test,timeout=6):
 until=time.monotonic()+timeout
 while time.monotonic()<until:
  try:
   s=audit()
   if test(s):return s
  except (OSError,ValueError):pass
  time.sleep(.1)
 raise RuntimeError('Native UI did not reach expected state')
def shot(player,name):
 time.sleep(1.1);before=set(RUNTIME.glob('screen-*.png'));player.key('F12')
 until=time.monotonic()+4
 while time.monotonic()<until:
  fresh=set(RUNTIME.glob('screen-*.png'))-before
  if fresh:
   src=max(fresh,key=lambda p:p.stat().st_mtime);shutil.copyfile(src,OUT/name);return str(OUT/name)
  time.sleep(.1)
 raise RuntimeError('Native screenshot missing')
def click(player,px,py):
 # Let Unity consume pointer motion before button-down on the next frame.
 t.XTestFakeMotionEvent(player.d,-1,player.left+int(px*player.width/1600),player.top+int(py*player.height/900),0);x.XFlush(player.d);time.sleep(.18);player.click(px,py)
def main():
 wait(lambda s:time.time()-(RUNTIME/'presentation-audit.json').stat().st_mtime<1);time.sleep(.6);p=Player();time.sleep(.3);p.key('F5');checks=[];screens=[];click(p,160,124);wait(lambda s:s['product']=='LAGER');
 if not audit()['paused']:p.key('space')
 wait(lambda s:s['paused']);held=audit()['sim_time'];time.sleep(.7);checks.append({'name':'Pause holds single simulation clock','pass':audit()['sim_time']==held})
 for name,px in [('LAGER',160),('IPA',245),('STOUT',329)]:
  p=Player();click(p,px,124);s=wait(lambda s:s['product']==name);checks.append({'name':'Actual button selects '+name+' without advancing paused process','pass':s['sim_time']==held and s['view']=='line'});screens.append(shot(p,'product-'+name.lower()+'.png'))
 for key,name in [('F6','filler'),('F7','capper'),('F8','inspection'),('F5','line')]:
  p.key(key);s=wait(lambda s:s['view']==name);checks.append({'name':'Presentation view '+name,'pass':s['view']==name});screens.append(shot(p,'view-'+name+'.png'))
 p.key('space');s=wait(lambda s:not s['paused']);old_angle=s['capper_angle'];old_time=s['sim_time'];time.sleep(2);moving=audit();checks.append({'name':'Resume drives bottle motion and capper animation','pass':moving['sim_time']>old_time and moving['capper_angle']!=old_angle and (moving['first_bottle_id']!=s['first_bottle_id'] or moving['first_bottle_x']!=s['first_bottle_x'])})
 click(p,200,80);reset=wait(lambda s:s['sim_time']<45);checks.append({'name':'Reset seeded process retains selected visual identity','pass':reset['product']=='STOUT' and reset['sim_time']<45})
 click(p,160,124);wait(lambda s:s['product']=='LAGER');p.key('F5');p.key('F3');click(p,1325,80);time.sleep(4)
 with urllib.request.urlopen('http://127.0.0.1:8810/state',timeout=2) as reply:state=json.load(reply)
 checks.append({'name':'Preserved native inspection supplies a real legacy crop','pass':state.get('result') is not None and state['explanation_calls']==0});screens.append(shot(p,'inspection-baseline-evidence.png'))
 p.key('F2');click(p,1220,80);click(p,200,80);wait(lambda s:s['sim_time']<45);p.key('F5')
 report={'checks':checks,'all_pass':all(c['pass'] for c in checks),'screenshots':screens,'resolution':[p.width,p.height],'llm_calls':0,'scope':'Actual window input and application audit state; visual review of saved screenshots separately; learned accuracy not scored'}
 (OUT/'native-ui.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
 if not report['all_pass']:raise RuntimeError('Native UI check failed')
if __name__=='__main__':main()
