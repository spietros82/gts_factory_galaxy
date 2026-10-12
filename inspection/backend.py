"""Pixels-only backends; association/localisation and decision policy are separate."""
from dataclasses import dataclass,asdict
from typing import Protocol
from io import BytesIO
from pathlib import Path
import hashlib,json,time
import numpy as np
from PIL import Image,ImageFilter

CLASSES=['aligned','missing','displaced','uncertain']
WORDING={'aligned':'Cap visually present/aligned','missing':'Cap visually missing','displaced':'Cap visually displaced','uncertain':'Unable to assess'}
@dataclass(frozen=True)
class Assessment:
 label:str
 score:float
 backend:str
 reason:str

class InspectionBackend(Protocol):
 def assess(self,crop:Image.Image)->Assessment:...

def features(image):
 a=np.asarray(image.convert('RGB').resize((24,24),Image.Resampling.BILINEAR),dtype=np.float32)/255
 gray=a.mean(axis=2);dx=np.diff(gray,axis=1,prepend=gray[:,:1]);dy=np.diff(gray,axis=0,prepend=gray[:1,:])
 # Spatial color and edges preserve visual tilt/offset; no IDs, labels or metadata.
 return np.concatenate([a.flatten(),dx.flatten(),dy.flatten()])

def quality(image):
 a=np.asarray(image.convert('RGB'),dtype=np.float32)/255;gray=a.mean(axis=2)
 return {'mean':float(gray.mean()),'contrast':float(gray.std()),'detail':float(np.abs(np.diff(gray,axis=1)).mean()+np.abs(np.diff(gray,axis=0)).mean())}

def localize(frame:Image.Image,roi):
 if not isinstance(roi,list) or len(roi)!=4 or any(type(v)!=int for v in roi):raise ValueError('Four integer ROI coordinates required')
 x,y,w,h=roi
 if w<1 or h<1 or x<0 or y<0 or x+w>frame.width or y+h>frame.height:raise ValueError('ROI outside frame')
 return frame.crop((x,y,x+w,y+h))

class ClassicalBackend:
 name='non-learned cyan/geometry baseline / CPU'
 def __init__(self,policy):self.policy=policy
 def assess(self,crop):
  a=np.asarray(crop.convert('RGB').resize((96,96)),dtype=np.float32)/255
  # Synthetic cyan cap against the bottle neck; conventional color heuristic, not AI.
  mask=(a[:,:,2]>.22)&(a[:,:,1]>.18)&(a[:,:,0]<a[:,:,1]*.40)
  mask[60:]=False; ys,xs=np.nonzero(mask)
  if len(xs)<self.policy.get('baseline_pixels',100):return Assessment('missing',1,self.name,'No cyan cap pattern in expected upper neck region')
  cx=float(xs.mean()/96);spread=float(np.std(ys)/96)
  label='displaced' if abs(cx-.5)>self.policy.get('baseline_offset',.07) or spread>self.policy.get('baseline_spread',.10) else 'aligned'
  return Assessment(label,1,self.name,'Conventional color-region centroid/vertical spread; synthetic material dependent')

class LearnedBackend:
 name='supervised random forest v1 / CPU'
 def __init__(self,path,policy):
  import joblib
  # Trusted project artifact only. Do not accept uploaded pickle/joblib models.
  p=Path(path);expected=policy['model_sha256']
  if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise ValueError('Frozen model hash mismatch')
  self.model=joblib.load(p)
 def assess(self,crop):
  scores=self.model.predict_proba(features(crop)[None])[0];index=int(np.argmax(scores));label=str(self.model.classes_[index])
  return Assessment(label,float(scores[index]),self.name,'Image-grid/edge features classified by trained forest; score uncalibrated')

class DecisionPolicy:
 def __init__(self,config):self.config=config
 def decide(self,backend,crop,metadata,now):
  reasons=[]
  if metadata.get('association')!='simulator-assisted' or metadata.get('target_count')!=1:reasons.append('Ambiguous or unverified target association')
  if metadata.get('observations_available') is not True:reasons.append('Required observation/trigger quality missing')
  age=now-metadata['capture_epoch']
  if age<-.1 or age>self.config.get('max_age_seconds',2):reasons.append('Stale or invalid frame timestamp')
  if min(crop.size)<32:reasons.append('Target crop undersampled (<32 pixels)')
  q=quality(crop)
  if q['mean']<self.config.get('min_mean',.06):reasons.append('Underexposed target image')
  if q['contrast']<self.config.get('min_contrast',.025) or q['detail']<self.config.get('min_detail',.004):reasons.append('Insufficient target detail/contrast')
  if reasons:return Assessment('uncertain',0,getattr(backend,'name','unavailable'),'; '.join(reasons))
  a=backend.assess(crop)
  if a.score<self.config.get('threshold',.6):return Assessment('uncertain',a.score,a.backend,'Classifier score below validation-selected abstention threshold')
  return a
