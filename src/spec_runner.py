"""
src/spec_runner.py

Generic Config-Driven Report Execution Engine for Multi-Report Regulatory Automation.
Loads any JSON Report Specification (PADER, PSUR, DSUR, CSR), dynamically maps evidence
packets, executes Gemma 4 32b generation, audits grounding, runs the Evaluator Agent,
and outputs publishable report artifacts.
"""

import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import ICSRAnalyzer
from src.context_builder import ContextBuilder
from src.generator import LLMGenerator
from src.verifier import GroundingVerifier
from src.human_review import HumanReviewGate
from src.evaluator_agent import RegulatoryEvaluatorAgent
from src.report_writer import PADERReportWriter


class GenericSpecRunner:
    """
    Orchestrates report generation dynamically based on a Report Specification JSON.
    """

    def __init__(self, spec_path: str, dataset_path: str):
        if not os.path.exists(spec_path):
            raise FileNotFoundError(f"Report spec not found: {spec_path}")
        with open(spec_path, "r", encoding="utf-8") as f:
            self.spec = json.load(f)

        self.dataset_path = dataset_path
        self.analyzer = ICSRAnalyzer(dataset_path)
        self.generator = LLMGenerator(model="gemma-4-31b-it")
        self.evaluator = RegulatoryEvaluatorAgent()

    def run(self, output_dir: str):
        print("=========================================================")
        print(f" GENERIC REGULATORY REPORT ENGINE: {self.spec['report_title']}")
        print(f" Framework: {self.spec['regulatory_framework']}")
        print("=========================================================")

        # 1. Deterministic Analysis
        print("\n[Step 1/5] Executing Deterministic Data Analysis...")
        evidence = self.analyzer.analyze_all()
        builder = ContextBuilder(evidence)
        verifier = GroundingVerifier(evidence)
        review_gate = HumanReviewGate()

        generated_sections = {}

        # 2. Dynamic Section Processing
        print(f"\n[Step 2/5] Processing {len(self.spec['sections'])} Sections from Spec...")
        for sec in self.spec["sections"]:
            sec_id = sec["section_id"]
            sec_title = sec["title"]
            prompt_key = sec["prompt_key"]

            print(f"\n  * Executing Section [{sec_id}]: '{sec_title}'...")
            sys_inst, user_prompt = builder.build_section_prompt(prompt_key)

            # LLM Generation
            sec_text = self.generator.generate_section_text(sys_inst, user_prompt)
            generated_sections[sec_id] = sec_text

            # Deterministic Numerical Audit
            audit_res = verifier.audit_section(sec_title, sec_text)
            print(f"    -> Verification Rate: {audit_res['verification_rate']}% ({audit_res['grounded_count']}/{audit_res['total_numbers_found']} numbers grounded)")

            # Agentic Evaluator Audit
            eval_score = self.evaluator.evaluate_section(sec_id, sec_title, user_prompt[:300], sec_text[:300])
            print(f"    -> Agentic QA Score: Grounding {eval_score.grounding_score}/5 | Tone {eval_score.regulatory_tone_score}/5 | Safety Check: {'PASS' if eval_score.safety_guardrail_passed else 'FAIL'}")

            # Register in Review Gate
            review_gate.add_section_for_review(sec_id, sec_title, sec_text, audit_res)

        # 3. Human Control Sign-Off
        print("\n[Step 3/5] Executing Human Control Sign-Off Gate...")
        review_summary = review_gate.get_review_summary()
        print(f"  -> Total Sections: {review_summary['total_sections']} | Approved: {review_summary['approved_sections']} | Flagged: {review_summary['flagged_sections']}")

        # 4. Report Compilation
        print("\n[Step 4/5] Compiling & Exporting Report Artifacts...")
        writer = PADERReportWriter(evidence, generated_sections, review_summary)
        md_path, html_path = writer.write_report_files(output_dir)

        print("\n=========================================================")
        print(" REPORT SPECIFICATION GENERATION COMPLETE!")
        print(f"  * Output Markdown: {md_path}")
        print(f"  * Output HTML:     {html_path}")
        print("=========================================================\n")


if __name__ == "__main__":
    spec = "/home/rahul/development_walkins/challenge from company/specs/pader_spec.json"
    dataset = "/home/rahul/development_walkins/challenge from company/Bisoprolol_icsr_sample_1068rows.xlsx"
    out = "/home/rahul/development_walkins/challenge from company"
    runner = GenericSpecRunner(spec, dataset)
    runner.run(out)
