import json,unittest
from jev_pii import scan_columns,diff,coverage_diff
class CoverageDiffTests(unittest.TestCase):
 def test_population_growth_exposes_declining_coverage_even_when_detector_is_unchanged(self):
  a=scan_columns({'contact':['synthetic@example.test']},row_counts={'contact':1});b=scan_columns({'contact':['synthetic@example.test']},row_counts={'contact':100});r=diff(a,b)
  self.assertEqual(r['recategorized'],[]);self.assertEqual(r['coverage_regressions'],['contact']);self.assertEqual(r['coverage_changed'],['contact']);self.assertNotIn('synthetic@example.test',json.dumps(r))
 def test_same_or_improved_fraction_is_not_a_regression(self):
  a=scan_columns({'x':['one']},row_counts={'x':10});b=scan_columns({'x':['one','two']},row_counts={'x':10});self.assertEqual(coverage_diff(a,b)['coverage_regressions'],[]);self.assertEqual(coverage_diff(a,a)['coverage_changed'],[])
 def test_unknown_or_corrupt_metadata_is_unchecked_instead_of_complete(self):
  a=scan_columns({'x':['one']});b=scan_columns({'x':['one']});b['findings'][0]['coverage']['provided_rows']=True;r=coverage_diff(a,b);self.assertEqual(r['coverage_unchecked'],[{'column':'x','side':'after'}]);self.assertEqual(r['coverage_regressions'],[])
 def test_empty_to_nonempty_unobserved_population_is_a_regression(self):
  a=scan_columns({'x':[]});b=scan_columns({'x':[]},row_counts={'x':10});self.assertEqual(coverage_diff(a,b)['coverage_regressions'],['x'])
