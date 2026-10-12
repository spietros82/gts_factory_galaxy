"""Functional native QA only; no explanation request or locked-test inference."""
import json,time,urllib.request,shutil
from pathlib import Path
from tools.unity_ui import Player
OUT=Path('reports/inspection/gui');OUT.mkdir(exist_ok=True);runtime=Path('runtime/inspection-native')
def state():return json.load(urllib.request.urlopen('http://127.0.0.1:8810/state',timeout=2))
def screenshot(player,name):
 time.sleep(1.05) # Native F12 filenames have one-second precision; prevent overwrite
 before=set(runtime.glob('screen-*.png'));player.key('F12')
 for _ in range(30):
  fresh=set(runtime.glob('screen-*.png'))-before
  if fresh:
   p=max(fresh,key=lambda f:f.stat().st_mtime);shutil.copyfile(p,OUT/name);return str(OUT/name)
  time.sleep(.1)
 raise RuntimeError('Actual native screenshot not written')
def main():
 p=Player();p.key('F3');time.sleep(.3);checks=[]
 checks.append({'name':'fresh learned inspection and crop endpoint','pass':state().get('result') is not None,'scope':'actual native capture/service'})
 screenshot(p,'01-focused-evidence.png')
 p.key('space');time.sleep(.4);before=state()['captured'];time.sleep(3);after=state();checks.append({'name':'pause holds capture, stale status explicit','pass':after['captured']==before and after['result']['status']=='historical-stale'})
 screenshot(p,'02-paused-stale-evidence.png');p.key('space');time.sleep(2.5);checks.append({'name':'resume captures new targets','pass':state()['captured']>before})
 old=state()['session'];p.click(200,80);time.sleep(2.5);new=state();checks.append({'name':'explicit reset creates new session and clears advice association','pass':new['session']!=old and new['assistant_frame_id']=='' and new['result']['frame_id'].startswith(new['session']+'-')})
 screenshot(p,'03-new-replay.png')
 # Actual observed quality originates from simulated observation records; toggle is not sent as evidence.
 before_uncertain=state()['uncertain'];p.click(1274,298);time.sleep(18);quality=state();checks.append({'name':'missing observed quality yields abstention','pass':quality['uncertain']>before_uncertain});screenshot(p,'04-observation-quality.png');p.click(1274,298)
 p.key('F4');time.sleep(.2);screenshot(p,'05-explanation-panel-no-extra-call.png');checks.append({'name':'native QA sends no explanation calls','pass':state()['explanation_calls']==0})
 p.click(200,80);time.sleep(2);p.key('F3');screenshot(p,'06-review-ready.png')
 out={'checks':checks,'model_calls':0,'llm_calls':0,'inspection':'normal runtime synthetic captures only; not a second locked evaluation or soak','source_commit':'a7513f2','all_pass':all(c['pass'] for c in checks)}
 (OUT/'results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
