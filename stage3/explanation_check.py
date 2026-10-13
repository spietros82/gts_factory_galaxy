"""Three frozen, sequential Stage3 event explanations. No retries."""
import json,time,hashlib
from pathlib import Path
from stage3.gui_check import api,wait,click,audit,shot
from stage3.service import explain_request
from factory.model import ollama_payload

def main():
 out=Path('reports/stage3/qwen');out.mkdir(exist_ok=True)
 if (out/'frozen-inputs.json').exists():raise SystemExit('Frozen run already reserved; no retries')
 if api()['explanation_calls']!=0:raise SystemExit('Existing requests; do not reset ledger')
 records=[]
 for y,station,decision in [(376,'cap','missing'),(487,'fill','underfilled'),(652,'label','misaligned')]:
  click(1310,70);click(290,y);after=time.time();click(855,112)
  s=wait(lambda s:any(r['station_id']==station and r['decision']==decision and __import__('datetime').datetime.fromisoformat(r['capture_utc']).timestamp()>after for r in s['events']),18)
  records.append(next(r for r in s['events'] if r['station_id']==station and r['decision']==decision and __import__('datetime').datetime.fromisoformat(r['capture_utc']).timestamp()>after))
 click(90,155)
 # Freeze exact generated requests and factual expectations BEFORE any language inference.
 plan={'settings':{'model':'qwen3:8b','temperature':0,'seed':42,'num_ctx':8192,'num_predict':512,'think':False,'timeout_seconds':120},'expectations':'Mention only recorded synthetic visual finding and uncertainty; cite exact frame/S3-DEMO-1; useful crop/association review; no physical properties/cause/control action. Vision decisions unchanged.','records':records,'requests':[ollama_payload(explain_request(r,'qwen3:8b')) for r in records]}
 (out/'frozen-inputs.json').write_text(json.dumps(plan,indent=2))
 checks=[]
 for r in records:
  raw_before=next(json.loads(l) for l in Path('runtime/stage3-service/results.jsonl').read_text().splitlines() if json.loads(l)['frame_id']==r['frame_id'])
  start=time.time();print('Request',r['station_id'],r['frame_id'],flush=True);reply=api('/explain',{'frame_id':r['frame_id']});s=wait(lambda s:s['assistant_state']!='processing',130)
  raw_after=next(json.loads(l) for l in Path('runtime/stage3-service/results.jsonl').read_text().splitlines() if json.loads(l)['frame_id']==r['frame_id'])
  checks.append({'station':r['station_id'],'frame_id':r['frame_id'],'vision_record_unchanged':raw_before==raw_after,'state':s['assistant_state'],'displayed_text':s['assistant_text'],'wait_seconds':time.time()-start})
  print(checks[-1],flush=True)
 for name in ['stage3-qwen-ledger.jsonl','explanations.jsonl']:(out/name).write_bytes((Path('runtime/stage3-service')/name).read_bytes())
 (out/'application-checks.json').write_text(json.dumps(checks,indent=2))
 click(1080,112);click(230,305);shot('qwen-event-review')
 click(1310,70);click(290,322);click(610,112);click(90,155)
if __name__=='__main__':main()
