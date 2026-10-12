"""One bounded training run; thresholds selected ONLY on validation."""
from pathlib import Path
import json,time,hashlib,itertools
import numpy as np
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
import joblib
from .backend import features,quality,LearnedBackend,ClassicalBackend,DecisionPolicy,CLASSES
ROOT=Path('inspection/dataset')

def metadata(row):return {'association':'simulator-assisted','target_count':1,'observations_available':True,'capture_epoch':0}
def predictions(backend,policy,rows):
 return [DecisionPolicy(policy).decide(backend,Image.open(ROOT/'crops'/(r['id']+'.png')),metadata(r),0).label for r in rows]
def objective(rows,pred):
 critical=sum(r['label']=='missing' and p=='aligned' for r,p in zip(rows,pred))
 poor=sum(r['label']=='uncertain' and p!='uncertain' for r,p in zip(rows,pred))
 correct=sum(r['label']!='uncertain' and r['label']==p for r,p in zip(rows,pred))
 return (critical,poor,-correct)

def main():
 models=Path('inspection/models');models.mkdir(exist_ok=True)
 if (models/'cap-rf.joblib').exists():raise SystemExit('Training already performed; preserve candidate')
 train=json.loads((ROOT/'train.json').read_text());val=json.loads((ROOT/'validation.json').read_text())
 t=time.perf_counter();X=np.array([features(Image.open(ROOT/'crops'/(r['id']+'.png'))) for r in train]);y=[r['label'] for r in train]
 model=RandomForestClassifier(n_estimators=128,max_depth=12,min_samples_leaf=2,class_weight='balanced',random_state=42,n_jobs=2)
 model.fit(X,y);duration=time.perf_counter()-t
 if duration>1800:raise RuntimeError('Training time budget exceeded; do not continue')
 joblib.dump(model,models/'cap-rf.joblib',compress=3)
 sha=hashlib.sha256((models/'cap-rf.joblib').read_bytes()).hexdigest()
 common={'min_mean':.06,'min_contrast':.025,'min_detail':.004,'max_age_seconds':2,'model_sha256':sha}
 backend=LearnedBackend(models/'cap-rf.joblib',common)
 records=[]
 for threshold in [.5,.6,.7,.8,.9]:
  policy={**common,'threshold':threshold};pred=predictions(backend,policy,val);records.append({'threshold':threshold,'objective':objective(val,pred),'predictions':pred})
 selected=min(records,key=lambda r:(r['objective'],r['threshold']));policy={**common,'threshold':selected['threshold']}
 # Conventional baseline thresholds selected on validation only, separate from learned decision.
 baseline_trials=[]
 for offset,spread,pixels in itertools.product([.04,.07,.10],[.06,.10,.14],[50,100,160]):
  cfg={**common,'threshold':0,'baseline_offset':offset,'baseline_spread':spread,'baseline_pixels':pixels}
  pred=predictions(ClassicalBackend(cfg),cfg,val)
  baseline_trials.append({'config':cfg,'objective':objective(val,pred)})
 baseline=min(baseline_trials,key=lambda r:r['objective'])['config']
 (models/'policy.json').write_text(json.dumps(policy,indent=2));(models/'baseline-policy.json').write_text(json.dumps(baseline,indent=2))
 freeze={'version':'cap-rf/1','model_sha256':sha,'model_bytes':(models/'cap-rf.joblib').stat().st_size,'training_seconds':duration,
 'training_rows':len(train),'validation_rows':len(val),'classes':list(model.classes_),'parameters':model.get_params(),
 'feature_contract':'24x24 RGB and grayscale dx/dy; no metadata','backend':'CPU / sklearn forest','download_bytes':0,
 'weight_provenance':'locally trained from synthetic procedural Unity images; no third-party/pretrained weights',
 'licence':'project-generated artifact; redistribution rights require project-owner confirmation; sklearn BSD-3-Clause does not itself license project assets',
 'policy_sha256':hashlib.sha256((models/'policy.json').read_bytes()).hexdigest(),'baseline_policy_sha256':hashlib.sha256((models/'baseline-policy.json').read_bytes()).hexdigest(),
 'validation_thresholds':records,'selected':selected,'locked_test_read':False}
 Path('reports/inspection/training.json').write_text(json.dumps(freeze,indent=2,default=str));print({k:freeze[k] for k in ['training_seconds','model_bytes','model_sha256','backend']});print('threshold',selected['threshold'],'validation objective',selected['objective'])
if __name__=='__main__':main()
