import unittest,json,base64,uuid,copy,tempfile,time
from pathlib import Path
from io import BytesIO
from PIL import Image
from stage3.service import validate_batch,validate_explanation,explain_request,Engine
from factory.model import FakeAdapter,ModelResponse
class SafetyTests(unittest.TestCase):
 def batch(self):
  b=BytesIO();Image.new('RGB',(256,256),'white').save(b,format='PNG')
  return dict(contract='gts.three-frame/1',line_id='Line01',session_id='session',bottle_id='12',batch_id='batch',capture_utc='2026-10-13T00:00:00+00:00',source_time=42.0,target_count=1,observations_available=True,product='LAGER',frames=[dict(station_id=s,frame_id=uuid.uuid4().hex,image=base64.b64encode(b.getvalue()).decode(),roi=[48,48,160,160]) for s in ['cap','fill','label']])
 def test_three_distinct_views_same_association(self):
  t,views=validate_batch(self.batch());self.assertEqual([v[2].size for v in views],[(160,160)]*3)
 def test_duplicate_frame_identity(self):
  b=self.batch();b['frames'][1]['frame_id']=b['frames'][0]['frame_id']
  with self.assertRaises(ValueError):validate_batch(b)
 def test_hidden_truth_rejected(self):
  b=self.batch();b['expected_class']='aligned'
  with self.assertRaises(ValueError):validate_batch(b)
 def test_frame_metadata_truth_rejected(self):
  b=self.batch();b['frames'][0]['mask']='hidden'
  with self.assertRaises(ValueError):validate_batch(b)
 def test_unexpected_dimensions(self):
  b=self.batch();b['frames'][0]['roi']=[0,0,999,999]
  with self.assertRaises(ValueError):validate_batch(b)
 def test_missing_station(self):
  b=self.batch();b['frames'].pop()
  with self.assertRaises(ValueError):validate_batch(b)
 def test_path_traversal(self):
  b=self.batch();b['frames'][0]['frame_id']='../evil'
  with self.assertRaises(ValueError):validate_batch(b)
 def test_qwen_invalid_cannot_establish_finding(self):
  r={'frame_id':'evidence'};reply=FakeAdapter({'done':True,'done_reason':'stop','message':{'content':'not json'}}).execute(None)
  with self.assertRaises(ValueError):validate_explanation(reply,r)
 def test_qwen_invented_reference(self):
  v=dict(explanation='Synthetic defect',next_check='Review crop',uncertainty='Experimental',evidence_ids=['invented'],procedure_ids=['S3-DEMO-1']);reply=ModelResponse({'done':True,'done_reason':'stop','message':{'content':json.dumps(v)}},0,'fake')
  with self.assertRaises(ValueError):validate_explanation(reply,{'frame_id':'evidence'})
 def test_qwen_scope_violation(self):
  v=dict(explanation='Cap seal is secure',next_check='Review crop',uncertainty='Experimental',evidence_ids=['evidence'],procedure_ids=['S3-DEMO-1']);reply=ModelResponse({'done':True,'done_reason':'stop','message':{'content':json.dumps(v)}},0,'fake')
  with self.assertRaises(ValueError):validate_explanation(reply,{'frame_id':'evidence'})
 def test_ml_decision_is_not_volume_unit(self):
  v=dict(explanation="Synthetic ML decision, uncertain",next_check="Review crop",uncertainty="Experimental",evidence_ids=["evidence"],procedure_ids=["S3-DEMO-1"]);reply=ModelResponse({"done":True,"done_reason":"stop","message":{"content":json.dumps(v)}},0,"fake")
  self.assertEqual(validate_explanation(reply,{"frame_id":"evidence"})["explanation"],v["explanation"])
  v["explanation"]="Contains 250 ml";reply.raw["message"]["content"]=json.dumps(v)
  with self.assertRaises(ValueError):validate_explanation(reply,{"frame_id":"evidence"})
 def test_defect_review_survives_healthy_history_and_restart(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as d:
   rows=[dict(frame_id=str(i),batch_id=str(i),session_id='past',capture_utc='2026-10-13T00:00:00+00:00',decision='missing' if i==0 else 'aligned') for i in range(220)]
   Path(d,'results.jsonl').write_text('\n'.join(json.dumps(r) for r in rows))
   cfg=dict(data_path=d,device='cpu',queue_capacity=2,ollama_endpoint='http://127.0.0.1:11434',assistant_timeout_seconds=1,monitoring=False)
   with patch('threading.Thread.start'):engine=Engine(cfg)
   self.assertEqual(len(engine.records),200);self.assertTrue(any(r['frame_id']=='0' for r in engine.view()['events']))
 def test_backend_failure_honest(self):
  with self.assertRaises(ValueError):validate_explanation(FakeAdapter(error='offline').execute(None),{'frame_id':'evidence'})
if __name__=='__main__':unittest.main()
