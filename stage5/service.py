"""Loopback bounded full-frame detector service, contract gts.full-frame/1."""
import argparse,collections,hashlib,io,json,math,queue,re,threading,time
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from PIL import Image,ImageDraw
from .detector import Detector
from .tracker import Tracker
from stage3.monitor import Monitor

FIELDS={'line_id','session_id','camera_id','frame_id','sequence','capture_utc','source_time','width','height'}
def validate(meta,raw,registry,now=None):
    if set(meta)!=FIELDS:raise ValueError('Unexpected metadata; simulator truth/IDs/crops are prohibited')
    for key in ('line_id','session_id','camera_id','frame_id'):
        if not isinstance(meta[key],str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,96}',meta[key]):raise ValueError('Invalid neutral identity')
    if registry.get(meta['line_id'])!=meta['session_id']:raise ValueError('Retired or unregistered session')
    if meta['width']!=640 or meta['height']!=640 or len(raw)>2*1024*1024 or not raw.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Expected bounded 640×640 PNG frame')
    if not isinstance(meta['sequence'],int) or meta['sequence']<0:raise ValueError('Invalid sequence')
    if not isinstance(meta['source_time'],(int,float)) or not math.isfinite(meta['source_time']) or meta['source_time']<0:raise ValueError('Invalid source time')
    captured=datetime.fromisoformat(meta['capture_utc'].replace('Z','+00:00')).timestamp()
    age=(time.time() if now is None else now)-captured
    if age<-.10 or age>.5:raise ValueError('Capture timestamp future/stale')
    return captured

class Engine:
    def __init__(self,config,detectors=None):
        self.config=config;self.path=Path(config['data_path']);self.path.mkdir(parents=True,exist_ok=True)
        self.lock=threading.RLock();self.queue=queue.Queue(maxsize=config['queue_capacity']);self.registry={};self.epoch=0;self.trackers={};self.latest={};self.ids=collections.OrderedDict();self.sequences={};self.counts=collections.Counter();self.reasons=collections.Counter();self.records=collections.deque(maxlen=4096);self.latencies=collections.deque(maxlen=20000);self.device=config['device'];self.actual='idle';self.current='idle';self.running=True;self.start=time.time();self.native={};self.metrics={};self.monitor=Monitor();self.gpu_verified=False;self.files=collections.deque();self.last_native_cpu=None
        if detectors is None:
            self.detectors={'cpu':Detector(config['model_path'],'cpu',threads=config['threads'])};self.gpu_error=''
            try:self.detectors['gpu']=Detector(config['model_path'],'gpu',threads=config['threads'])
            except Exception as e:self.gpu_error=str(e)
        else:self.detectors=detectors;self.gpu_error='fake/offline'
        self.cold={d:{'load_ms':getattr(v,'cold_load_ms',None),'cpu_partitions':getattr(v,'cpu_partitions',[]),'gpu_name':getattr(v,'gpu_name',None)} for d,v in self.detectors.items()}
        self.worker=threading.Thread(target=self.work,daemon=True);self.worker.start()
        if config.get('monitoring'):threading.Thread(target=self.sample,daemon=True).start()
    def audit(self,kind,value):
        record={'event':kind,'wall_utc':datetime.now(timezone.utc).isoformat(),**value};p=self.path/'audit.jsonl'
        with self.lock:
            if p.exists() and p.stat().st_size>4*1024*1024:
                for i in (2,1):
                    source=p if i==1 else self.path/'audit.jsonl.1';dest=self.path/('audit.jsonl.'+str(i))
                    if source.exists():source.replace(dest)
            with p.open('a') as f:f.write(json.dumps(record,allow_nan=False)+'\n')
    def reject(self,reason):
        self.counts['rejected']+=1;self.reasons[reason]+=1
    def register(self,lines):
        if not 1<=len(lines)<=3 or len({l['line_id'] for l in lines})!=len(lines):raise ValueError('Full-frame guard1–3lines')
        new={l['line_id']:l['session_id'] for l in lines}
        if any(set(l)!={'line_id','session_id'} for l in lines):raise ValueError('Registry contains unsupported fields')
        if any(not re.fullmatch(r'[A-Za-z0-9_-]{1,96}',v) for pair in new.items() for v in pair):raise ValueError('Invalid registry')
        with self.lock:
            if new==self.registry:return
            self.registry=new;self.epoch+=1;self.latest.clear();self.trackers.clear();self.sequences.clear()
        self.audit('registry',{'lines':lines,'epoch':self.epoch})
    def submit(self,meta,raw):
        with self.lock:
            self.counts['offered']+=1
            try:captured=validate(meta,raw,self.registry)
            except Exception as e:self.reject(str(e));raise
            key=(meta['line_id'],meta['session_id'],meta['camera_id'])
            if meta['frame_id'] in self.ids:self.reject('duplicate');raise ValueError('duplicate')
            if meta['sequence']<=self.sequences.get(key,-1):self.reject('out-of-order');raise ValueError('out-of-order')
            if self.queue.full():self.reject('queue-full');raise ValueError('queue-full')
            self.ids[meta['frame_id']]=True
            while len(self.ids)>8192:self.ids.popitem(last=False)
            self.sequences[key]=meta['sequence'];self.counts['accepted']+=1
            self.queue.put_nowait((meta,raw,captured,time.time(),self.epoch));self.audit('accepted',{'metadata':meta,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    def work(self):
        while self.running:
            try:meta,raw,captured,admitted,epoch=self.queue.get(timeout=.2)
            except queue.Empty:continue
            try:
                with self.lock:
                    if epoch!=self.epoch:self.reject('retired-before-inference');continue
                    device=self.device;self.current='processing'
                worker_started=time.time();begin=time.perf_counter()
                with Image.open(io.BytesIO(raw)) as decoded:
                    if decoded.format!='PNG' or decoded.size!=(640,640):raise ValueError('Frame PNG must decode as 640×640')
                    image=decoded.convert('RGB')
                decode_ms=(time.perf_counter()-begin)*1000
                if time.time()-captured>self.config['deadline_seconds']:
                    with self.lock:self.counts['expired']+=1;self.reasons['expired-in-queue']+=1
                    self.audit('expired',{'frame_id':meta['frame_id'],'age_ms':1000*(time.time()-captured)});continue
                boxes,timing=self.detectors[device].infer(image);tracking_start=time.perf_counter()
                with self.lock:
                    if epoch!=self.epoch:self.counts['cancelled']+=1;self.reasons['retired-after-inference']+=1;continue
                    key=(meta['line_id'],meta['session_id'],meta['camera_id']);tracker=self.trackers.setdefault(key,Tracker());tracked=tracker.update(boxes,captured)
                tracking_ms=(time.perf_counter()-tracking_start)*1000
                if device=='gpu' and timing.get('gpu_compute_delta_ns',0)>0:self.gpu_verified=True
                stale=time.time()-captured>self.config['deadline_seconds']
                for b in tracked:
                    if stale:b['association']='stale';b['inspection']='uncertain'
                storage_start=time.perf_counter();fid=meta['frame_id'];original=self.path/(fid+'.png');overlay=self.path/(fid+'-overlay.png');image.save(original)
                drawing=image.copy();draw=ImageDraw.Draw(drawing)
                for b in tracked:
                    draw.rectangle(b['box'],outline=(10,240,220),width=3);draw.text((b['box'][0],max(0,b['box'][1]-12)),f"{b['track_id'] or '?'} bottle {b['score']:.2f}",fill='white')
                    for region in b['regions'].values() if 'regions' in b else []:draw.rectangle(region,outline=(240,200,70),width=1)
                drawing.save(overlay);storage_ms=(time.perf_counter()-storage_start)*1000
                completed=time.time();record={'metadata':meta,'detections':tracked,'timing':timing,'decode_ms':decode_ms,'queue_ms':1000*(completed-storage_ms/1000-captured)-timing['detector_ms']-tracking_ms-decode_ms,'tracking_ms':tracking_ms,'storage_ms':storage_ms,'admission_utc':admitted,'completion_utc':datetime.now(timezone.utc).isoformat(),'completed_epoch':completed,'end_to_end_ms':1000*(completed-captured),'stale':stale or completed-captured>self.config['deadline_seconds'],'original_url':'/image/'+fid+'.png','overlay_url':'/image/'+fid+'-overlay.png','downstream':'uncertain — new detector-derived crops are outside frozen classifier validation'}
                # Queue interval is admission to worker start; transfer is capture to admission.
                record['queue_ms']=1000*(worker_started-admitted)
                record['transport_and_readback_ms']=1000*(admitted-captured)
                with self.lock:
                    if epoch!=self.epoch:self.counts['cancelled']+=1;self.reasons['retired-after-storage']+=1;original.unlink(missing_ok=True);overlay.unlink(missing_ok=True);continue
                    self.files.append((original,overlay))
                    while len(self.files)>self.config['image_limit']:
                        for f in self.files.popleft():f.unlink(missing_ok=True)
                    self.latest[key]=record;self.records.append(record);self.latencies.append(record['end_to_end_ms']);self.counts['completed']+=1;self.counts['detections']+=len(boxes);self.counts['uncertain_inspections']+=len(boxes);self.counts['empty_detections']+=int(not boxes);self.counts['deadline_misses']+=int(record['stale']);self.actual=timing['actual_device']
                self.audit('result',record)
            except Exception as e:
                with self.lock:self.counts['failed']+=1;self.reasons['inference-or-storage-failure']+=1;self.actual='unavailable'
                self.audit('failure',{'metadata':meta,'error':str(e)})
            finally:
                self.current='idle';self.queue.task_done()
    def sample(self):
        while self.running:
            start=time.perf_counter();m=self.monitor.sample();pid=self.native.get('pid')
            try:
                p=Path('/proc')/str(pid);f=(p/'stat').read_text().rsplit(')',1)[1].split();ticks=int(f[11])+int(f[12]);now=time.monotonic()
                if self.last_native_cpu and self.last_native_cpu[0]==pid:m['native_cpu_percent']=100*(ticks-self.last_native_cpu[2])/100/(now-self.last_native_cpu[1])
                m['native_rss_mb']=int(f[21])*4096/1e6;self.last_native_cpu=(pid,now,ticks)
            except (OSError,ValueError):m['native_cpu_percent']=m['native_rss_mb']=-1
            m['cpu_temperature_c']=-1
            for root in Path('/sys/class/hwmon').glob('hwmon*'):
                try:
                    if (root/'name').read_text().strip()=='k10temp':m['cpu_temperature_c']=float((root/'temp1_input').read_text())/1000
                except OSError:pass
            m['monitor_total_ms']=(time.perf_counter()-start)*1000
            with self.lock:self.metrics=m
            self.audit('resources',m);time.sleep(1)
    def state(self):
        with self.lock:
            elapsed=max(.001,time.time()-self.start);latest=[]
            for v in self.latest.values():
                r=dict(v);r['age_seconds']=time.time()-datetime.fromisoformat(v['metadata']['capture_utc']).timestamp();r['historical']=r['age_seconds']>.5 or bool(self.native.get('paused'));latest.append(r)
            return {'contract':'gts.full-state/1','selected_device':self.device,'actual_device':self.actual,'status':self.current,'gpu_verified':self.gpu_verified,'gpu_error':self.gpu_error,'cold':self.cold,'model':'YOLO11n COCO / ncnn1.0.20260526','precision':'FP32','input_size':640,'tensor_batch_size':1,'larger_batches':'unavailable in frozen exported graph','counts':dict(self.counts),'drop_reasons':dict(self.reasons),'queue_depth':self.queue.qsize(),'oldest_queue_age':max([0]+[time.time()-v[2] for v in list(self.queue.queue)]),'offered_rate':self.counts['offered']/elapsed,'accepted_rate':self.counts['accepted']/elapsed,'completed_rate':self.counts['completed']/elapsed,'latency_p50_ms':float(__import__('numpy').percentile(self.latencies,50)) if self.latencies else None,'latency_p95_ms':float(__import__('numpy').percentile(self.latencies,95)) if self.latencies else None,'latency_p99_ms':float(__import__('numpy').percentile(self.latencies,99)) if self.latencies else None,'latest':latest,'metrics':self.metrics,'native':self.native,'elapsed_seconds':elapsed,'qwen':'disabled; Stage5 ledger0/2'}
    def stop(self):
        with self.lock:self.epoch+=1;self.latest.clear();self.trackers.clear();self.native['stop_requested']=True
        self.audit('operator-stop',{})
    def close(self):self.running=False;self.worker.join(timeout=5)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def response(self,status,value):
        data=json.dumps(value,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        e=self.server.engine
        if self.path in ('/state','/health'):self.response(200,e.state());return
        match=re.fullmatch(r'/image/([a-f0-9]{32}(?:-overlay)?\.png)',self.path)
        if match:
            p=e.path/match[1]
            if p.exists():
                data=p.read_bytes();self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        self.response(404,{'error':'not found'})
    def do_POST(self):
        e=self.server.engine
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n<=0 or n>2*1024*1024:raise ValueError('Body size outside bounds')
            body=self.rfile.read(n)
            if self.path=='/frame':e.submit(json.loads(self.headers['X-Gts-Metadata']),body);self.response(202,{'accepted':True});return
            value=json.loads(body)
            if self.path=='/registry':e.register(value['lines'])
            elif self.path=='/device':
                if value['device'] not in e.detectors:raise ValueError('Selected device unavailable: '+e.gpu_error)
                with e.lock:e.device=value['device']
            elif self.path=='/native':
                if not isinstance(value,dict):raise ValueError('Native heartbeat must be a mapping')
                with e.lock:e.native=value
            elif self.path=='/stop':e.stop()
            else:self.response(404,{'error':'unsupported endpoint'});return
            self.response(200,{'ok':True})
        except Exception as ex:self.response(400,{'error':str(ex)})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default='stage5/config.local.json');a=p.parse_args();c=json.loads(Path(a.config).read_text());assert c['host']=='127.0.0.1';assert 1<=c['queue_capacity']<=12 and 1<=c['image_limit']<=256
    server=ThreadingHTTPServer((c['host'],c['port']),Handler);server.engine=Engine(c)
    (server.engine.path/'cold-start.json').write_text(json.dumps(server.engine.cold,indent=2))
    try:server.serve_forever()
    finally:server.engine.close();server.server_close()
