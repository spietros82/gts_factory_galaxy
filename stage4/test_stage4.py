"""Offline/fake checks. No locked-set evaluation or Ollama call."""
import base64,copy,json,tempfile,time,unittest,uuid,threading
from pathlib import Path
from datetime import datetime,timezone,timedelta
from io import BytesIO
from PIL import Image
from stage4.service import Engine
from stage3.service import validate_batch

class Fake:
 cold_start_ms=0
 def __init__(self):self.entered=threading.Event();self.release=threading.Event();self.release.set();self.visits=[]
 def predict(self,station,image):
  self.visits.append(station);self.entered.set();self.release.wait(3)
  return dict(decision='aligned' if station!='fill' else 'within_range',wording='Fake test result',reason='fake',score=.9,device='cpu',backend='fake/test',model_sha256='test',preprocess_ms=0,transfer_ms=0,inference_ms=0,gpu_elapsed_ms=0,classifier_ms=0)
def batch(line='Line01',session='s1',age=0,target=1):
 image=Image.new('RGB',(256,256),(110,130,150));b=BytesIO();image.save(b,format='PNG');encoded=base64.b64encode(b.getvalue()).decode()
 return dict(contract='gts.three-frame/1',line_id=line,session_id=session,bottle_id='1',batch_id=uuid.uuid4().hex,capture_utc=(datetime.now(timezone.utc)-timedelta(seconds=age)).isoformat(),product='LAGER',source_time=40.,target_count=target,observations_available=True,frames=[dict(station_id=s,frame_id=uuid.uuid4().hex,image=encoded,roi=[48,48,160,160]) for s in ['cap','fill','label']])
def wait(fn):
 for _ in range(500):
  if fn():return
  time.sleep(.005)
 raise AssertionError('Timed out')
class Checks(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.cfg=json.loads(Path('stage4/config.example.json').read_text());self.cfg.update(data_path=self.tmp.name,assistant_ledger=self.tmp.name+'/never-called.jsonl',monitoring=False,image_limit=6,audit_segment_bytes=512,audit_segments=3);self.fake=Fake();self.e=Engine(self.cfg,{'cpu':self.fake});wait(lambda:self.e.ready);self.addCleanup(lambda:(self.fake.release.set(),wait(lambda:not self.e.busy)));self.e.register([dict(line_id='Line01',session_id='s1'),dict(line_id='Line02',session_id='s2')])
 def test_trigger_latency_join(self):
  v=batch();self.e.submit(v);wait(lambda:not self.e.busy)
  self.e.heartbeat({'capture_timings':[{'batch_id':v['batch_id'],'acquisition_wait_ms':250.}]})
  self.assertEqual(self.e.view()['trigger_timing_samples'],3)
  self.assertGreaterEqual(self.e.view()['trigger_to_result_p95_ms'],250)
  self.e.heartbeat({'capture_timings':[{'batch_id':v['batch_id'],'acquisition_wait_ms':250.}]})
  self.assertEqual(self.e.view()['trigger_timing_samples'],3)
 def test_unavailable_backend_status(self):
  self.e.backends={};self.e.submit(batch());wait(lambda:not self.e.busy)
  self.assertEqual(self.e.view()['status'],'unavailable');self.assertTrue(all(r['decision']=='uncertain' for r in self.e.records))
 def test_line_rate_uses_registration_interval(self):
  self.e.started-=1000;self.e.submit(batch());wait(lambda:not self.e.busy)
  line=self.e.view()['lines'][0];self.assertLess(line['rate_elapsed_seconds'],2);self.assertGreater(line['inspection_rate'],1)
  self.assertAlmostEqual(line['inspection_rate']*line['rate_elapsed_seconds'],3,delta=.1)
 def test_line_inspection_health(self):
  self.assertEqual(self.e.view()['lines'][0]['inspection_health'],'Waiting')
  self.e.submit(batch(target=2));wait(lambda:not self.e.busy);self.assertEqual(self.e.view()['lines'][0]['inspection_health'],'Uncertain')
  self.e.submit(batch());wait(lambda:not self.e.busy);self.assertEqual(self.e.view()['lines'][0]['inspection_health'],'Current')
  self.e.native={'paused':True};self.assertEqual(self.e.view()['lines'][0]['inspection_health'],'Historical')
  self.e.native={'inspection':False};self.assertEqual(self.e.view()['lines'][0]['inspection_health'],'Off')
 def test_session_isolation(self):
  self.e.submit(batch());self.e.submit(batch('Line02','s2'));wait(lambda:self.e.counts['completed']==6);self.assertEqual(len(self.e.view('Line01')['results']),3);self.assertTrue(all(r['line_id']=='Line02' for r in self.e.view('Line02')['results']))
 def test_retired_result_not_current(self):
  self.fake.release.clear();self.e.submit(batch());wait(self.fake.entered.is_set);self.e.register([dict(line_id='Line01',session_id='new')]);self.fake.release.set();wait(lambda:not self.e.busy);self.assertEqual(self.e.view('Line01')['results'],[]);self.assertEqual(self.e.counts['cancelled'],3)
 def test_removed_submission_rejected(self):
  self.e.register([dict(line_id='Line01',session_id='s1')]);self.assertRaises(ValueError,self.e.submit,batch('Line02','s2'))
 def test_unknown_not_pass(self):
  self.e.submit(batch(target=2));wait(lambda:self.e.counts['completed']==3);self.assertTrue(all(r['decision']=='uncertain' for r in self.e.records));self.assertEqual(self.fake.visits,[])
 def test_stale_withheld(self):
  self.e.submit(batch(age=5));wait(lambda:self.e.counts['completed']==3);self.assertEqual(self.e.counts['stale'],3);self.assertTrue(all(r['decision']=='uncertain' for r in self.e.records))
 def test_missing_withheld(self):
  v=batch();v['observations_available']=False;self.e.submit(v);wait(lambda:self.e.counts['completed']==3);self.assertEqual(self.fake.visits,[])
 def test_duplicate_rejected(self):
  v=batch();self.e.submit(v);self.assertRaises(ValueError,self.e.submit,v)
 def test_frame_identity_reserved_across_lines(self):
  self.fake.release.clear();first=batch();self.e.submit(first);wait(self.fake.entered.is_set)
  other=batch('Line02','s2');other['frames']=copy.deepcopy(first['frames']);self.assertRaises(ValueError,self.e.submit,other)
 def test_hidden_truth_rejected(self):
  v=batch();v['expected_class']='aligned';self.assertRaises(ValueError,validate_batch,v)
 def test_bounded_and_fair(self):
  self.fake.release.clear();self.e.submit(batch());wait(self.fake.entered.is_set);self.assertRaises(ValueError,self.e.submit,batch());self.e.submit(batch('Line02','s2'));self.fake.release.set();wait(lambda:self.e.counts['completed']==6);self.assertEqual([r['line_id'] for r in self.e.records],['Line01']*3+['Line02']*3);self.assertEqual(self.e.counts['dropped'],3)
 def test_no_gpu_fallback(self):self.assertRaises(ValueError,self.e.switch,'gpu');self.assertEqual(self.e.selected,'cpu')
 def test_switch_only_batches(self):self.e.backends['gpu']=self.fake;self.e.switch('gpu');self.assertEqual(self.e.selected,'gpu')
 def test_image_and_audit_limits(self):
  for _ in range(5):self.e.submit(batch());wait(lambda:not self.e.busy)
  self.assertEqual(len(list((Path(self.tmp.name)/'frames').glob('*.png'))),6);self.assertLessEqual(len(list(Path(self.tmp.name).glob('results.jsonl*'))),3)
 def test_no_qwen_in_benchmark(self):
  self.e.native={'benchmark':True};self.assertRaises(ValueError,self.e.explain,'anything');self.assertFalse(Path(self.cfg['assistant_ledger']).exists())
 def test_registry_guard(self):self.assertRaises(ValueError,self.e.register,[]);self.assertRaises(ValueError,self.e.register,[dict(line_id='L'+str(i),session_id='s'+str(i)) for i in range(49)])
 def test_pause_history(self):
  self.e.submit(batch());wait(lambda:self.e.counts['completed']==3);self.e.native={'paused':True};self.assertTrue(all(r['historical'] for r in self.e.view('Line01')['results']))
 def test_reset_not_erasure(self):
  self.e.submit(batch());wait(lambda:not self.e.busy);self.e.register([dict(line_id='Line01',session_id='new')]);self.assertEqual(len(self.e.records),3);self.assertEqual(self.e.view('Line01')['results'],[])
if __name__=='__main__':unittest.main()
