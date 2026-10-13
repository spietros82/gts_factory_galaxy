"""Exactly one locked evaluation/device. Development comparisons use validation only."""
import json,math,time,hashlib
from pathlib import Path
from PIL import Image
from stage3.backend import NeuralBackend,STATIONS,LABELS
ROOT=Path('stage3/dataset');OUT=Path('reports/stage3')
def wilson(k,n):
 if not n:return None
 z=1.96;p=k/n;c=(p+z*z/(2*n))/(1+z*z/n);d=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n);return [max(0,c-d),min(1,c+d)]
def evaluate(device):
 marker=OUT/('locked-'+device+'-started.json')
 if marker.exists():raise RuntimeError('Locked evaluation already attempted: '+device)
 policy=Path('stage3/models/policy.json');marker.write_text(json.dumps({'started_epoch':time.time(),'policy_sha256':hashlib.sha256(policy.read_bytes()).hexdigest(),'test_manifest_sha256':hashlib.sha256((ROOT/'test.json').read_bytes()).hexdigest()}))
 backend=NeuralBackend(device=device);rows=json.loads((ROOT/'test.json').read_text());records=[];report={}
 for station in STATIONS:
  matrix=[[0]*4 for _ in range(4)];products={p:[[0]*4 for _ in range(4)] for p in ['LAGER','IPA','STOUT']}
  for row in [r for r in rows if r['station']==station]:
   result=backend.predict(station,Image.open(ROOT/'crops'/(row['id']+'.png')));truth=LABELS[station].index(row['label']);prediction=LABELS[station].index(result['decision']);matrix[truth][prediction]+=1;products[row['product']][truth][prediction]+=1;records.append({'id':row['id'],'product':row['product'],'station':station,'truth':row['label'],**result})
  stats={}
  for index,label in enumerate(LABELS[station]):
   n=sum(matrix[index]);accepted=sum(r[index] for r in matrix);tp=matrix[index][index];stats[label]={'samples':n,'precision':tp/accepted if accepted else None,'recall':tp/n if n else None,'recall_wilson95':wilson(tp,n),'abstained':matrix[index][3]}
  decidable=sum(sum(r) for r in matrix[:3]);abstained=sum(r[3] for r in matrix[:3]);missed=sum(r[0] for r in matrix[1:3]);false_reject=sum(matrix[0][1:3]);poor_accept=sum(matrix[3][:3]);report[station]={'labels':LABELS[station],'confusion_matrix':matrix,'per_class':stats,'product_confusion_matrices':products,'decidable_coverage':(decidable-abstained)/decidable,'missed_defects_as_healthy':missed,'false_rejects_of_healthy':false_reject,'poor_quality_accepted':poor_accept,'critical_missing_cap_accepted_aligned':matrix[1][0] if station=='cap' else None,'critical_error_wilson95':wilson(matrix[1][0],sum(matrix[1])) if station=='cap' else None}
 report['device']=device;report['gpu_renderer']=getattr(backend,'renderer',None);report['records']=records;report['limitations']='Synthetic grouped sequences; adjacent frames correlated, sample Wilson intervals do not imply independence or real-camera reliability.'
 (OUT/('locked-'+device+'.json')).write_text(json.dumps(report,indent=2));print(json.dumps({s:{k:v for k,v in report[s].items() if k not in ['per_class','product_confusion_matrices']} for s in STATIONS},indent=2))
if __name__=='__main__':
 import sys;evaluate(sys.argv[1])
