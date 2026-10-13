"""Actual native controls/screenshots; no Qwen. Kept separate from capacity runs."""
import json,time,shutil,urllib.request
from pathlib import Path
from tools.unity_ui import Player,x,t
from stage3.ui_revision_check import activate
OUT=Path('reports/stage4/native-qa');OUT.mkdir(parents=True,exist_ok=True);R=Path('runtime/stage4-native');checks=[]
def api(line='Line01'):return json.load(urllib.request.urlopen('http://127.0.0.1:8830/state?line_id='+line,timeout=3))
def audit():return json.loads((R/'stage4-audit.json').read_text())
def click(px,py):
 activate();p=Player();t.XTestFakeMotionEvent(p.d,-1,p.left+int(px*p.width/1920),p.top+int(py*p.height/1080),0);x.XFlush(p.d);time.sleep(.15);p.click(px*1600/1920,py*900/1080);time.sleep(1.1)
def wait(fn,timeout=12):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  if fn():return True
  time.sleep(.25)
 return False
def check(label,value):checks.append({'name':label,'pass':bool(value)});print(label,bool(value),flush=True)
def shot(name):
 activate();old=set(R.glob('screen-*.png'));Player().key('F12');wait(lambda:bool(set(R.glob('screen-*.png'))-old),4);paths=set(R.glob('screen-*.png'))-old
 if not paths:raise RuntimeError('Native screenshot missing')
 time.sleep(.2);shutil.copy2(max(paths,key=lambda p:p.stat().st_mtime),OUT/(name+'.png'))
def main():
 try:
  wait(lambda:api()['active_lines']==1);wait(lambda:api().get('native',{}).get('width')==1920 and api().get('native',{}).get('height')==1080,8);time.sleep(1);calls=api()['explanation_calls'];p=Player();check('Actual1920×1080',p.width==1920 and p.height==1080);shot('one-line')
  click(210,138);check('Three independent lines',wait(lambda:api()['active_lines']==3));check('Cyclic products', [r['product'] for r in audit()['lines']]==['LAGER','IPA','STOUT']);check('Distinct sessions',len({r['session_id'] for r in audit()['lines']})==3)
  check('All offscreen lines inspected',wait(lambda:len(api()['lines'])==3 and all(v['completed']>=3 for v in api()['lines']),20));shot('three-lines')
  click(93,357);check('Select Line02',audit()['selected_line']=='Line02');click(1640,436);check('Line02 underfill',wait(lambda:any(v['decision']=='underfilled' for v in api('Line02')['results']),12));check('Line01 stays healthy',all(v['decision'] in ['aligned','within_range'] for v in api('Line01')['results']));shot('line02-evidence')
  click(1642,561);check('Lager product selected on Line02',audit()['lines'][1]['product']=='LAGER');click(1844,561);check('Stout product selected on Line02',audit()['lines'][1]['product']=='STOUT');click(1750,561)
  click(1642,315);check('Blockage onlyLine02',audit()['lines'][1]['blocked'] and not audit()['lines'][0]['blocked']);before=audit()['lines'][1]['buffer'];time.sleep(8);check('Buffer accumulates',audit()['lines'][1]['buffer']>before);shot('blockage');click(1810,315);check('Clear actual blockage',not audit()['lines'][1]['blocked']);
  click(1000,98);time.sleep(1.2);a=audit();time.sleep(1.2);b=audit();check('Pause freezes all processes',a['paused'] and [v['sim_time'] for v in a['lines']]==[v['sim_time'] for v in b['lines']]);check('Paused evidence historical',all(v['historical'] for v in api('Line02')['results']));click(1000,98)
  old=audit()['lines'][1]['session_id'];click(1640,357);check('Reset independent session',audit()['lines'][1]['session_id']!=old);check('Old results excluded from current',all(v['session_id']!=old for v in api('Line02')['results']))
  click(151,139);check('Remove lines',wait(lambda:api()['active_lines']==1));click(211,139);check('Re-added session differs',wait(lambda:len(audit()['lines'])==3 and audit()['lines'][1]['session_id']!=old))
  click(100,98);check('Machine data mode',audit()['view']=='Machine data');shot('machine-data');click(265,98);check('Digital twin mode',audit()['view']=='Digital twin');shot('digital-twin');click(800,98);check('Debug mode',audit()['view']=='Debug');shot('debug');click(650,98);check('Failure review mode',audit()['view']=='Failure review');shot('failure-review');click(445,98)
  click(690,138);check('GPU selected',wait(lambda:api()['selected_device']=='gpu'));check('GPU actually completes new batch',wait(lambda:api('Line01')['results'] and all(v['device']=='gpu' for v in api('Line01')['results']),12));click(610,138)
  click(383,138);check('24line allocation',wait(lambda:api()['active_lines']==24,35));check('All24 lines processed',wait(lambda:all(v['completed']>=3 for v in api()['lines']) and len(api()['lines'])==24,35));shot('many-lines')
  click(1795,98);check('Stop benchmark returns one-lineCPU',wait(lambda:api()['active_lines']==1 and api()['selected_device']=='cpu'));check('No language calls',api()['explanation_calls']==calls)
 finally:(OUT/'checks.json').write_text(json.dumps({'checks':checks,'scope':'Native functional integration, not capacity or real-camera accuracy'},indent=2))
 if not all(v['pass'] for v in checks):raise SystemExit(1)
if __name__=='__main__':main()
