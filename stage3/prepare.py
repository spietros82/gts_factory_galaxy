"""Plan groups before capture; truth belongs only in dataset/evaluator files."""
import json,random,uuid,hashlib
from pathlib import Path
ROOT=Path('stage3/dataset');
if (ROOT/'capture-plan.json').exists():raise RuntimeError('Capture plan exists; preserve frozen dataset, do not overwrite')
ROOT.mkdir(parents=True,exist_ok=True)
rng=random.Random(3042);items=[];groups=[]
for product in ['LAGER','IPA','STOUT']:
 order=list(range(20));rng.shuffle(order)
 for number in range(20):
  split='train' if number in order[:12] else 'validation' if number in order[12:16] else 'test'
  group=f'{product}-{number}';base={'group':group,'split':split,'product':product,'seed':3042+len(groups),'light':rng.uniform(.8,1.25),'camera_x':rng.uniform(-.012,.012),'camera_y':rng.uniform(-.012,.012),'rotation':rng.uniform(-5,5)};groups.append(base)
  for condition in range(4):
   for adjacent in range(2):
    items.append(dict(base,id=uuid.uuid5(uuid.NAMESPACE_DNS,group+str(condition)+str(adjacent)).hex,condition=condition,cap_condition=condition,fill_condition=(condition+number)%4,label_condition=(condition+number//4)%4,adjacent=adjacent,fill=(rng.uniform(.94,1.00) if (condition+number)%4==0 else rng.uniform(.81,.87) if (condition+number)%4==1 else rng.uniform(1.10,1.17)),offset=rng.uniform(.065,.09),tilt=rng.uniform(17,25),quality_mode=number%3))
plan={'version':'brewery-three-station-data/1','groups':groups,'items':items};p=ROOT/'capture-plan.json';p.write_text(json.dumps(plan,indent=2));(ROOT/'split-freeze.json').write_text(json.dumps({'plan_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'groups':groups,'total_crops':len(items)*3},indent=2));print(len(items)*3)
