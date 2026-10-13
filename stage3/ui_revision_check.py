"""Focused native layout smoke check. No explanation requests or held-out evaluation."""
import json,time,shutil,urllib.request
from pathlib import Path
from tools.unity_ui import Player,x,t,D,U
import ctypes as C
OUT=Path('reports/stage3/ui-revision');RUNTIME=Path('runtime/stage3-native')
def state():
 session=json.loads((RUNTIME/'stage3-audit.json').read_text())['session_id'] if (RUNTIME/'stage3-audit.json').exists() else ''
 return json.load(urllib.request.urlopen('http://127.0.0.1:8820/state?session_id='+session,timeout=3))
def audit():return json.loads((RUNTIME/'stage3-audit.json').read_text())
class Client(C.Structure):
 _fields_=[('type',C.c_int),('serial',U),('send_event',C.c_int),('display',D),('window',U),('message_type',U),('format',C.c_int),('data',C.c_long*5)]
class Event(C.Union):_fields_=[('client',Client),('pad',C.c_long*24)]
def activate():
 # Ask the window manager to foreground the player, including over Wayland windows.
 p=Player();x.XInternAtom.argtypes=[D,C.c_char_p,C.c_int];x.XInternAtom.restype=U;x.XSendEvent.argtypes=[D,U,C.c_int,C.c_long,C.POINTER(Event)]
 e=Event();e.client.type=33;e.client.display=p.d;e.client.window=p.window;e.client.message_type=x.XInternAtom(p.d,b'_NET_ACTIVE_WINDOW',0);e.client.format=32;e.client.data[0]=2
 x.XSendEvent(p.d,p.root,0,(1<<20)|(1<<19),C.byref(e));x.XFlush(p.d);time.sleep(.3)
def click(px,py):
 activate();p=Player();t.XTestFakeMotionEvent(p.d,-1,p.left+int(px*p.width/1920),p.top+int(py*p.height/1080),0);x.XFlush(p.d);time.sleep(.2)
 p.click(px*1600/1920,py*900/1080);time.sleep(.7)
def shot(name):
 time.sleep(1);old=set(RUNTIME.glob('screen-*.png'));Player().key('F12')
 for _ in range(40):
  new=set(RUNTIME.glob('screen-*.png'))-old
  if new:
   time.sleep(.3);shutil.copy2(max(new,key=lambda p:p.stat().st_mtime),OUT/(name+'.png'));return
  time.sleep(.1)
 raise RuntimeError('Screenshot unavailable')
def main():
 checks=[];OUT.mkdir(parents=True,exist_ok=True);calls=state()['explanation_calls']
 def check(name,v):checks.append({'name':name,'pass':bool(v)});print(name,bool(v),flush=True)
 try:
  for _ in range(50):
   try:Player();break
   except RuntimeError:time.sleep(.2)
  time.sleep(2);p=Player();check('1920x1080',p.width==1920 and p.height==1080)
  for name,x in [('Machine data',100),('Digital twin',275),('Combined',445),('Inspection',615),('Failure review',785),('Debug',955),('Examples',1135)]:
   click(x,94);check('Navigation '+name,audit()['view']==name)
   if name not in ['Failure review','Examples']:shot('after-'+name.lower().replace(' ','-'))
  for name,x in [('LAGER',1600),('IPA',1710),('STOUT',1820)]:
   click(x,131);check('Product '+name,audit()['product']==name)
  click(1600,131);click(445,94);time.sleep(3)
  s=state();rows=s['results'];check('Three crops / same bottle and capture',len(rows)==3 and len({r['bottle_id'] for r in rows})==1 and len({r['capture_utc'] for r in rows})==1 and len({r['frame_id'] for r in rows})==3)
  click(1570,688);check('Compact crop opens detailed evidence',audit()['view']=='Failure review');shot('after-evidence-review')
  click(445,94);click(95,131);a=audit();time.sleep(.8);b=audit();check('Pause preserves process clock',a['paused'] and a['sim_time']==b['sim_time']);shot('after-paused')
  click(95,131);old=audit()['session_id'];click(238,131);check('Reset creates new session',audit()['session_id']!=old)
  check('Recorded evidence survives reset',any(r['session_id']==old for r in state()['events']))
  click(1135,94);click(280,300);click(445,94);click(383,131);shot('after-combined')
  click(1680,94);check('CPU selected',state()['selected_device']=='cpu');check('No new language calls',state()['explanation_calls']==calls)
 finally:
  (OUT/'native-checks.json').write_text(json.dumps({'checks':checks,'qwen_calls_before':calls,'qwen_calls_after':state()['explanation_calls'],'scope':'UI smoke check; no training, locked evaluation or benchmark'},indent=2))
 if not all(c['pass'] for c in checks):raise SystemExit(1)
if __name__=='__main__':main()
