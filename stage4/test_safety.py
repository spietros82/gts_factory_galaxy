"""Offline safety/report checks only; no capacity or language inference."""
import json,tempfile,unittest,subprocess,time,sys
from pathlib import Path
from stage4.timing import combined_timings
from stage4.bench import abort_on_guard
from stage4.supervisor import supervise
class Checks(unittest.TestCase):
 def test_known_saved_unit_correction(self):
  rows=[dict(batch_id='a',frame_id='f',line_id='Line01',end_to_end_ms=20)]
  self.assertEqual(combined_timings(rows,[dict(batch_id='a',acquisition_wait_ms=.4)],1000)[0]['trigger_to_result_ms'],420)
 def test_missing_timing_not_invented(self):
  self.assertEqual(combined_timings([dict(batch_id='missing')],[]),[])
 def test_invalid_negative_timing_withheld(self):
  self.assertEqual(combined_timings([dict(batch_id='a')],[dict(batch_id='a',acquisition_wait_ms=-1)]),[])
 def test_operator_stop_aborts_cycle(self):
  self.assertRaises(RuntimeError,abort_on_guard,dict(failure='Operator stop'))
 def test_resource_stop_aborts_cycle(self):
  self.assertRaises(RuntimeError,abort_on_guard,dict(failure='Resource guard: memory'))
 def test_normal_frame_failure_not_guard(self):
  abort_on_guard(dict(passed=False,failure=''))
 def test_supervisor_stops_only_owned_child(self):
  with tempfile.TemporaryDirectory() as d:
   unrelated=subprocess.Popen([sys.executable,'-c','import time; time.sleep(20)'])
   child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(20)','--stage4',d])
   try:
    supervise(child.pid,Path(d),.1);child.wait(5)
    self.assertIsNone(unrelated.poll());self.assertEqual(json.loads((Path(d)/'supervisor-stop.json').read_text())['reason'],'Owned phase duration limit')
   finally:
    for p in [child,unrelated]:
     if p.poll() is None:p.terminate();p.wait(5)
if __name__=='__main__':unittest.main()
