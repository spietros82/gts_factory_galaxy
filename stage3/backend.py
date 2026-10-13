"""Same safe float32 neural weights and pixels-only preprocessing on CPU/GPU."""
import hashlib,json,time
from pathlib import Path
from typing import Protocol
import numpy as np
from PIL import Image
STATIONS=['cap','fill','label']
LABELS={'cap':['aligned','missing','displaced','uncertain'],'fill':['within_range','underfilled','overfilled','uncertain'],'label':['aligned','missing','misaligned','uncertain']}
WORDS={'cap':['Cap visually present/aligned','Cap visually missing','Cap visually displaced','Unable to assess cap'],'fill':['Visible liquid level within demo range','Visible liquid level below demo range','Visible liquid level above demo range','Unable to assess liquid level'],'label':['Label visually present/aligned','Label visually missing','Label visually misaligned','Unable to assess label']}
def features(image):return np.asarray(image.convert('RGB').resize((24,24),Image.Resampling.BILINEAR),dtype=np.float32).reshape(-1)/np.float32(255)
class InspectionBackend(Protocol):
 def predict(self,station:str,image:Image.Image)->dict:...
SHADER='''#version 430
layout(local_size_x=64) in;
layout(std430,binding=0) readonly buffer X{float x[];};
layout(std430,binding=1) readonly buffer W{float w[];};
layout(std430,binding=2) readonly buffer B{float b[];};
layout(std430,binding=3) writeonly buffer Y{float y[];};
uniform int inputs;uniform int outputs;uniform int relu;
void main(){uint j=gl_GlobalInvocationID.x;if(j>=uint(outputs))return;float s=b[j];for(int i=0;i<inputs;i++)s+=x[i]*w[i*outputs+j];y[j]=relu==1?max(0.0,s):s;}
'''
class NeuralBackend:
 def __init__(self,root='stage3/models',device='cpu'):
  start=time.perf_counter();self.device=device;self.root=Path(root);self.policy=json.loads((self.root/'policy.json').read_text());self.weights={};self.context=None
  for station in STATIONS:
   p=self.root/(station+'.npz')
   if hashlib.sha256(p.read_bytes()).hexdigest()!=self.policy['hashes'][station]:raise ValueError('Frozen weight hash mismatch')
   self.weights[station]=dict(np.load(p,allow_pickle=False))
  self.backend='MLP48-v1 / NumPy float32'
  if device=='gpu':
   import moderngl
   self.context=moderngl.create_standalone_context(require=430,backend='egl');renderer=self.context.info['GL_RENDERER']
   if 'Radeon' not in renderer or 'llvmpipe' in renderer.lower():raise RuntimeError('Hardware GPU not verified: '+renderer)
   self.renderer=renderer;self.backend='MLP48-v1 / OpenGL compute';self.shader=self.context.compute_shader(SHADER)
   self.buffers={}
   for station,w in self.weights.items():self.buffers[station]=[[self.context.buffer(w['w'+str(i)].astype('f4').tobytes()),self.context.buffer(w['b'+str(i)].astype('f4').tobytes())] for i in range(2)]
  self.cold_start_ms=(time.perf_counter()-start)*1000
 def predict(self,station,image):
  start=time.perf_counter();x=features(image);pre=(time.perf_counter()-start)*1000;transfer=0;gpu_ns=0;w=self.weights[station];infer=time.perf_counter()
  if self.device=='cpu':
   hidden=np.maximum(np.float32(0),x@w['w0']+w['b0']);logits=hidden@w['w1']+w['b1'];inference=(time.perf_counter()-infer)*1000
  else:
   c=self.context;t=time.perf_counter();inp=c.buffer(x.tobytes());hidden=c.buffer(reserve=48*4);out=c.buffer(reserve=4*4);transfer+=(time.perf_counter()-t)*1000
   with c.query(time=True) as query:
    for index,(a,b,dim,outputs) in enumerate([(inp,hidden,len(x),48),(hidden,out,48,4)]):
     a.bind_to_storage_buffer(0);self.buffers[station][index][0].bind_to_storage_buffer(1);self.buffers[station][index][1].bind_to_storage_buffer(2);b.bind_to_storage_buffer(3);self.shader['inputs']=dim;self.shader['outputs']=outputs;self.shader['relu']=int(index==0);self.shader.run(group_x=(outputs+63)//64);c.memory_barrier()
   t=time.perf_counter();logits=np.frombuffer(out.read(),dtype='f4').copy();transfer+=(time.perf_counter()-t)*1000;gpu_ns=query.elapsed;inference=(time.perf_counter()-infer)*1000-transfer
   inp.release();hidden.release();out.release()
  scores=np.exp(logits-logits.max());scores/=scores.sum();i=int(scores.argmax());decision=LABELS[station][i];reason='Learned appearance category; score is uncalibrated.'
  quality=np.asarray(image.convert('RGB'),dtype=np.float32)/255
  if min(image.size)<32 or quality.mean()<.06 or quality.std()<.015 or float(scores[i])<self.policy['thresholds'][station]:decision='uncertain';reason='Insufficient image quality or validation-selected abstention threshold.'
  return {'decision':decision,'wording':WORDS[station][LABELS[station].index(decision)],'score':float(scores[i]),'reason':reason,'device':self.device,'backend':self.backend,'model_sha256':self.policy['hashes'][station],'preprocess_ms':pre,'transfer_ms':transfer,'inference_ms':inference,'gpu_elapsed_ms':gpu_ns/1e6,'classifier_ms':(time.perf_counter()-start)*1000}
