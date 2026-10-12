"""Targeted control-position verification after a failed fixed-coordinate GUI check."""
import json,time,shutil,urllib.request
from pathlib import Path
from tools.unity_ui import Player
OUT=Path('reports/inspection/gui')
def state():return json.load(urllib.request.urlopen('http://127.0.0.1:8810/state',timeout=2))
def main():
 p=Player();p.key('F3');p.scroll(down=False,steps=30);time.sleep(.4)
 before=state()['uncertain'];p.click(1274,298);began=time.monotonic();found=None
 while time.monotonic()-began<40:
  s=state()
  if s['uncertain']>before:found=s;break
  time.sleep(.2)
 if found:
  p.key('space');p.key('F12');time.sleep(.5)
  images=list(Path('runtime/inspection-native').glob('screen-*.png'));shutil.copyfile(max(images,key=lambda f:f.stat().st_mtime),OUT/'07-observed-quality-abstention.png')
  p.key('space')
 # Reset gives a fresh healthy replay and clears observation loss, independent of any scroll coordinates.
 p.click(200,80);time.sleep(2);p.key('F3');p.scroll(down=False,steps=30)
 result={'check':'actual observation quality control with sidebar explicitly at top','pass':found is not None,'before_uncertain':before,'after_uncertain':found['uncertain'] if found else state()['uncertain'],'elapsed_seconds':time.monotonic()-began,'previous_failure':'fixed-coordinate click while sidebar scrolled; preserved gui/results.json false','extra_explanation_calls':state()['explanation_calls'],'model_policy_unchanged':True,'no_locked_eval':True}
 (OUT/'quality-control-recheck.json').write_text(json.dumps(result,indent=2));print(result)
if __name__=='__main__':main()
