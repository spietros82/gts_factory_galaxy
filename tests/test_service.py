import unittest,tempfile,pathlib,json,time
from factory.analysis import validate_observations,findings,assistant_evidence
from factory.model import FakeAdapter,ModelRequest,ModelResponse,validate_response,ASSIST_SCHEMA
from factory.service import State
ROOT=pathlib.Path(__file__).resolve().parent.parent
def row(sequence=1,value=500,head=0,quality='good'):
 return {'contract':'gts.telemetry/1','asset_id':'filler','name':'fill_ml','unit':'mL','quality':quality,'machine_state':'cycling','sequence':sequence,'timestamp':10+sequence*.1,'value':value,'has_value':quality=='good','bottle_id':sequence,'head':head}
def batch(rows):return {'contract':'gts.observation-batch/1','session':'test','sim_time':30,'profile':2,'observations':rows}
class Checks(unittest.TestCase):
 def test_untrusted_observation_fields(self):
  with self.assertRaises(ValueError):validate_observations(batch([dict(row(),fault='cap')]))
 def test_contract_bound(self):
  with self.assertRaises(ValueError):validate_observations(batch([row()]*401))
 def test_missing_and_stale(self):
  e=assistant_evidence([row(1,0,quality='missing'),row(2,499)],30,[])
  self.assertTrue(all(o['value'] is None for o in e['observations']))
  self.assertEqual(findings([row(i,0,quality='missing') for i in range(1,10)],30,2),[])
 def test_normal_variability(self):
  results=findings([row(i,500+(-1)**i) for i in range(1,21)],30,2);self.assertFalse(results[0]['flagged'])
 def test_perhead_measurement(self):
  results=findings([row(i,490,2) for i in range(1,21)],30,2);self.assertTrue(results[0]['flagged']);self.assertIn('Head 3',results[0]['title'])
 def test_plc_only_not_weakened(self):self.assertEqual(findings([row(i,490) for i in range(1,21)],30,1),[])
 def test_model_reference_membership(self):
  out={'explanation':'Unconfirmed','next_check':'Inspect','uncertainty':'Unknown','evidence_ids':['O-999'],'procedure_ids':['P-FILL-1']}
  r=ModelResponse({'done':True,'done_reason':'stop','message':{'content':json.dumps(out)}},1,'fake/test')
  with self.assertRaises(ValueError):validate_response('assistant',r,['O-1'],['P-FILL-1'])
 def test_malformed_and_unavailable(self):
  for r in [ModelResponse({},1,'fake/test','timeout'),ModelResponse({'done':True,'message':{'content':'bad'}},1,'fake/test')]:
   with self.assertRaises(ValueError):validate_response('assistant',r)
 def test_queue_bound_and_duplicate_ingestion(self):
  with tempfile.TemporaryDirectory() as d:
   cfg=json.loads((ROOT/'config.example.json').read_text());cfg['data_path']=d;cfg['procedures_path']=str(ROOT/'data/procedures.json');cfg['inference_enabled']=False
   s=State(cfg,FakeAdapter());s.ingest(batch([row()]));s.ingest(batch([row()]));self.assertEqual(len(s.rows),1)
   with self.assertRaises(ValueError):s.request('assistant',{})
   self.assertEqual(s.queue.maxsize,2)
 def test_ground_truth_separation(self):
  source=(ROOT/'UnityProject/Assets/Scripts/EdgeClient.cs').read_text();cam=source.split('class CameraFrame')[1].split('class ScoringTruth')[0]
  self.assertNotIn('cap_present',cam);self.assertNotIn('cap_displaced',cam)
 def test_no_model_control_adapter(self):
  self.assertEqual(set(ASSIST_SCHEMA['properties']),{'explanation','next_check','uncertainty','evidence_ids','procedure_ids'})
if __name__=='__main__':unittest.main()
