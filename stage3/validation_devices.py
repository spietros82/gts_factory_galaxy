import json
from pathlib import Path
from PIL import Image
from stage3.backend import NeuralBackend
rows=json.loads(Path('stage3/dataset/validation.json').read_text());cpu=NeuralBackend(device='cpu');gpu=NeuralBackend(device='gpu');records=[]
for r in rows[::4]:
 im=Image.open('stage3/dataset/crops/'+r['id']+'.png');a=cpu.predict(r['station'],im);b=gpu.predict(r['station'],im);records.append({'id':r['id'],'matches':a['decision']==b['decision'],'score_delta':abs(a['score']-b['score']),'gpu_elapsed_ms':b['gpu_elapsed_ms']})
report={'cold_cpu_ms':cpu.cold_start_ms,'cold_gpu_ms':gpu.cold_start_ms,'renderer':gpu.renderer,'samples':len(records),'all_decisions_match':all(r['matches'] for r in records),'max_score_delta':max(r['score_delta'] for r in records),'records':records};Path('reports/stage3/device-validation.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='records'});assert report['all_decisions_match']
