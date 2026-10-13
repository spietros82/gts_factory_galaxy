"""Timing joins only; never model evidence and never modifies raw records."""
import math

def combined_timings(records,traces,wait_scale=1.):
 mapping={v['batch_id']:v for v in traces};out=[]
 for r in records:
  trace=mapping.get(r['batch_id'])
  if trace is None:continue
  wait=trace['acquisition_wait_ms']*wait_scale
  if not math.isfinite(wait) or wait<0:continue
  out.append({'frame_id':r['frame_id'],'batch_id':r['batch_id'],'line_id':r['line_id'],'acquisition_wait_ms':wait,'capture_to_result_ms':r['end_to_end_ms'],'trigger_to_result_ms':wait+r['end_to_end_ms']})
 return out
