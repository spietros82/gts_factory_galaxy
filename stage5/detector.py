"""Independent YOLO11 raw-head decoder; ncnn model inference is mixed Vulkan/CPU.
No simulation IDs, labels, crops or masks enter this interface.
"""
from pathlib import Path
import time, hashlib
import numpy as np
import ncnn
from PIL import Image

def drm_compute_ns():
    clients={}
    for p in Path('/proc/self/fdinfo').glob('*'):
        try:
            fields=dict(line.split(':',1) for line in p.read_text().splitlines() if ':' in line)
            if fields.get('drm-driver','').strip()!='amdgpu':continue
            cid=fields['drm-client-id'].strip()
            clients[cid]=int(fields.get('drm-engine-compute','0').split()[0])
        except (OSError,KeyError,ValueError):pass
    return sum(clients.values()) if clients else None

def iou(a,b):
    x=max(0,min(a[2],b[2])-max(a[0],b[0]));y=max(0,min(a[3],b[3])-max(a[1],b[1]))
    inter=x*y;union=(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-inter
    return inter/max(1e-9,union)

def decode(raw,size=640,confidence=.25,nms=.45):
    if raw.shape!=(sum((size//s)**2 for s in (8,16,32)),144) or not np.isfinite(raw).all():
        raise ValueError('Invalid detector output shape/values')
    proposals=[];offset=0
    for stride in (8,16,32):
        grid=size//stride;head=raw[offset:offset+grid*grid];offset+=grid*grid
        scores=1/(1+np.exp(-np.clip(head[:,64+39],-50,50)))
        # Keep bottle proposals only when bottle is the highest-scoring COCO class.
        indices=np.flatnonzero((scores>=confidence)&(head[:,64:].argmax(axis=1)==39))
        for idx in indices:
            logits=head[idx,:64].reshape(4,16);e=np.exp(logits-logits.max(axis=1,keepdims=True));dist=(e/e.sum(axis=1,keepdims=True)*np.arange(16)).sum(axis=1)*stride
            cx=(idx%grid+.5)*stride;cy=(idx//grid+.5)*stride
            box=[float(np.clip(cx-dist[0],0,size)),float(np.clip(cy-dist[1],0,size)),float(np.clip(cx+dist[2],0,size)),float(np.clip(cy+dist[3],0,size))]
            if box[2]<=box[0] or box[3]<=box[1]:continue
            proposals.append({'box':box,'score':float(scores[idx]),'class_name':'bottle'})
    proposals.sort(key=lambda d:-d['score']);out=[]
    for d in proposals:
        if all(iou(d['box'],p['box'])<=nms for p in out):out.append(d)
        if len(out)>=64:break
    return out

class Detector:
    def __init__(self,model_path='stage5/models',device='cpu',size=640,threads=4):
        if device not in ('cpu','gpu') or size!=640:raise ValueError('Supported: CPU/GPU FP32, 640 only')
        start=time.perf_counter();self.device=device;self.size=size;self.net=ncnn.Net();o=self.net.opt
        o.num_threads=threads;o.use_vulkan_compute=device=='gpu'
        o.use_fp16_packed=o.use_fp16_storage=o.use_fp16_arithmetic=False
        o.use_bf16_packed=o.use_bf16_storage=False;o.use_int8_inference=False
        self.gpu_name=None
        if device=='gpu':
            physical=[i for i in range(ncnn.get_gpu_count()) if 'Radeon' in ncnn.get_gpu_info(i).device_name()]
            if not physical:raise RuntimeError('No physical Radeon Vulkan device; CPU fallback prohibited')
            index=physical[0];self.gpu_name=ncnn.get_gpu_info(index).device_name();self.net.set_vulkan_device(index)
        p=Path(model_path)
        if self.net.load_param(str(p/'yolo11n.ncnn.param'))!=0 or self.net.load_model(str(p/'yolo11n.ncnn.bin'))!=0:raise RuntimeError('Cannot load frozen model')
        self.cpu_partitions=[{'name':l.name,'type':l.type} for l in self.net.layers() if not l.support_vulkan] if device=='gpu' else [{'name':'all','type':'CPU'}]
        self.cold_load_ms=(time.perf_counter()-start)*1000
        self.weights_sha256=hashlib.sha256((p/'yolo11n.ncnn.bin').read_bytes()).hexdigest()
    def infer(self,image):
        if image.size!=(640,640):raise ValueError('Full frames must be 640×640')
        # ncnn's ndarray constructor interprets this export's input layout
        # differently from its pixel import path and produced NaNs on CPU.
        # Use the same explicit RGB byte conversion and 1/255 normalization
        # for both execution devices.
        start=time.perf_counter();rgb=np.asarray(image.convert('RGB'),dtype=np.uint8)
        tensor=ncnn.Mat.from_pixels(rgb,ncnn.Mat.PixelType.PIXEL_RGB,640,640)
        tensor.substract_mean_normalize([0.0,0.0,0.0],[1.0/255.0,1.0/255.0,1.0/255.0])
        pre=(time.perf_counter()-start)*1000
        before=drm_compute_ns() if self.device=='gpu' else None;t=time.perf_counter()
        with self.net.create_extractor() as ex:
            if ex.input('in0',tensor)!=0:raise RuntimeError('Detector input failed')
            ret,out=ex.extract('out0') # CPU Mat extraction synchronizes GPU completion/download.
            if ret!=0:raise RuntimeError('Detector failed; no silent fallback')
            raw=np.array(out,copy=True)
        inference=(time.perf_counter()-t)*1000;after=drm_compute_ns() if self.device=='gpu' else None
        t=time.perf_counter();boxes=decode(raw,self.size);post=(time.perf_counter()-t)*1000
        compute_delta=None if before is None or after is None else max(0,after-before)
        # A Vulkan device can be present while a graph silently executes on CPU.
        # Only report GPU execution for this call when the process-scoped AMD DRM
        # compute-engine counter advances across the synchronized extraction.
        actual='cpu' if self.device=='cpu' else ('gpu+cpu-partitions' if compute_delta and compute_delta>0 else 'gpu-unverified')
        return boxes,{'preprocessing_ms':pre,'inference_completed_ms':inference,'postprocessing_ms':post,'detector_ms':(time.perf_counter()-start)*1000,'transfer_ms':None,'gpu_kernel_ms':None,'gpu_compute_delta_ns':compute_delta,'actual_device':actual,'gpu_name':self.gpu_name,'cpu_partitions':self.cpu_partitions,'precision':'FP32','input_size':self.size,'weights_sha256':self.weights_sha256}
