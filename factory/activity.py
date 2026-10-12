"""Read-only host counters. Engine occupancy is NOT a share of device utilization."""
import datetime,json,os,pathlib,threading,time,urllib.request

def drm_clients(pid):
    clients={}
    try:
        for path in pathlib.Path('/proc',str(pid),'fdinfo').iterdir():
            try:
                fields=dict(line.split(':',1) for line in path.read_text().splitlines() if line.startswith('drm-'))
                if 'drm-client-id' not in fields:continue
                key=(fields.get('drm-pdev','').strip(),fields['drm-client-id'].strip())
                clients[key]={k:int(v.split()[0]) for k,v in fields.items() if k.startswith('drm-engine-') and v.strip().endswith('ns')}
            except (OSError,ValueError):continue
        return clients,'measured' if clients else 'unavailable: no readable DRM client'
    except OSError:return {},'unavailable: process permissions or exited'

class Sampler:
    def __init__(self,endpoint):self.endpoint=endpoint;self.previous={};self.cpu=None;self.latest={};self.lock=threading.Lock()
    def sample(self):
        now=time.monotonic();out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classification':'directly measured OS counters','processes':[]}
        cpu=list(map(int,pathlib.Path('/proc/stat').read_text().splitlines()[0].split()[1:9]));total=sum(cpu);idle=cpu[3]+cpu[4]
        out['host_cpu_percent']=None if self.cpu is None else 100*(1-(idle-self.cpu[1])/max(1,total-self.cpu[0]));self.cpu=(total,idle)
        mem={l.split(':')[0]:int(l.split()[1])*1024 for l in pathlib.Path('/proc/meminfo').read_text().splitlines() if l.startswith(('MemTotal:','MemAvailable:'))};out.update(mem)
        out['gpu']={}
        for card in pathlib.Path('/sys/class/drm').glob('card[0-9]*/device'):
            for key in ['gpu_busy_percent','mem_info_vram_used','mem_info_gtt_used']:
                try:out['gpu'][key]=int((card/key).read_text())
                except (OSError,ValueError):pass
        for proc in pathlib.Path('/proc').iterdir():
            if not proc.name.isdigit():continue
            try:
                name=(proc/'comm').read_text().strip()
                if name not in ['Unity Main Thre','Unity','llama-server','ollama','gnome-shell','Xwayland','firefox','unityhub-bin']:continue
                clients,status=drm_clients(proc.name);engines={}
                for client,values in clients.items():
                    key=(int(proc.name),client);old=self.previous.get(key);self.previous[key]=(now,values)
                    if old:
                        for engine,value in values.items():
                            delta=value-old[1].get(engine,value)
                            if delta>=0:engines[engine]=engines.get(engine,0)+100*delta/(1e9*(now-old[0]))
                out['processes'].append({'pid':int(proc.name),'name':name,'counter_status':status,'engine_busy_percent':engines})
            except OSError:continue
        try:
            ps=json.load(urllib.request.urlopen(self.endpoint+'/api/ps',timeout=1));out['loaded_models']=[{'name':m['name'],'reported_allocation_bytes':m.get('size_vram')} for m in ps.get('models',[])]
        except Exception:out['loaded_models']=[];out['residency_status']='unavailable'
        out['limitations']='GPU busy is device-wide. DRM engine deltas are per readable client, deduplicated by client ID, not percentage shares; engines may overlap. Other-user model runner counters unavailable. VRAM/GTT are shared-memory accounting domains; do not add to host RAM. Model residency does not establish inference activity. Unrelated applications remain running.'
        with self.lock:self.latest=out
        return out
    def view(self):
        with self.lock:return dict(self.latest)
    def start(self):
        def loop():
            while True:
                try:self.sample()
                except Exception:pass
                time.sleep(2)
        threading.Thread(target=loop,daemon=True).start()

def display(sample,running,calls,backend,states=None,enabled=True):
    gpu=sample.get('gpu',{});cpu=sample.get('host_cpu_percent');fmt=lambda n:'unavailable' if n is None else f'{n:.1f}'
    text=f"Host CPU {fmt(cpu)}% • GPU busy {fmt(gpu.get('gpu_busy_percent'))}% (direct OS counters)\nDevice busy alone cannot attribute workloads.\n"
    for k,label in [('MemTotal','RAM total'),('MemAvailable','RAM available')]:text+=f"{label}: {fmt(sample.get(k)/2**30 if k in sample else None)} GiB\n"
    for k,label in [('mem_info_vram_used','DRM VRAM accounting'),('mem_info_gtt_used','DRM GTT accounting')]:text+=f"{label}: {fmt(gpu[k]/2**30 if k in gpu else None)} GiB\n"
    for task,label in [('vision','Vision'),('assistant','Language')]:
        completed=[c for c in calls if c['task']==task];last=completed[-1] if completed else None
        state='running' if running==task else 'queued' if (states or {}).get(task)=='queued' else 'idle'
        if not enabled:state='disabled'
        elif sample.get('residency_status')=='unavailable' and state=='idle':state='unavailable'
        text+=f"{label}: {state} • {backend}\n"
        if last:
            raw=last['raw_response'];sec=raw.get('eval_duration',0)/1e9;rate=raw.get('eval_count',0)/sec if sec else None
            text+=f"Last request {last['wall_seconds']:.2f}s; generation {fmt(rate)} tokens/s (measured provider)\n"
    recent=[c for c in calls if c['task']=='vision' and not c.get('error') and c.get('validation')!='failed' and time.time()-datetime.datetime.fromisoformat(c['completed_utc']).timestamp()<=60]
    text+=f'Recent completed inspections: {len(recent)}/last60s (measured)\n'
    other=[p for p in sample.get('processes',[]) if p['name'] not in ['Unity','Unity Main Thre','ollama','llama-server']]
    active_names=sorted({p['name'] for p in other if any(v>0 for v in p['engine_busy_percent'].values())})
    text+='Other readable GPU activity: '+(', '.join(active_names) or 'idle / unavailable')+'\nOther-account GPU attribution unavailable.\n'
    text+='Loaded, not necessarily active: '+', '.join(m['name'] for m in sample.get('loaded_models',[]))
    details=sample.get('limitations','Instrumentation warming up')+'\n'
    for p in sample.get('processes',[]):details+=f"PID {p['pid']} {p['name']}: {p['counter_status']} {p['engine_busy_percent']}\n"
    return text,details
