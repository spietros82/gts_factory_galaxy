"""Postprocess declared synthetic quality variation, crop, hash and review development data."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageFilter,ImageEnhance,ImageDraw
from .backend import localize

def finalize():
 root=Path('inspection/dataset');plan=json.loads((root/'capture-plan.json').read_text())['items'];meta={r['frame_id']:r for r in map(json.loads,(root/'acquisition.jsonl').read_text().splitlines())}
 (root/'crops').mkdir(exist_ok=True);rows=[]
 for row in plan:
  p=root/'frames'/(row['id']+'.png');image=Image.open(p).convert('RGB');mode=row['quality_mode']
  # Declared image-quality transformations; original rendered image retained for provenance.
  if mode in [1,2,3]:
   original=root/'render-originals';original.mkdir(exist_ok=True);(original/p.name).write_bytes(p.read_bytes())
   if mode==1:image=image.filter(ImageFilter.GaussianBlur(14))
   elif mode==2:image=ImageEnhance.Brightness(image).enhance(.05)
   else:image=image.resize((16,12),Image.Resampling.BILINEAR).resize((512,384),Image.Resampling.NEAREST)
   image.save(p)
  roi=meta[row['id']]['roi'];crop=localize(image,roi);cp=root/'crops'/p.name;crop.save(cp)
  rows.append({**row,'roi':roi,'frame_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'crop_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'capture_utc':meta[row['id']]['capture_utc']})
 (root/'manifest.json').write_text(json.dumps({'version':'synthetic-cap-data/1','rows':rows},indent=2))
 for split in ['train','validation','test']:
  selected=[r for r in rows if r['split']==split];p=root/(split+'.json');p.write_text(json.dumps(selected,indent=2))
 hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.json')}
 (root/'hashes.json').write_text(json.dumps(hashes,indent=2))
 # Manual pretraining review sheet ONLY train and validation; never locked test.
 sheets=[]
 for split in ['train','validation']:
  selected=[]
  for label in ['aligned','missing','displaced','uncertain']:
   pool=[r for r in rows if r['split']==split and r['label']==label]
   selected.extend([pool[i] for i in [0,5,9,16]])
  sheet=Image.new('RGB',(4*240,4*210),(25,30,40));draw=ImageDraw.Draw(sheet)
  for i,r in enumerate(selected):
   image=Image.open(root/'crops'/(r['id']+'.png'));image.thumbnail((230,170));x=i%4*240;y=i//4*210
   sheet.paste(image,(x,y));draw.text((x+4,y+174),r['label']+' '+r['id'][:8],fill='white');draw.text((x+4,y+188),'quality '+str(r['quality_mode']),fill='white')
  out=Path('reports/inspection')/(split+'-label-review.png');sheet.save(out);sheets.append(str(out))
 print({'images':len(rows),'class_balance':{s:{c:sum(r['split']==s and r['label']==c for r in rows) for c in ['aligned','missing','displaced','uncertain']} for s in ['train','validation','test']},'review_sheets':sheets})
if __name__=='__main__':finalize()
