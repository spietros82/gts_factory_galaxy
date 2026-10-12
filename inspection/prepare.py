"""Prepare neutral capture IDs and sequence splits BEFORE acquisition."""
import json,random,uuid,hashlib
from pathlib import Path

def main():
 root=Path('inspection/dataset');root.mkdir(parents=True,exist_ok=True)
 if (root/'capture-plan.json').exists():raise SystemExit('Plan already exists; preserve it')
 items=[]
 for group in range(60):
  rng=random.Random(7000+group)
  setting={'group':f'G{group:03d}','seed':7000+group,'split':'train' if group<36 else 'validation' if group<48 else 'test',
  'light':rng.uniform(.8,1.6),'ambient':rng.uniform(.3,.55),'camera_x':rng.uniform(-.035,.035),'camera_y':rng.uniform(-.035,.035),
  'position_x':rng.uniform(2.95,3.05),'rotation':rng.uniform(-8,8),'cap_color':rng.uniform(.65,.90)}
  for cls in range(4):
   underlying=cls if cls<3 else group%3
   for adjacent in range(4):
    ident=uuid.uuid5(uuid.NAMESPACE_OID,f'factory-focused-v1-{group}-{cls}-{adjacent}').hex
    row={**setting,'id':ident,'sequence':f'S{group:03d}-{cls}','adjacent':adjacent,'label':['aligned','missing','displaced','uncertain'][cls],
      'cap_present':underlying!=1,'cap_displaced':underlying==2,'offset':rng.uniform(.065,.09) if underlying==2 else rng.uniform(-.006,.006),
      'tilt':rng.uniform(15,22) if underlying==2 else rng.uniform(-2,2),'quality_mode':group%4 if cls==3 else -1}
    items.append(row)
 (root/'capture-plan.json').write_text(json.dumps({'version':'synthetic-cap-data/1','items':items},indent=2))
 splits={s:[r['id'] for r in items if r['split']==s] for s in ['train','validation','test']}
 (root/'splits.json').write_text(json.dumps(splits,indent=2))
 (root/'split-freeze.json').write_text(json.dumps({'sha256':hashlib.sha256((root/'splits.json').read_bytes()).hexdigest(),'counts':{k:len(v) for k,v in splits.items()},'group_unit':'all classes and adjacent frames sharing appearance/seed'},indent=2))
 print({k:len(v) for k,v in splits.items()})
if __name__=='__main__':main()
