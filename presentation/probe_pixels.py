"""Fresh unscored pixel compatibility captures; no model or held-out inputs."""
import hashlib,json,subprocess,shutil
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path.cwd();before=ROOT/'runtime/stage1/pixel-probe-before';rows=[]
original={r['frame_id']:r for r in map(json.loads,(before/'acquisition.jsonl').read_text().splitlines())}
for product in ['LAGER','IPA','STOUT']:
 out=ROOT/'runtime/stage1'/('pixel-final-'+product.lower());out.mkdir(exist_ok=False);shutil.copyfile(before/'capture-plan.json',out/'capture-plan.json')
 cmd=[str(ROOT/'builds/stage1/FactoryGalaxy.x86_64'),'-screen-fullscreen','0','-screen-width','1600','-screen-height','900','-logFile',str(out/'player.log'),'--focused-inspection','true','--profile','1','--inspection-dataset',str(out),'--data-path',str(out),'--frame-target','60','--presentation','true','--comparison-camera','true','--product',product,'--disable-explanations','true']
 with (out/'console.txt').open('w') as log:subprocess.run(cmd,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=20)
 acquired={r['frame_id']:r for r in map(json.loads,(out/'acquisition.jsonl').read_text().splitlines())}
 for path in sorted((before/'frames').glob('*.png')):
  a=np.array(Image.open(path).convert('RGB'));b=np.array(Image.open(out/'frames'/path.name).convert('RGB'));x,y,w,h=original[path.stem]['roi'];crop=a[y:y+h,x:x+w];other=b[y:y+h,x:x+w]
  rows.append({'product':product,'fixture':path.stem,'roi_identical':original[path.stem]['roi']==acquired[path.stem]['roi'],'full_frame_pixels_identical':bool(np.array_equal(a,b)),'crop_pixels_identical':bool(np.array_equal(crop,other)),'changed_crop_pixels':int(np.any(crop!=other,axis=2).sum()),'crop_pixel_sha256':hashlib.sha256(crop.tobytes()).hexdigest()})
result={'method':'Three fresh unscored positions × three product appearances, compared with preserved original standalone. Identical optics, pose, key/ambient settings and ROI. No held-out set and no classifier/LLM call.','all_pass':all(r['roi_identical'] and r['crop_pixels_identical'] and r['full_frame_pixels_identical'] for r in rows),'rows':rows,'limits':'Finite compatibility sample, not new accuracy evidence. Brewery presentation pixels are not classified and remain unvalidated.'}
(ROOT/'reports/stage1/inspection-compatibility-final.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
