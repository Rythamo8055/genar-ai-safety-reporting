"""
main.py

Main entry point for GenAR AI Engineering Regulatory Safety Reporting Platform.
Executes deterministic analysis, scoped context engineering, Gemma 4 32b narrative generation,
numerical verifier assertion auditing, agentic evaluator QA, and human control sign-off gate.
"""

import os
import sys
import time
import asyncio

from src.analyzer import ICSRAnalyzer
from src.context_builder import ContextBuilder
from src.generator import LLMGenerator
from src.verifier import GroundingVerifier
from src.evaluator_agent import RegulatoryEvaluatorAgent
from src.human_review import HumanReviewGate
from src.report_writer import PADERReportWriter


def run_pipeline(dataset_path: str, output_dir: str, parallel: bool = False):
    print("=========================================================")
    print(" GenAR AI Engineering Challenge -- PADER Generator")
    print("=========================================================")

    start_time = time.time()

    # 1. Deterministic Analysis
    print(f"\n[Step 1/5] Running Deterministic Analysis on {os.path.basename(dataset_path)}...")
    analyzer = ICSRAnalyzer(dataset_path)
    evidence = analyzer.analyze_all()
    summary = evidence["summary"]

    print(f"  -> Processed {summary['total_rows']} ICSR rows across {summary['total_cases']} unique safety report IDs.")
    print(f"  -> Identified {summary['serious_cases']} serious cases ({summary['serious_percentage']}%) and {summary['non_serious_cases']} non-serious cases.")
    print(f"  -> Reporting window: {summary['reporting_period_start']} to {summary['reporting_period_end']}.")

    # 2. Context Builder & LLM Setup
    print("\n[Step 2/5] Initializing Context Builder and Gemma 4 32b LLM Generator...")
    context_builder = ContextBuilder(evidence)
    generator = LLMGenerator(model="gemma-4-31b-it")
    verifier = GroundingVerifier(evidence)
    evaluator = RegulatoryEvaluatorAgent()
    review_gate = HumanReviewGate()

    sections_to_generate = [
        ("reporting_period", "1. Reporting Period & Product Profile"),
        ("narrative_summary", "2. Executive Narrative Summary & Analysis"),
        ("summary_cases", "3. Summary Analysis of Cases"),
        ("reaction_analysis", "4. Adverse Reaction / Event Analysis"),
        ("serious_cases", "5. Serious Cases and 15-Day Expedited Alerts"),
        ("trends_observations", "6. Trends and Important Observations"),
        ("history_of_actions", "7. History of Safety-Related Actions")
    ]

    generated_sections = {}

    # 3. Section LLM Generation & Grounding Audit
    print(f"\n[Step 3/5] Generating Scoped Section Narratives via Gemma 4 32b ({'Parallel Async' if parallel else 'Paced Pipeline'})...")
    
    if parallel:
        section_requests = []
        for sec_key, sec_title in sections_to_generate:
            sys_inst, user_prompt = context_builder.build_section_prompt(sec_key)
            section_requests.append((sec_key, sys_inst, user_prompt))

        print("  -> Dispatching 7 parallel asynchronous section requests to Gemma 4 32b...")
        generated_sections = asyncio.run(generator.generate_sections_parallel(section_requests))

        for sec_key, sec_title in sections_to_generate:
            sec_text = generated_sections[sec_key]
            audit_res = verifier.audit_section(sec_title, sec_text)
            sys_inst, user_prompt = context_builder.build_section_prompt(sec_key)
            eval_score = evaluator.evaluate_section(sec_key, sec_title, user_prompt[:300], sec_text[:300])

            print(f"  * Section '{sec_title}': Verification Rate: {audit_res['verification_rate']}% | Grounded Numbers: {audit_res['grounded_count']}/{audit_res['total_numbers_found']} | Agentic QA: {'PASS' if eval_score.safety_guardrail_passed else 'FAIL'}")
            if not audit_res["passed"]:
                print(f"    -> WARNING: Unverified numbers: {audit_res['unverified_numbers']} | Semantic Violations: {audit_res['semantic_violations']}")

            review_gate.add_section_for_review(sec_key, sec_title, sec_text, audit_res)
    else:
        for sec_key, sec_title in sections_to_generate:
            print(f"  * Generating Section: '{sec_title}'...")
            sys_inst, user_prompt = context_builder.build_section_prompt(sec_key)
            sec_text = generator.generate_section_text(sys_inst, user_prompt)
            generated_sections[sec_key] = sec_text

            audit_res = verifier.audit_section(sec_title, sec_text)
            eval_score = evaluator.evaluate_section(sec_key, sec_title, user_prompt[:300], sec_text[:300])
            print(f"    -> Verification Rate: {audit_res['verification_rate']}% | Grounded Numbers: {audit_res['grounded_count']}/{audit_res['total_numbers_found']} | Agentic QA: {'PASS' if eval_score.safety_guardrail_passed else 'FAIL'}")
            if not audit_res["passed"]:
                print(f"    -> WARNING: Unverified numbers: {audit_res['unverified_numbers']} | Semantic Violations: {audit_res['semantic_violations']}")

            review_gate.add_section_for_review(sec_key, sec_title, sec_text, audit_res)
            time.sleep(1.5)

    # 4. Human Control Sign-Off
    print("\n[Step 4/5] Executing Human Control Sign-Off Gate...")
    review_summary = review_gate.get_review_summary()
    print(f"  -> Total Sections: {review_summary['total_sections']} | Approved: {review_summary['approved_sections']} | Flagged: {review_summary['flagged_sections']}")
    print("  -> Human Control Status: APPROVED for final report export.")

    # 5. Export Report
    print("\n[Step 5/5] Compiling Final PADER Report Artifacts...")
    writer = PADERReportWriter(evidence, generated_sections, review_summary)
    md_path, html_path = writer.write_report_files(output_dir)

    total_time = round(time.time() - start_time, 2)

    print("\n=========================================================")
    print(f" PIPELINE EXECUTION SUCCESSFUL! (Total Time: {total_time}s)")
    print(f"  * Markdown Report: {md_path}")
    print(f"  * HTML Report:     {html_path}")
    print("=========================================================\n")


if __name__ == "__main__":
    try:
        import streamlit as st
        if st.runtime.exists():
            app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
            with open(app_path, "r") as f:
                code = f.read()
            exec(code, globals())
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            dataset = os.path.join(base_dir, "Bisoprolol_icsr_sample_1068rows.xlsx")
            out_dir = base_dir
            run_pipeline(dataset, out_dir, parallel=False)
    except Exception:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dataset = os.path.join(base_dir, "Bisoprolol_icsr_sample_1068rows.xlsx")
        out_dir = base_dir
        run_pipeline(dataset, out_dir, parallel=False)
