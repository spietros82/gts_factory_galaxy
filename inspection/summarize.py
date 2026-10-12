"""Saved-record reporting only: no model, training or evaluation calls."""
from pathlib import Path
import json,csv,statistics,math,hashlib,os

def dist(values):
 values=sorted(values)
 if not values:return {'n':0}
 def percentile(p):return values[min(len(values)-1,max(0,math.ceil(p*len(values))-1))]
 return {'n':len(values),'mean':statistics.mean(values),'p50':percentile(.5),'p95':percentile(.95),'p99':percentile(.99),'max':max(values)}
def main():
 root=Path('reports/inspection/live');final=json.loads((root/'final.json').read_text());native=root/'native';frames=[]
 for p in native.glob('frames-*.csv'):
  for r in csv.DictReader(p.open()):
   if float(r['wall_seconds'])>=5:frames.append(float(r['wall_frame_interval_ms']))
 inspections=[json.loads(l) for l in (root/'service/inspections.jsonl').read_text().splitlines()];calls=[json.loads(l) for l in (root/'service/explanations.jsonl').read_text().splitlines()]
 hw=json.loads((root/'hardware.json').read_text());run=json.loads(next(native.glob('run-*.json')).read_text())
 cpustats={}
 for key in ['native','inspection_service']:
  cpus=[]
  for a,b in zip(hw,hw[1:]):
   if 'cpu_ticks_total' in a.get(key,{}) and 'cpu_ticks_total' in b.get(key,{}):cpus.append((b[key]['cpu_ticks_total']-a[key]['cpu_ticks_total'])/os.sysconf('SC_CLK_TCK')/(b['elapsed_seconds']-a['elapsed_seconds'])*100)
  cpustats[key]={'process_cpu_percent_one_core100':dist(cpus),'rss_bytes':dist([r[key]['rss_bytes'] for r in hw if 'rss_bytes' in r.get(key,{})])}
 first=inspections[0]['capture_utc'];last=inspections[-1]['completed_utc']
 import datetime
 active=(datetime.datetime.fromisoformat(last)-datetime.datetime.fromisoformat(first)).total_seconds()
 summary={'native_run':run,'render_intervals_ms':dist(frames),'mean_render_fps':1000/statistics.mean(frames),'inspection_counts':{c:sum(r['decision']==c for r in inspections) for c in ['aligned','missing','displaced','uncertain']},
 'capture_to_result_ms':dist([r['latency_seconds']*1000 for r in inspections]),'queue_wait_ms':dist([r['queue_seconds']*1000 for r in inspections]),'classification_policy_wall_ms':dist([r['classifier_seconds']*1000 for r in inspections]),
 'first_capture_utc':first,'last_result_utc':last,'active_capture_to_last_result_seconds':active,'completed_inspections':len(inspections),'completed_per_native_wall_second':len(inspections)/run['wall_seconds'],'successive_completion_rate':(len(inspections)-1)/active,
 'final_counters':final['final_state'],'host_cpu_percent_total_capacity':dist([r['host_cpu_percent'] for r in hw if r.get('host_cpu_percent') is not None]),'gpu_busy_percent_device':dist([r['gpu']['gpu_busy_percent'] for r in hw if 'gpu_busy_percent' in r.get('gpu',{})]),'ram_available_gib':dist([r['MemAvailable']/2**30 for r in hw if 'MemAvailable' in r]),'processes':cpustats,
 'language_calls':[{'number':r['number'],'wall_seconds':r['wall_seconds'],'validation':r['validation'],'validation_error':r.get('validation_error'),'model':r['request']['model'],'stop_reason':r['raw_response'].get('done_reason'),'load_seconds':r['raw_response'].get('load_duration',0)/1e9,'prompt_seconds':r['raw_response'].get('prompt_eval_duration',0)/1e9,'generation_seconds':r['raw_response'].get('eval_duration',0)/1e9} for r in calls],
 'backend':'learned random forest CPU; Unity OpenGLCore GPU; qwen ROCm37/37 verified in saved journal','limits':['Native intervals not GPU execution time','CPU host total capacity versus process one-core scale differ','No per-process GPU attribution or shared-memory sum','Live inspection decisions not independently truth-scored; manually viewed crops only','Comparison with saved Gemma is different capture framing/dataset, not controlled accuracy ablation'],'tested_commit':final['tested_commit']}
 Path('reports/inspection/performance-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps({k:summary[k] for k in ['mean_render_fps','render_intervals_ms','completed_inspections','capture_to_result_ms','queue_wait_ms','classification_policy_wall_ms','host_cpu_percent_total_capacity','language_calls']},indent=2))
if __name__=='__main__':main()
