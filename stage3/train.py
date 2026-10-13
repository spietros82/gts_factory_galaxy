"""One candidate, train/validation only. Never reads test rows/crops."""
import json,time,hashlib,warnings
from pathlib import Path
import numpy as np
from PIL import Image
from sklearn.neural_network import MLPClassifier
from stage3.backend import features,STATIONS,LABELS
ROOT=Path('stage3/dataset');OUT=Path('stage3/models');
if (OUT/'policy.json').exists():raise RuntimeError('Frozen models already exist; no automatic retraining')
OUT.mkdir(exist_ok=True)
train=json.loads((ROOT/'train.json').read_text());val=json.loads((ROOT/'validation.json').read_text());started=time.perf_counter();report={};hashes={};thresholds={}
for station in STATIONS:
 rows=[r for r in train if r['station']==station];X=np.stack([features(Image.open(ROOT/'crops'/(r['id']+'.png'))) for r in rows]);y=np.array([LABELS[station].index(r['label']) for r in rows]);s=time.perf_counter()
 model=MLPClassifier(hidden_layer_sizes=(48,),activation='relu',solver='adam',alpha=.002,batch_size=48,learning_rate_init=.002,max_iter=200,random_state=42,tol=.0001,n_iter_no_change=20)
 with warnings.catch_warnings(record=True) as captured:model.fit(X,y)
 if time.perf_counter()-started>1800:raise RuntimeError('Training time budget exceeded')
 path=OUT/(station+'.npz');np.savez(path,w0=model.coefs_[0].astype('f4'),b0=model.intercepts_[0].astype('f4'),w1=model.coefs_[1].astype('f4'),b1=model.intercepts_[1].astype('f4'));hashes[station]=hashlib.sha256(path.read_bytes()).hexdigest()
 rows=[r for r in val if r['station']==station];scores=model.predict_proba(np.stack([features(Image.open(ROOT/'crops'/(r['id']+'.png'))) for r in rows]));truth=np.array([LABELS[station].index(r['label']) for r in rows]);options=[]
 for threshold in [.5,.65,.8]:
  p=scores.argmax(1);p[scores.max(1)<threshold]=3;coverage=float(((p!=3)&(truth!=3)).sum()/max(1,(truth!=3).sum()));accuracy=float((p==truth).sum()/len(truth));options.append({'threshold':threshold,'accuracy':accuracy,'decidable_coverage':coverage})
 valid=[x for x in options if x['decidable_coverage']>=.75];selected=max(valid or options,key=lambda x:(x['accuracy'],x['threshold']));thresholds[station]=selected['threshold'];report[station]={'training_seconds':time.perf_counter()-s,'iterations':model.n_iter_,'warnings':[str(w.message) for w in captured],'validation_options':options,'selected':selected};print(station,report[station],flush=True)
policy={'version':'brewery-mlp48/1','preprocessing':'RGB24x24-bilinear-float32/255','thresholds':thresholds,'hashes':hashes,'seed':42,'labels':LABELS};(OUT/'policy.json').write_text(json.dumps(policy,indent=2));report['total_training_wall_seconds']=time.perf_counter()-started;Path('reports/stage3/training.json').write_text(json.dumps(report,indent=2))
