"""Native regression for retained panel pixels outside the resized 3D viewport.

Requires this player's --telemetry-audit true QA flag, existing Pillow/X11.
No model calls, image accuracy evaluation or hardware changes.
"""
import json
import shutil
import time
from pathlib import Path
from PIL import Image
from tools.unity_ui import Player

ROOT = Path.cwd()
RUNTIME = ROOT / 'runtime/stage2-native'
OUT = ROOT / 'reports/stage2/display-fix'

def wait_mode(mode):
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        state = json.loads((RUNTIME / 'telemetry-audit.json').read_text())
        if state['mode'] == mode:
            return state
        time.sleep(.1)
    raise AssertionError('Mode did not change: ' + mode)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    player = Player()
    time.sleep(2)
    checks = []
    for index, (key, mode) in enumerate([('1','data'),('2','twin'),('3','combined'),('2','twin'),('1','data'),('3','combined')]):
        player.key(key)
        wait_mode(mode)
        time.sleep(.6)
        old = set(RUNTIME.glob('screen-*.png'))
        player.key('F12')
        deadline = time.monotonic() + 6
        while time.monotonic() < deadline:
            new = set(RUNTIME.glob('screen-*.png')) - old
            if new:
                image = max(new, key=lambda p:p.stat().st_mtime)
                try:
                    im = Image.open(image).convert('RGB')
                    break
                except OSError:
                    pass
            time.sleep(.1)
        else:
            raise AssertionError('Native screenshot not saved')
        dest = OUT / f'after-{player.width}-{index}-{mode}.png'
        shutil.copyfile(image, dest)
        # These strips previously contained old table text/buttons after switching
        # Combined -> Twin. They must be opaque and uniform, not merely dark.
        scale = max(.7, player.width / 1600)
        regions = [('header margin', (0,0,12*scale,230*scale))]
        if mode != 'data':
            edge = player.width * (.63 if mode == 'combined' else .77)
            left = player.width*.63 + 8*scale if mode=='combined' else player.width-355*scale
            regions.append(('viewport-panel gap',(edge+2*scale,260*scale,left-2*scale,player.height-80*scale)))
        for name, region in regions:
            crop = im.crop(tuple(round(v) for v in region))
            colors = crop.getcolors(crop.width*crop.height)
            passed = len(colors)==1 and max(colors[0][1]) < 30
            checks.append({'mode':mode,'region':name,'pass':passed,'unique_colors':len(colors),'screenshot':dest.name})
            if not passed:
                raise AssertionError((mode,name,len(colors)))
        print(mode,'clean margins',flush=True)
        time.sleep(.5)
    (OUT / f'margins-{player.width}.json').write_text(json.dumps({'resolution':[player.width,player.height],'checks':checks},indent=2))

if __name__ == '__main__':
    main()
