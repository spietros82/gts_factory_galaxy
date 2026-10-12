import unittest
from factory.activity import display,drm_clients
class ActivityTests(unittest.TestCase):
 def test_loaded_is_not_active(self):
  text,details=display({'loaded_models':[{'name':'example'}]},'',[],'unverified')
  self.assertIn('Language: idle',text);self.assertIn('not necessarily active',text);self.assertNotIn('Language: running',text)
 def test_unknown_metrics_not_zero(self):
  text,_=display({},'',[],'unverified');self.assertIn('GPU busy unavailable',text);self.assertIn('RAM available: unavailable',text)
 def test_process_permissions_not_bypassed(self):
  clients,state=drm_clients(99999999);self.assertEqual(clients,{});self.assertIn('unavailable',state)
