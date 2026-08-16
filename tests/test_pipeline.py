"""
tests/test_pipeline.py

Automated Test Suite for Regulatory Safety Report Generation Pipeline.
Executes unit and integration tests across data analysis, context building,
verifier auditing, human control gate, evaluator agent, and spec runner.
"""

import sys
import os
import unittest

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import ICSRAnalyzer
from src.context_builder import ContextBuilder
from src.verifier import GroundingVerifier
from src.human_review import HumanReviewGate
from src.evaluator_agent import RegulatoryEvaluatorAgent
from src.spec_runner import GenericSpecRunner


class TestPADERPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dataset_path = "/home/rahul/development_walkins/challenge from company/Bisoprolol_icsr_sample_1068rows.xlsx"
        cls.spec_path = "/home/rahul/development_walkins/challenge from company/specs/pader_spec.json"
        cls.analyzer = ICSRAnalyzer(cls.dataset_path)
        cls.evidence = cls.analyzer.analyze_all()

    def test_case_deduplication(self):
        summary = self.evidence["summary"]
        self.assertEqual(summary["total_rows"], 1068)
        self.assertEqual(summary["total_cases"], 1024)

    def test_serious_counts(self):
        summary = self.evidence["summary"]
        self.assertEqual(summary["serious_cases"], 1023)
        self.assertEqual(summary["non_serious_cases"], 1)
        self.assertAlmostEqual(summary["serious_percentage"], 99.9, places=1)

    def test_reporting_period_dates(self):
        summary = self.evidence["summary"]
        self.assertEqual(summary["reporting_period_start"], "2024-12-27")
        self.assertEqual(summary["reporting_period_end"], "2025-12-26")

    def test_top_reactions(self):
        reactions = self.evidence["reactions"]["top_reactions"]
        self.assertTrue(len(reactions) > 0)
        self.assertEqual(reactions[0]["reaction_pt"], "Acute kidney injury")
        self.assertEqual(reactions[0]["case_count"], 22)

    def test_context_builder(self):
        builder = ContextBuilder(self.evidence)
        sys_inst, user_prompt = builder.build_section_prompt("narrative_summary")
        self.assertIn("1024", user_prompt)
        self.assertIn("1023", user_prompt)

    def test_verifier_grounding(self):
        verifier = GroundingVerifier(self.evidence)
        sample_text = "During the reporting period, 1,024 cases were received, of which 1,023 (99.9%) were serious."
        res = verifier.audit_section("Test Section", sample_text)
        self.assertTrue(res["passed"])
        self.assertEqual(res["verification_rate"], 100.0)

    def test_verifier_hallucination_flagging(self):
        verifier = GroundingVerifier(self.evidence)
        sample_text = "There were 99999 fake cases in the report."
        res = verifier.audit_section("Fake Section", sample_text)
        self.assertIn("99999", res["unverified_numbers"])

    def test_human_review_gate(self):
        gate = HumanReviewGate()
        gate.add_section_for_review("sec1", "Title 1", "Text 1", {"passed": True, "verification_rate": 100.0})
        summary = gate.get_review_summary()
        self.assertEqual(summary["total_sections"], 1)
        self.assertEqual(summary["approved_sections"], 1)
        self.assertTrue(summary["all_passed"])

    def test_generic_spec_runner_init(self):
        runner = GenericSpecRunner(self.spec_path, self.dataset_path)
        self.assertEqual(runner.spec["report_type"], "PADER")
        self.assertEqual(len(runner.spec["sections"]), 7)


if __name__ == "__main__":
    unittest.main()
