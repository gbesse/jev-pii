import unittest,copy,math
from jev_pii.strata import sample_strata
class Strata(unittest.TestCase):
 def test_small_stratum_not_lost_when_budget_allows(self):
  x=sample_strata({'large':1000,'tiny':1},10);self.assertEqual(x['allocation']['tiny'],1);self.assertEqual(x['sampled'],10);self.assertEqual(sum(x['allocation'].values()),10)
 def test_insufficient_budget_exposes_uninspected(self):
  x=sample_strata({'a':100,'b':1},1);self.assertEqual(x['uninspected_nonempty_strata'],['b']);self.assertFalse(x['pii_absence_proven'])
 def test_reproducible_without_replacement(self):
  a=sample_strata({'a':10,'b':4},8,seed=42);self.assertEqual(a,sample_strata({'b':4,'a':10},8,seed=42));self.assertTrue(all(len(v)==len(set(v))for v in a['selected_indices'].values()))
