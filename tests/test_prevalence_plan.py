import unittest,math
from jev_pii.core import sample_plan_for_prevalence
class SamplePlanTests(unittest.TestCase):
 def test_single_positive_requires_full_sample_for_five_percent(self):
  x=sample_plan_for_prevalence(10,1,.05);self.assertEqual(x['sample_size'],10);self.assertEqual(x['miss_probability_under_assumption'],0)
 def test_hypergeometric(self):
  x=sample_plan_for_prevalence(20,5,.1);n=x['sample_size'];exact=math.comb(15,n)/math.comb(20,n)if n<=15 else 0;self.assertAlmostEqual(x['miss_probability_under_assumption'],exact);self.assertLessEqual(exact,.1);self.assertGreater(x['previous_size_miss_probability'],.1)
 def test_assumption_not_absence(self):self.assertFalse(sample_plan_for_prevalence(100,10)['absence_certified'])
