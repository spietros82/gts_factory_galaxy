"""Explicit saved-report correction for frozen9ea0b81 trace unit bug. No inference."""
import json,datetime,copy
from pathlib import Path
from stage4.bench import stats
from stage4.timing import combined_timings
ROOT=Path('reports/stage4/capacity')
def main():
 freeze=json.loads((ROOT/'freeze.json').read_text())
 if freeze['commit']!='9ea0b8132c9266778630a93d65a246bd652f3455':raise SystemExit('Correction is only authorised for known frozen unit bug')
 original=json.loads((ROOT/'summary.json').read_text());result=copy.deepcopy(original);result['correction']='Raw acquisition_wait_ms contains seconds in9ea0b81; corrected reported wait×1000. Raw records/summary retained. Capture→result latency is already ms and unchanged. Trigger→result derived from matched direct timings, not AI.'
 for r in result['phases']:
  root=ROOT/r['name'];epoch=datetime.datetime.fromisoformat(r['native_metadata']['started_utc']).timestamp();warm=r['warmup_seconds'];measure=r['measurement_seconds'];records=[];traces=[]
  for file in (root/'service').glob('results.jsonl*'):records.extend(json.loads(l) for l in file.read_text().splitlines())
  for file in (root/'native').glob('captures.jsonl*'):traces.extend(json.loads(l) for l in file.read_text().splitlines())
  records=[v for v in records if epoch+warm<=datetime.datetime.fromisoformat(v['completed_utc']).timestamp()<epoch+warm+measure]
  joined=combined_timings(records,traces,1000.)
  r['acquisition_wait_ms_raw_mislabeled']=r['acquisition_wait_ms'];r['acquisition_wait_ms']=stats([v['acquisition_wait_ms'] for v in joined]);r['trigger_to_result_ms']=stats([v['trigger_to_result_ms'] for v in joined]);r['trigger_deadlines_over_2s']=sum(v['trigger_to_result_ms']>2000 for v in joined);r['timing_join_sample_count']=len(joined)
  (root/'corrected-trigger-timings.json').write_text(json.dumps(joined))
 (ROOT/'corrected-summary.json').write_text(json.dumps(result,indent=2));print('Saved explicit corrected summary; original retained')
if __name__=='__main__':main()
