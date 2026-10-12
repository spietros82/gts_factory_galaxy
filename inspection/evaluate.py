"""One-shot locked test. Immutable candidate policy; evaluation cannot train or tune."""
from pathlib import Path
import json,hashlib,time,math
from PIL import Image
from .backend import LearnedBackend,ClassicalBackend,DecisionPolicy,CLASSES,WORDING

def wilson(k,n):
 if not n:return None
 z=1.96;p=k/n;den=1+z*z/n;center=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return [center-half,center+half]
def score(rows,pred):
 confusion={c:{d:0 for d in CLASSES} for c in CLASSES}
 for r,p in zip(rows,pred):confusion[r['label']][p]+=1
 per={}
 for c in CLASSES:
  n=sum(confusion[c].values());accepted=sum(confusion[g][c] for g in CLASSES);tp=confusion[c][c]
  per[c]={'sample_count':n,'precision':tp/accepted if accepted else None,'recall':tp/n if n else None,'precision_wilson95':wilson(tp,accepted),'recall_wilson95':wilson(tp,n),
   'abstentions':confusion[c]['uncertain'],'coverage':(n-confusion[c]['uncertain'])/n if n else None}
 n=sum(sum(confusion[c].values()) for c in CLASSES if c!='uncertain');accepted=sum(sum(confusion[c][d] for d in CLASSES if d!='uncertain') for c in CLASSES if c!='uncertain')
 critical=confusion['missing']['aligned'];poor=sum(confusion['uncertain'][c] for c in CLASSES if c!='uncertain');coverage=accepted/n
 targets={'zero_missing_accepted_aligned':critical==0,'precision_recall_95':all(per[c]['precision'] is not None and per[c]['precision']>=.95 and per[c]['recall']>=.95 for c in CLASSES if c!='uncertain'),'decidable_coverage_90':coverage>=.9,'zero_poor_quality_accepted':poor==0}
 return {'confusion':confusion,'per_class':per,'critical_false_accepts':critical,'missing_count':per['missing']['sample_count'],'critical_rate_wilson95':wilson(critical,per['missing']['sample_count']),
 'poor_quality_accepted':poor,'decidable_coverage':coverage,'targets':targets,'all_targets_pass':all(targets.values()),'limits':'sample-level intervals; four adjacent captures/group correlated; synthetic only; zero observed error does not establish zero risk'}

def main():
 out=Path('reports/inspection/locked-evaluation.json');marker=out.with_suffix('.started')
 with marker.open('x') as f:f.write('Locked evaluation started; no automatic rerun even after failure\n')
 root=Path('inspection/dataset');models=Path('inspection/models');freeze=json.loads(Path('reports/inspection/training.json').read_text())
 for name,key in [('policy.json','policy_sha256'),('baseline-policy.json','baseline_policy_sha256')]:assert hashlib.sha256((models/name).read_bytes()).hexdigest()==freeze[key]
 expected=json.loads((root/'hashes.json').read_text())['test.json'];assert hashlib.sha256((root/'test.json').read_bytes()).hexdigest()==expected
 rows=json.loads((root/'test.json').read_text());allresults={}
 for name,backend,policy in [('learned',LearnedBackend(models/'cap-rf.joblib',json.loads((models/'policy.json').read_text())),json.loads((models/'policy.json').read_text())),('classical',ClassicalBackend(json.loads((models/'baseline-policy.json').read_text())),json.loads((models/'baseline-policy.json').read_text()))]:
  predictions=[];raw=[]
  for row in rows:
   p=root/'crops'/(row['id']+'.png');assert hashlib.sha256(p.read_bytes()).hexdigest()==row['crop_sha256'];image=Image.open(p);t=time.perf_counter()
   result=DecisionPolicy(policy).decide(backend,image,{'association':'simulator-assisted','target_count':1,'observations_available':True,'capture_epoch':0},0);elapsed=time.perf_counter()-t
   predictions.append(result.label);raw.append({'id':row['id'],'group':row['group'],'truth':row['label'],'prediction':result.label,'score':result.score,'reason':result.reason,'seconds':elapsed})
  allresults[name]={'metrics':score(rows,predictions),'raw':raw,'policy_sha256':hashlib.sha256(json.dumps(policy,sort_keys=True).encode()).hexdigest()}
 out.write_text(json.dumps({'version':'focused-eval/1','test_manifest_sha256':expected,'training_model_sha256':freeze['model_sha256'],'runs':allresults,'once_only':True},indent=2))
 for name,r in allresults.items():print(name,json.dumps(r['metrics']))
if __name__=='__main__':main()
