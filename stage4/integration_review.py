"""Once-only new integration crop review; no old locked set, no training/tuning."""
import base64,hashlib,json
from pathlib import Path
from io import BytesIO
from PIL import Image
import numpy as np
from stage3.backend import NeuralBackend,STATIONS
from stage3.service import validate_batch
ROOT=Path('reports/stage4/integration')
def main():
 marker=ROOT/'review-started.json'
 if marker.exists():raise SystemExit('Integration review already performed; preserve results')
 marker.write_text(json.dumps({'scope':'NEW integration images only; frozen Stage3weights; no tuning'}))
 plan=json.loads((ROOT/'capture-plan.json').read_text())['items'];expect=json.loads((ROOT/'expectations.json').read_text());backends={d:NeuralBackend('stage3/models',d) for d in ['cpu','gpu']};results=[];comparison=[]
 for item in plan:
  payload=json.loads((ROOT/'native'/(item['id']+'.json')).read_text());_,images=validate_batch(payload);truth=expect[item['id']]
  for i,(frame,raw,crop) in enumerate(images):
   cpu=backends['cpu'].predict(frame['station_id'],crop);gpu=backends['gpu'].predict(frame['station_id'],crop);sample={'id':item['id'],'line_id':payload['line_id'],'session_id':payload['session_id'],'bottle_id':payload['bottle_id'],'station_id':frame['station_id'],'frame_id':frame['frame_id'],'product':item['product'],'expected':truth['expected'][i],'cpu':cpu,'gpu':gpu,'decision_match':cpu['decision']==gpu['decision'],'score_abs_difference':abs(cpu['score']-gpu['score']),'expected_match':cpu['decision']==gpu['decision']==truth['expected'][i],'crop_sha256':hashlib.sha256(crop.tobytes()).hexdigest()};results.append(sample)
   if truth.get('comparison'):comparison.append(sample)
   (ROOT/'crops').mkdir(exist_ok=True);crop.save(ROOT/'crops'/(frame['frame_id']+'.png'))
 invariance={s:len({r['crop_sha256'] for r in comparison if r['station_id']==s})==1 for s in STATIONS}
 summary={'scope':'81 newly authored rendered crops / 27batches; integration, not new industrial accuracy or locked-set test','expected_matches':sum(r['expected_match'] for r in results),'total':len(results),'cpu_gpu_agreement':sum(r['decision_match'] for r in results),'maximum_score_difference':max(r['score_abs_difference'] for r in results),'numerical_tolerance':.0001,'tolerance_pass':all(r['score_abs_difference']<=.0001 for r in results),'canonical_multi_origin_pixel_identical':invariance,'failures':[r for r in results if not r['expected_match']],'results':results}
 (ROOT/'review.json').write_text(json.dumps(summary,indent=2));print({k:v for k,v in summary.items() if k not in ['results','failures']})
 # Contact sheet for manual label/crop review; external truth is never classifier input.
 sheet=Image.new('RGB',(3*160,9*160),'white')
 for n,r in enumerate(results[::3][:9]):
  row=[q for q in results if q['id']==r['id']]
  for i,q in enumerate(row):sheet.paste(Image.open(ROOT/'crops'/(q['frame_id']+'.png')),(i*160,n*160))
 sheet.save(ROOT/'contact-sheet.png')
if __name__=='__main__':main()
