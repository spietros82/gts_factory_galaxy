import unittest,base64,json,datetime,time,tempfile
from pathlib import Path
from io import BytesIO
from PIL import Image
from .backend import Assessment,DecisionPolicy,localize,LearnedBackend
from .service import validate_input,State
from factory.model import FakeAdapter

class Probe:
 name='fake/test CPU'
 def __init__(self):self.calls=0
 def assess(self,crop):self.calls+=1;return Assessment('aligned',.99,self.name,'fake result')

def frame():
 im=Image.new('RGB',(512,384));pix=im.load()
 for x in range(512):
  for y in range(384):pix[x,y]=(100+(x%5)*20,100+(y%5)*20,150)
 b=BytesIO();im.save(b,format='PNG')
 return {'contract':'gts.focused-frame/1','frame_id':'neutral-1','capture_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target_id':'42','session':'neutral','association':'simulator-assisted','target_count':1,'observations_available':True,'roi':[150,100,120,120],'image':base64.b64encode(b.getvalue()).decode()}
class Tests(unittest.TestCase):
 def setUp(self):
  self.backend=Probe();self.policy=DecisionPolicy({'threshold':.6});self.crop=localize(Image.open(BytesIO(base64.b64decode(frame()['image']))),[150,100,120,120]);self.meta={'association':'simulator-assisted','target_count':1,'observations_available':True,'capture_epoch':100}
 def test_exact_metadata_rejects_truth(self):
  for key in ['cap_present','fault','object_name','label','mask']:
   body=frame();body[key]='aligned'
   with self.assertRaises(ValueError):validate_input(body)
 def test_multiple_targets(self):
  self.meta['target_count']=2;self.assertEqual(self.policy.decide(self.backend,self.crop,self.meta,100).label,'uncertain');self.assertEqual(self.backend.calls,0)
 def test_stale_frame(self):self.assertEqual(self.policy.decide(self.backend,self.crop,self.meta,103).label,'uncertain')
 def test_missing_observation(self):
  self.meta['observations_available']=False;self.assertEqual(self.policy.decide(self.backend,self.crop,self.meta,100).label,'uncertain')
 def test_tiny_dark_blank(self):
  for im in [self.crop.resize((16,16)),Image.new('RGB',(100,100)),Image.new('RGB',(100,100),(150,150,150))]:self.assertEqual(self.policy.decide(self.backend,im,self.meta,100).label,'uncertain')
 def test_pixels_backend_only(self):
  self.meta['target_id']='arbitrary';self.assertEqual(self.policy.decide(self.backend,self.crop,self.meta,100).label,'aligned');self.assertEqual(self.backend.calls,1)
 def test_roi_invalid(self):
  with self.assertRaises(ValueError):localize(self.crop,[-1,0,60,60])
 def test_path_escape(self):
  body=frame();body['frame_id']='../password'
  with self.assertRaises(ValueError):validate_input(body)
 def make_state(self,adapter):
  cfg=json.loads(Path('inspection/config.example.json').read_text());temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);cfg['data_path']=temp.name
  return State(cfg,self.backend,adapter)
 def wait(self,state):state.jobs.join();state.explanations.join()
 def test_duplicate_submission(self):
  state=self.make_state(FakeAdapter());body=frame();state.submit(body);state.submit(body);self.wait(state);self.assertEqual(state.counts['captured'],1);self.assertEqual(state.counts['inspected'],1)
 def test_backend_outage_no_decision_override(self):
  state=self.make_state(FakeAdapter(error='backend unavailable'));state.submit(frame());self.wait(state);original=dict(state.result);state.explain();self.wait(state);self.assertEqual(state.result,original);self.assertEqual(state.assistant_state,'fallback');self.assertIn('APPLICATION FACTUAL FALLBACK',state.assistant_text)
 def test_invalid_reference_and_attachment_wording(self):
  for evidence,text in [(['invented'],'Cap appears aligned'),(['neutral-1'],'Torque and seal are guaranteed'),(['neutral-1'],'The cap is secured and leakproof')]:
   raw={'done':True,'done_reason':'stop','message':{'content':json.dumps({'explanation':text,'next_check':'Review crop','uncertainty':'Synthetic','evidence_ids':evidence,'procedure_ids':['IP-CHECK-1']})}}
   state=self.make_state(FakeAdapter(raw));state.submit(frame());self.wait(state);original=dict(state.result);state.explain();self.wait(state);self.assertEqual(state.result,original);self.assertEqual(state.assistant_state,'fallback')
 def test_no_fresh_evidence_no_call(self):
  state=self.make_state(FakeAdapter());state.explain();self.assertEqual(state.counts['explanation_calls'],0)
 def test_six_call_limit(self):
  state=self.make_state(FakeAdapter(error='offline'));state.submit(frame());self.wait(state);state.counts['explanation_calls']=6
  with self.assertRaises(ValueError):state.explain()
 def test_frozen_weight_hash(self):
  policy=json.loads(Path('inspection/models/policy.json').read_text());policy['model_sha256']='bad'
  with self.assertRaises(ValueError):LearnedBackend('inspection/models/cap-rf.joblib',policy)
 def test_native_quality_uses_observations_not_presenter_flag(self):
  source=Path('UnityProject/Assets/Scripts/FocusedInspection.cs').read_text().split('IEnumerator CaptureAndSend')[1].split('UnityWebRequest Post')[0]
  self.assertNotIn('ObservationLoss',source)
  self.assertNotIn('CapPresent',source)
  self.assertNotIn('CapDisplaced',source)
  self.assertIn('o.has_value',source)
 def test_explanation_has_own_evidence_age(self):
  raw={'done':True,'done_reason':'stop','message':{'content':json.dumps({'explanation':'Cap visually aligned','next_check':'Review crop','uncertainty':'Synthetic only','evidence_ids':['neutral-1'],'procedure_ids':['IP-CHECK-1']})}}
  state=self.make_state(FakeAdapter(raw));state.submit(frame());self.wait(state);state.explain();self.wait(state);view=state.snapshot()
  self.assertEqual(view['assistant_frame_id'],'neutral-1');self.assertEqual(view['assistant_target_id'],'42');self.assertGreaterEqual(view['assistant_age_seconds'],0)
 def test_new_session_withholds_old_advice(self):
  state=self.make_state(FakeAdapter(error='offline'));body=frame();state.submit(body);self.wait(state);state.explain();self.wait(state)
  fresh=frame();fresh['session']='new';fresh['frame_id']='new-1';state.submit(fresh);self.wait(state)
  self.assertEqual(state.snapshot()['session'],'new');self.assertEqual(state.snapshot()['assistant_frame_id'],'');self.assertEqual(state.result['frame_id'],'new-1')
if __name__=='__main__':unittest.main(verbosity=2)
