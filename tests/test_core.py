# Purpose: Verify detectors, privacy controls, sampling and inventory changes.
import unittest
from jev_pii import *
class Tests(unittest.TestCase):
 def test_checksums(self):
  self.assertTrue(luhn('4111 1111 1111 1111'));self.assertFalse(luhn('4111 1111 1111 1112'));self.assertTrue(iban('GB82 WEST 1234 5698 7654 32'));self.assertFalse(iban('GB82 WEST 1234 5698 7654 31'))
 def test_detectors_and_near_miss(self):
  self.assertIn('email',detect('a@example.test'));self.assertNotIn('email',detect('a@x'));self.assertIn('payment_card',detect('4111111111111111'))
 def test_read_only(self):
  with self.assertRaises(PermissionError):assert_read_only(type('C',(),{'read_only':False})())
 def test_sampling_reproducible(self):self.assertEqual(sample_column(range(100),5,3),sample_column(range(100),5,3))
 def test_exact_dry_run_local_and_mask(self):
  class Fail:
   def send(self,p):raise AssertionError('socket opened')
  self.assertEqual(scan_columns({'x':['a@b.co']},local_only=True,transport=Fail())['payloads'],[])
  expected=payload_for('x',['a@b.co'],20,7,True);r=scan_columns({'x':['a@b.co']},local_only=False,dry_run=True,mask=True);self.assertEqual(r['payloads'],[expected]);self.assertIn('a***@b.co',expected.decode())
 def test_diff(self):
  a={'findings':[{'column':'a','detectors':['email']},{'column':'b','detectors':[]}]};b={'findings':[{'column':'a','detectors':['phone']},{'column':'c','detectors':[]}]};self.assertEqual(diff(a,b),{'added':['c'],'removed':['b'],'recategorized':['a']})
if __name__=='__main__':unittest.main()
