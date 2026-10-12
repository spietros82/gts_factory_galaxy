"""Actual XWayland input for this player's window only; screenshots use Unity F12."""
import ctypes as C,ctypes.util,json,sys,time
x=C.CDLL(ctypes.util.find_library('X11'));t=C.CDLL(ctypes.util.find_library('Xtst'))
D=C.c_void_p;U=C.c_ulong
x.XOpenDisplay.argtypes=[C.c_char_p];x.XOpenDisplay.restype=D
x.XDefaultRootWindow.argtypes=[D];x.XDefaultRootWindow.restype=U
x.XQueryTree.argtypes=[D,U,C.POINTER(U),C.POINTER(U),C.POINTER(C.POINTER(U)),C.POINTER(C.c_uint)]
x.XFetchName.argtypes=[D,U,C.POINTER(C.c_char_p)];x.XFree.argtypes=[D]
x.XGetGeometry.argtypes=[D,U,C.POINTER(U),C.POINTER(C.c_int),C.POINTER(C.c_int),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint)]
x.XTranslateCoordinates.argtypes=[D,U,U,C.c_int,C.c_int,C.POINTER(C.c_int),C.POINTER(C.c_int),C.POINTER(U)]
x.XMoveWindow.argtypes=[D,U,C.c_int,C.c_int];x.XRaiseWindow.argtypes=[D,U];x.XSetInputFocus.argtypes=[D,U,C.c_int,U];x.XFlush.argtypes=[D]
x.XStringToKeysym.argtypes=[C.c_char_p];x.XStringToKeysym.restype=U;x.XKeysymToKeycode.argtypes=[D,U];x.XKeysymToKeycode.restype=C.c_uint
for name,args in [('XTestFakeKeyEvent',[D,C.c_uint,C.c_int,U]),('XTestFakeButtonEvent',[D,C.c_uint,C.c_int,U]),('XTestFakeMotionEvent',[D,C.c_int,C.c_int,C.c_int,U])]:getattr(t,name).argtypes=args
class Player:
 def __init__(self):
  self.d=x.XOpenDisplay(None)
  if not self.d:raise RuntimeError('X11 display unavailable')
  self.root=x.XDefaultRootWindow(self.d);self.window=self.find(self.root)
  if not self.window:raise RuntimeError('Factory Galaxy graphical window not found')
  root=U();px=C.c_int();py=C.c_int();w=C.c_uint();h=C.c_uint();b=C.c_uint();depth=C.c_uint()
  x.XGetGeometry(self.d,self.window,C.byref(root),C.byref(px),C.byref(py),C.byref(w),C.byref(h),C.byref(b),C.byref(depth));self.width=w.value;self.height=h.value
  xx=C.c_int();yy=C.c_int();child=U();x.XTranslateCoordinates(self.d,self.window,self.root,0,0,C.byref(xx),C.byref(yy),C.byref(child));self.left=xx.value;self.top=yy.value
  x.XRaiseWindow(self.d,self.window);x.XSetInputFocus(self.d,self.window,1,0);x.XFlush(self.d)
 def find(self,window):
  title=C.c_char_p();x.XFetchName(self.d,window,C.byref(title));name=title.value.decode(errors='replace') if title.value else ''
  rr=U();parent=U();children=C.POINTER(U)();count=C.c_uint()
  if x.XQueryTree(self.d,window,C.byref(rr),C.byref(parent),C.byref(children),C.byref(count)):
   ids=[children[i] for i in range(count.value)];x.XFree(children)
   for item in ids:
    found=self.find(item)
    if found:return found
  return window if 'Factory Galaxy' in name else None
 def center(self):
  x.XMoveWindow(self.d,self.window,80,80);x.XFlush(self.d);time.sleep(.4)
  refreshed=Player();self.left=refreshed.left;self.top=refreshed.top
  return {"left":self.left,"top":self.top,"width":self.width,"height":self.height}
 def key(self,name):
  code=x.XKeysymToKeycode(self.d,x.XStringToKeysym(name.encode()));t.XTestFakeKeyEvent(self.d,code,1,0);x.XFlush(self.d);time.sleep(.12);t.XTestFakeKeyEvent(self.d,code,0,0);x.XFlush(self.d)
 def click(self,px,py,button=1):
  t.XTestFakeMotionEvent(self.d,-1,self.left+int(px*self.width/1600),self.top+int(py*self.height/900),0)
  t.XTestFakeButtonEvent(self.d,button,1,0);x.XFlush(self.d);time.sleep(.12);t.XTestFakeButtonEvent(self.d,button,0,0);x.XFlush(self.d)
 def scroll(self,down=True,steps=8):
  for _ in range(steps):self.click(1450,700,5 if down else 4);time.sleep(.03)
if __name__=='__main__':
 p=Player();print(json.dumps({'xid':p.window,'width':p.width,'height':p.height,'left':p.left,'top':p.top}))
 if len(sys.argv)>1:
  if sys.argv[1]=='key':p.key(sys.argv[2])
  if sys.argv[1]=='click':p.click(int(sys.argv[2]),int(sys.argv[3]))
  if sys.argv[1]=='scroll':p.scroll(sys.argv[2]!='up')
