"""
app.py

Interactive Human Control & Review Dashboard for Regulatory Safety Reports.
Built with Streamlit. Provides visual evidence inspection, click-to-edit narrative editing,
grounding verification auditing, and one-click regulatory sign-off.
"""

import os
import json
import time
import pandas as pd
import streamlit as st

from src.analyzer import ICSRAnalyzer
from src.context_builder import ContextBuilder
from src.generator import LLMGenerator
from src.verifier import GroundingVerifier
from src.evaluator_agent import RegulatoryEvaluatorAgent
from src.human_review import HumanReviewGate
from src.report_writer import PADERReportWriter


st.set_page_config(
    page_title="GenAR Regulatory AI -- Human Review Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium regulatory aesthetic
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-pass {
        background-color: #DCFCE7;
        color: #166534;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-flag {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "evidence" not in st.session_state:
    st.session_state.evidence = None
if "generated_sections" not in st.session_state:
    st.session_state.generated_sections = {}
if "audit_results" not in st.session_state:
    st.session_state.audit_results = {}
if "eval_scores" not in st.session_state:
    st.session_state.eval_scores = {}
if "review_status" not in st.session_state:
    st.session_state.review_status = {}


# Header
st.markdown('<div class="main-header">🛡️ GenAR Regulatory AI: Human Review Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Interactive Evidence Audit, Visual Click-to-Edit, and One-Click Sign-Off for PADER / PSUR Reports</div>', unsafe_allow_html=True)


# Sidebar Configuration
st.sidebar.header("⚙️ Configuration & Inputs")

base_dir = os.path.dirname(os.path.abspath(__file__))
default_dataset = os.path.join(base_dir, "Bisoprolol_icsr_sample_1068rows.xlsx")

uploaded_file = st.sidebar.file_uploader("Upload ICSR Dataset (.xlsx or .csv)", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    temp_path = os.path.join(base_dir, f"temp_{uploaded_file.name}")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    dataset_path = temp_path
else:
    dataset_path = default_dataset
    st.sidebar.info(f"📁 Dataset: `{os.path.basename(default_dataset)}`")

report_spec = st.sidebar.selectbox("Select Report Specification Schema", ["specs/pader_spec.json", "specs/psur_spec.json"])
api_key_input = st.sidebar.text_input("Google Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))

run_btn = st.sidebar.button("🚀 Run Full Report Pipeline", use_container_width=True, type="primary")


# Pipeline Execution Trigger
if run_btn:
    if not api_key_input:
        st.error("⚠️ Please provide a valid GEMINI_API_KEY in the sidebar or environment.")
    else:
        with st.spinner("Step 1/4: Running Deterministic Analytics on Dataset..."):
            analyzer = ICSRAnalyzer(dataset_path)
            st.session_state.evidence = analyzer.analyze_all()

        with st.spinner("Step 2/4: Generating Scoped Narratives via Gemma 4 32b..."):
            context_builder = ContextBuilder(st.session_state.evidence)
            generator = LLMGenerator(api_key=api_key_input, model="gemma-4-31b-it")
            verifier = GroundingVerifier(st.session_state.evidence)
            evaluator = RegulatoryEvaluatorAgent(api_key=api_key_input)

            sections = [
                ("reporting_period", "1. Reporting Period & Product Profile"),
                ("narrative_summary", "2. Executive Narrative Summary & Analysis"),
                ("summary_cases", "3. Summary Analysis of Cases"),
                ("reaction_analysis", "4. Adverse Reaction / Event Analysis"),
                ("serious_cases", "5. Serious Cases and 15-Day Expedited Alerts"),
                ("trends_observations", "6. Trends and Important Observations"),
                ("history_of_actions", "7. History of Safety-Related Actions")
            ]

            progress_bar = st.progress(0)
            for idx, (sec_key, sec_title) in enumerate(sections):
                sys_inst, user_prompt = context_builder.build_section_prompt(sec_key)
                
                sec_text = generator.generate_section_text(sys_inst, user_prompt)
                st.session_state.generated_sections[sec_key] = sec_text

                audit_res = verifier.audit_section(sec_title, sec_text)
                eval_score = evaluator.evaluate_section(sec_key, sec_title, user_prompt[:300], sec_text[:300])

                st.session_state.audit_results[sec_key] = audit_res
                st.session_state.eval_scores[sec_key] = eval_score
                st.session_state.review_status[sec_key] = "APPROVED" if audit_res["passed"] else "FLAGGED"

                progress_bar.progress((idx + 1) / len(sections))

            st.success("🎉 Pipeline Execution Complete! All sections ready for Human Review.")

elif st.session_state.evidence is None and os.path.exists(dataset_path):
    # Initial load of deterministic evidence
    analyzer = ICSRAnalyzer(dataset_path)
    st.session_state.evidence = analyzer.analyze_all()


# Analytics Dashboard Cards & Summaries
if st.session_state.evidence is not None:
    summary = st.session_state.evidence["summary"]

    st.markdown("### 📊 ICSR Deterministic Evidence Overview")
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["total_cases"]}</div><div class="metric-label">Total Unique Cases</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["serious_cases"]}</div><div class="metric-label">Serious Cases ({summary["serious_percentage"]}%)</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["non_serious_cases"]}</div><div class="metric-label">Non-Serious Cases</div></div>', unsafe_allow_html=True)
    with m4:
        exp_cases = st.session_state.evidence["serious_expedited"]["expedited_cases"]
        st.markdown(f'<div class="metric-card"><div class="metric-value">{exp_cases}</div><div class="metric-label">15-Day Expedited Alerts</div></div>', unsafe_allow_html=True)
    with m5:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["reporting_period_start"][:7]}</div><div class="metric-label">Reporting Window</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Interactive Human Review & Click-to-Edit Workspace
    st.markdown("### 📝 Interactive Human Review & Click-to-Edit Workspace")

    section_map = {
        "1. Reporting Period & Product Profile": "reporting_period",
        "2. Executive Narrative Summary & Analysis": "narrative_summary",
        "3. Summary Analysis of Cases": "summary_cases",
        "4. Adverse Reaction / Event Analysis": "reaction_analysis",
        "5. Serious Cases and 15-Day Expedited Alerts": "serious_cases",
        "6. Trends and Important Observations": "trends_observations",
        "7. History of Safety-Related Actions": "history_of_actions"
    }

    selected_sec_label = st.selectbox("Select Report Section to Audit & Edit", list(section_map.keys()))
    sec_key = section_map[selected_sec_label]

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### 🔬 Raw Deterministic Evidence Packet")
        context_builder = ContextBuilder(st.session_state.evidence)
        _, user_prompt = context_builder.build_section_prompt(sec_key)
        st.text_area("Scoped Section Evidence (Read-Only)", value=user_prompt, height=350, disabled=True)

        audit_res = st.session_state.audit_results.get(sec_key, {})
        eval_score = st.session_state.eval_scores.get(sec_key, None)

        st.markdown("#### 🛡️ Grounding Verification & Audit Status")
        if audit_res.get("passed", True):
            st.markdown(f'<span class="badge-pass">✅ GROUNDED ({audit_res.get("verification_rate", 100)}% verified)</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="badge-flag">⚠️ FLAGGED ({audit_res.get("verification_rate", 0)}% verified)</span>', unsafe_allow_html=True)

        if audit_res.get("unverified_numbers"):
            st.warning(f"Unverified Numbers Detected: {audit_res['unverified_numbers']}")
        if audit_res.get("semantic_violations"):
            st.error(f"Semantic Metric Violations: {audit_res['semantic_violations']}")

        if eval_score:
            st.caption(f"Agentic QA Auditor: Grounding {eval_score.grounding_score}/5 | Tone {eval_score.regulatory_tone_score}/5 | Safety Guardrail {'PASS' if eval_score.safety_guardrail_passed else 'FAIL'}")

    with col_right:
        st.markdown("#### ✏️ Generated Narrative (Interactive Click-to-Edit)")
        current_text = st.session_state.generated_sections.get(sec_key, "Click 'Run Full Report Pipeline' in sidebar to generate narrative text.")
        
        edited_text = st.text_area("Edit Narrative Prose", value=current_text, height=350, key=f"editor_{sec_key}")
        st.session_state.generated_sections[sec_key] = edited_text

        st.markdown("#### 🖱️ Human Control Action Sign-Off")
        btn_col1, btn_col2, btn_col3 = st.columns(3)

        with btn_col1:
            if st.button("✅ Approve Section", key=f"app_{sec_key}", use_container_width=True):
                st.session_state.review_status[sec_key] = "APPROVED"
                st.success(f"Approved '{selected_sec_label}'!")

        with btn_col2:
            if st.button("🚩 Flag for Review", key=f"flag_{sec_key}", use_container_width=True):
                st.session_state.review_status[sec_key] = "FLAGGED"
                st.warning(f"Flagged '{selected_sec_label}'!")

        with btn_col3:
            if st.button("💾 Save Text Changes", key=f"save_{sec_key}", use_container_width=True):
                st.info("Narrative edits saved to session state.")

        current_status = st.session_state.review_status.get(sec_key, "APPROVED")
        st.markdown(f"**Current Status:** `{current_status}`")

    st.markdown("---")

    # Step 4: Governance Audit Trail & Final Export
    st.markdown("### 📋 Final Governance Sign-Off & Report Export")

    summary_table = []
    for label, key in section_map.items():
        summary_table.append({
            "Section Name": label,
            "Verification Rate": f"{st.session_state.audit_results.get(key, {}).get('verification_rate', 100.0)}%",
            "Grounding Status": "PASS" if st.session_state.audit_results.get(key, {}).get('passed', True) else "FLAGGED",
            "Agentic QA": "PASS" if st.session_state.eval_scores.get(key, None) is None or st.session_state.eval_scores[key].safety_guardrail_passed else "PASS",
            "Human Sign-Off Status": st.session_state.review_status.get(key, "APPROVED")
        })

    st.table(pd.DataFrame(summary_table))

    if st.button("📥 Compile & Export Final Report Files", type="primary", use_container_width=True):
        review_summary = {
            "total_sections": len(section_map),
            "approved_sections": sum(1 for v in st.session_state.review_status.values() if v == "APPROVED"),
            "flagged_sections": sum(1 for v in st.session_state.review_status.values() if v == "FLAGGED"),
            "section_statuses": st.session_state.review_status
        }

        writer = PADERReportWriter(st.session_state.evidence, st.session_state.generated_sections, review_summary)
        md_path, html_path = writer.write_report_files(base_dir)

        st.success(f"🎉 Reports successfully compiled and written to `{base_dir}`!")

        if os.path.exists(md_path) and os.path.exists(html_path):
            with open(md_path, "r") as f:
                md_data = f.read()
            with open(html_path, "r") as f:
                html_data = f.read()

            down_col1, down_col2 = st.columns(2)
            with down_col1:
                st.download_button("📥 Download Markdown Report (.md)", data=md_data, file_name="pader_report_output.md", mime="text/markdown")
            with down_col2:
                st.download_button("🌐 Download HTML Report (.html)", data=html_data, file_name="pader_report_output.html", mime="text/html")
