# Purpose: Verify detectors, privacy controls, sampling and inventory changes.
import unittest
from jev_pii import *


class Tests(unittest.TestCase):
    def test_checksums(self):
        self.assertTrue(luhn("4111 1111 1111 1111"))
        self.assertFalse(luhn("4111 1111 1111 1112"))
        self.assertTrue(iban("GB82 WEST 1234 5698 7654 32"))
        self.assertFalse(iban("GB82 WEST 1234 5698 7654 31"))

    def test_detectors_and_near_miss(self):
        self.assertIn("email", detect("a@example.test"))
        self.assertNotIn("email", detect("a@x"))
        self.assertIn("payment_card", detect("4111111111111111"))

    def test_read_only(self):
        with self.assertRaises(PermissionError):
            assert_read_only(type("C", (), {"read_only": False})())

    def test_sampling_reproducible(self):
        self.assertEqual(
            sample_column(range(100), 5, 3), sample_column(range(100), 5, 3)
        )

    def test_exact_dry_run_local_and_mask(self):
        class Fail:
            def send(self, p):
                raise AssertionError("socket opened")

        self.assertEqual(
            scan_columns({"x": ["a@b.co"]}, local_only=True, transport=Fail())[
                "payloads"
            ],
            [],
        )
        expected = payload_for("x", ["a@b.co"], 20, 7, True)
        r = scan_columns({"x": ["a@b.co"]}, local_only=False, dry_run=True, mask=True)
        self.assertEqual(r["payloads"], [expected])
        self.assertIn("a***@b.co", expected.decode())

    def test_diff(self):
        a = {
            "findings": [
                {"column": "a", "detectors": ["email"]},
                {"column": "b", "detectors": []},
            ]
        }
        b = {
            "findings": [
                {"column": "a", "detectors": ["phone"]},
                {"column": "c", "detectors": []},
            ]
        }
        self.assertEqual(
            diff(a, b), {"added": ["c"], "removed": ["b"], "recategorized": ["a"], "coverage_changed": [], "coverage_regressions": [], "coverage_unchecked": [{"column":"a","side":"before"},{"column":"a","side":"after"}]}
        )


class CoverageTests(unittest.TestCase):
    def test_counts_rows_and_matches_without_values(self):
        result=scan_columns({"contact": ["a@example.test", "b@example.test", None, "", "ordinary"]}, row_counts={"contact": 50})
        finding=result['findings'][0]
        self.assertEqual(finding['row_count'],50)
        self.assertEqual(finding['coverage'],{'provided_rows':5,'nonempty_rows':3,'matched_rows':2,'detector_counts':{'email':2},'semantic_sample_count':0})
        self.assertNotIn('a@example.test',str(result))

    def test_overlapping_detectors_count_one_matching_row(self):
        result=scan_columns({'number':['4111111111111111']})['findings'][0]['coverage']
        self.assertEqual(result['matched_rows'],1)
        self.assertEqual(result['detector_counts']['payment_card'],1)
        self.assertGreaterEqual(sum(result['detector_counts'].values()),1)

    def test_semantic_sample_count_is_plan_bound_in_all_languages(self):
        for lang in ('fr','en','es'):
            result=scan_columns({'x':['one','two','three',None,'']},local_only=False,dry_run=True,sample_size=2,lang=lang)
            self.assertEqual(result['findings'][0]['coverage']['semantic_sample_count'],2)
            self.assertEqual(result['findings'][0]['coverage']['provided_rows'],5)

    def test_bad_population_counts_block_before_transport(self):
        class Fail:
            def send(self,payload):raise AssertionError('must not call')
        for counts in ({'x':0},{'x':True},{'x':1.5},{'other':20}):
            with self.assertRaises(ValueError):scan_columns({'x':['one']},row_counts=counts,local_only=False,transport=Fail())

if __name__ == "__main__":
    unittest.main()
