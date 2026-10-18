import copy
import json
import unittest
from jev_pii.core import scan_columns, preview_plan, FakeJev

class SnapshotTests(unittest.TestCase):
 def test_callback_mutation_does_not_change_plan_bound_local_evidence(self):
  for lang in ('fr','en','es'):
   columns={'a':['ordinary'],'b':['before@example.test']};counts={'a':20,'b':30};expected=preview_plan(columns,lang=lang);calls=[]
   class Mutating:
    def send(self,payload):
     calls.append(payload);columns['b'][:]=['plain','more'];counts['b']=999;columns['c']=['extra']
     return FakeJev().answer
   result=scan_columns(columns,local_only=False,transport=Mutating(),row_counts=counts,lang=lang)
   self.assertEqual(calls,expected['payloads']);self.assertEqual(result['plan_sha256'],expected['plan_sha256'])
   self.assertEqual(len(result['findings']),2);self.assertEqual(result['findings'][1]['row_count'],30)
   self.assertEqual(result['findings'][1]['coverage']['provided_rows'],1);self.assertIn('email',result['findings'][1]['detectors'])
   self.assertNotIn('before@example.test',str(result))
 def test_reused_transport_answers_are_detached(self):
  answer=FakeJev().answer;answer['nested']={'counter':0}
  class Reused:
   def send(self,payload):answer['nested']['counter']+=1;return answer
  result=scan_columns({'a':['one'],'b':['two']},local_only=False,transport=Reused())
  self.assertEqual([r['semantic']['nested']['counter'] for r in result['findings']],[1,2]);answer['nested']['counter']=99
  self.assertEqual(result['findings'][1]['semantic']['nested']['counter'],2)
 def test_local_scan_does_not_modify_supplied_columns(self):
  columns={'x':['plain',None,3]};before=copy.deepcopy(columns);scan_columns(columns)
  self.assertEqual(columns,before)
