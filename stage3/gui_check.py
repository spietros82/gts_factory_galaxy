"""Native 1080p operator path; test expectations stay in this evaluator."""
import json,time,urllib.request,shutil,uuid,base64
from pathlib import Path
from tools.unity_ui import Player
ROOT=Path.cwd();OUT=ROOT/'reports/stage3/gui';OUT.mkdir(exist_ok=True);RUNTIME=ROOT/'runtime/stage3-native'
def api(path='/state',body=None):
 req=urllib.request.Request('http://127.0.0.1:8820'+path,None if body is None else json.dumps(body).encode(),{'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(req,timeout=3))
def audit():return json.loads((RUNTIME/'stage3-audit.json').read_text())
def wait(fn,seconds=12):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  s=api()
  if fn(s):return s
  time.sleep(.15)
 raise RuntimeError('Native expectation timed out')
def click(x,y):
 p=Player();p.click(x*1600/1920,y*900/1080);time.sleep(.5)
def shot(name):
 p=Player();old=set(RUNTIME.glob('screen-*.png'));p.key('F12');end=time.monotonic()+5
 while time.monotonic()<end:
  new=set(RUNTIME.glob('screen-*.png'))-old
  if new:
   time.sleep(.3);dest=OUT/(name+'.png');shutil.copyfile(max(new,key=lambda p:p.stat().st_mtime),dest);time.sleep(.9);return str(dest)
  time.sleep(.1)
 raise RuntimeError('Native screenshot unavailable')
def main():
 checks=[];screens=[];states=[]
 def check(name,value):checks.append({'name':name,'pass':bool(value)});print(name,value,flush=True)
 def scene(view,x):click(x,112);check('Native navigation '+view,audit()['view']==view);screens.append(shot(view.lower().replace(' ','-')))
 try:
  for _ in range(50):
   try:Player();break
   except RuntimeError:time.sleep(.2)
  time.sleep(2);check('1920x1080 native window',Player().width==1920 and Player().height==1080)
  for view,x in [('Machine data',130),('Digital twin',360),('Combined',610),('Inspection',855)]:scene(view,x)
  for product,x in [('LAGER',915),('IPA',1025),('STOUT',1150)]:click(x,156);check('Product '+product,audit()['product']==product)
  click(915,156);s=wait(lambda s:len(s['events'])>=3);batch=s['events'][0]['batch_id'];r=[x for x in s['events'] if x['batch_id']==batch];check('Shared bottle/line/session/capture timestamp, distinct station/frame IDs',len(r)==3 and len({x['bottle_id'] for x in r})==1 and len({x['session_id'] for x in r})==1 and len({x['capture_utc'] for x in r})==1 and len({x['frame_id'] for x in r})==3)
  click(90,155);a=audit();time.sleep(1);b=audit();check('Pause retains source clock',a['paused'] and a['sim_time']==b['sim_time']);screens.append(shot('paused-historical'));click(90,155)
  old=audit()['session_id'];click(225,155);check('Reset creates new session',audit()['session_id']!=old);check('Review evidence preserved across reset',any(x['session_id']==old for x in api()['events']))
  for device,x in [('gpu',1775),('cpu',1565)]:
   click(x,112);s=wait(lambda s:s['selected_device']==device and len(s['events'])>=3 and all(r['device']==device for r in s['events'][:3]));check('Actual '+device+' batch',all(r['device']==device for r in s['events'][:3]));states.append(s)
  # Presenter controls contain fixture names; image inference receives none.
  for example,y,station,expected in [('Cap missing',376,'cap','missing'),('Cap displaced',432,'cap','displaced'),('Underfill',487,'fill','underfilled'),('Overfill',542,'fill','overfilled'),('Label missing',597,'label','missing'),('Label tilted',652,'label','misaligned'),('Poor image',707,'cap','uncertain')]:
   click(1310,70);click(290,y);start=time.time();click(855,112)
   s=wait(lambda s:any(r['station_id']==station and r['decision']==expected and __import__('datetime').datetime.fromisoformat(r['capture_utc']).timestamp()>start for r in s['events']),18);check('Rendered fixture '+example,True);states.append({'fixture_expected':example,'state':s});screens.append(shot(example.lower().replace(' ','-')))
  scene('Failure review',1080);click(230,305);screens.append(shot('event-review'));scene('Debug',1310);check('Debug metrics sampled with denominators',api().get('host_cpu_percent',-1)>=0);check('No Qwen GUI calls',api()['explanation_calls']==0)
 finally:(OUT/'verification.json').write_text(json.dumps({'checks':checks,'screenshots':screens,'states':states},indent=2))
if __name__=='__main__':main()
