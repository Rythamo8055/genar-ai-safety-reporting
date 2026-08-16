"""
build_slides.py

Generates 4 1080p high-resolution presentation slides using Pillow,
combining system architecture, Streamlit UI preview, and assessment highlights.
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Canvas dimensions
WIDTH, HEIGHT = 1920, 1080

def create_base_canvas(title, subtitle=""):
    img = Image.new("RGB", (WIDTH, HEIGHT), color="#0F172A")
    draw = ImageDraw.Draw(img)
    
    # Top banner gradient line
    draw.rectangle([0, 0, WIDTH, 12], fill="#38BDF8")
    draw.rectangle([0, 12, WIDTH, 16], fill="#818CF8")

    # Header title
    draw.text((80, 70), title, fill="#F8FAFC", font_size=54)
    if subtitle:
        draw.text((80, 140), subtitle, fill="#94A3B8", font_size=28)
        
    # Footer banner
    draw.rectangle([0, HEIGHT - 70, WIDTH, HEIGHT], fill="#1E293B")
    draw.text((80, HEIGHT - 48), "GenAR AI Safety & Regulatory Reporting Platform", fill="#64748B", font_size=22)
    draw.text((WIDTH - 480, HEIGHT - 48), "Candidate: Vishnu Vardhan M | QuickHyre Challenge", fill="#38BDF8", font_size=22)
    
    return img, draw

# Slide 1: Title Slide
img1, draw1 = create_base_canvas("🛡️ GenAR AI Safety & Regulatory Reporting", "Enterprise Pharmacovigilance Platform -- QuickHyre AI Engineering Challenge")

draw1.rectangle([200, 260, WIDTH - 200, 800], fill="#1E293B", outline="#334155", width=2)

draw1.text((250, 310), "CANDIDATE SUBMISSION DEMO & SYSTEM WALKTHROUGH", fill="#38BDF8", font_size=26)
draw1.text((250, 360), "Candidate Name: Vishnu Vardhan M", fill="#F8FAFC", font_size=42)
draw1.text((250, 420), "Target Role: AI Engineer @ QuickHyre", fill="#CBD5E1", font_size=32)

draw1.line([250, 480, WIDTH - 250, 480], fill="#475569", width=2)

bullets1 = [
    "✅ 100% Deterministic Aggregations (Zero LLM Math Hallucination)",
    "✅ Gemma 4 32b Scoped Context Engineering for Regulatory Narratives",
    "✅ Automated Numerical Verifier + Agentic QA Auditor (Fail-Safe)",
    "✅ Interactive Streamlit Human Control Sign-Off Workbench (app.py)",
    "✅ Config-Driven Specification Generalization (FDA PADER & EMA PSUR)"
]

y_pos = 520
for bullet in bullets1:
    draw1.text((250, y_pos), bullet, fill="#F1F5F9", font_size=28)
    y_pos += 52

img1.save("slide1.png")

# Slide 2: Architecture Slide
img2, draw2 = create_base_canvas("🏗️ System Architecture & Hybrid AI Pipeline", "Decoupled Analytical Engine + LLM Narrative Synthesis + Verifier Audit")

boxes = [
    ("Stage 1: Deterministic Engine", "Pandas ICSR Ingestion\nDeduplication & Counts\nMedDRA PT Ranking\n(0% Hallucination Risk)", 80, 260, 480, 750, "#0284C7"),
    ("Stage 2: Scoped Context Builder", "Dynamic Spec Injection\nScoped Prompting\nZero-Shot Safeguards\n(Section Specific)", 530, 260, 930, 750, "#6366F1"),
    ("Stage 3: Gemma 4 32b Engine", "Resilient API Generator\nExponential Backoff\nAsync Parallel Runner\nPaced Token Compliance", 980, 260, 1380, 750, "#8B5CF6"),
    ("Stage 4: Verifier & QA Gate", "Regex Metric Assertion\nSemantic Tuple Check\nAgentic QA Auditor\nHuman Sign-Off Gate", 1430, 260, 1830, 750, "#10B981")
]

for title, desc, x1, y1, x2, y2, color in boxes:
    draw2.rectangle([x1, y1, x2, y2], fill="#1E293B", outline=color, width=3)
    draw2.rectangle([x1, y1, x2, y1 + 60], fill=color)
    draw2.text((x1 + 15, y1 + 15), title, fill="#F8FAFC", font_size=22)
    draw2.text((x1 + 25, y1 + 100), desc, fill="#CBD5E1", font_size=24)

img2.save("slide2.png")

# Slide 3: Streamlit UI Preview Slide
img3, draw3 = create_base_canvas("🖥️ Interactive Streamlit Human Review Dashboard", "Visual Evidence Audit, Live Click-to-Edit Editing & Governance Sign-Off")

# Load existing UI screenshot if available, or build card view
ui_img_path = "/home/rahul/.gemini/antigravity/brain/bc9af827-35df-421c-a313-97ab3362a83a/streamlit_human_review_dashboard_1786874033770.jpg"
if os.path.exists(ui_img_path):
    ui_screenshot = Image.open(ui_img_path).resize((1760, 720))
    img3.paste(ui_screenshot, (80, 230))
else:
    draw3.rectangle([80, 230, WIDTH - 80, 850], fill="#1E293B", outline="#334155", width=2)
    draw3.text((120, 300), "Interactive Streamlit Web Workbench (app.py)", fill="#38BDF8", font_size=36)

img3.save("slide3.png")

# Slide 4: Results & Deliverables Slide
img4, draw4 = create_base_canvas("📋 Multi-Report Generalization & Submission Deliverables", "FDA PADER 21 CFR 314.80 & EMA PSUR Schema Support -- 100% Verified")

draw4.rectangle([100, 250, 920, 820], fill="#1E293B", outline="#334155", width=2)
draw4.text((140, 290), "🧪 Automated Testing & Audit Results", fill="#38BDF8", font_size=30)

res_bullets = [
    "✅ 9 / 9 Unit & Integration Tests Passing",
    "✅ Deterministic Math Verified against Raw ICSR",
    "✅ Verification Rate: 100.0% Grounded Figures",
    "✅ Numerical Swap Detection Engine Active",
    "✅ Zero Hardcoded Strings or Fallback Scores"
]

y_p = 360
for b in res_bullets:
    draw4.text((140, y_p), b, fill="#F1F5F9", font_size=26)
    y_p += 65

draw4.rectangle([980, 250, 1820, 820], fill="#1E293B", outline="#334155", width=2)
draw4.text((1020, 290), "📦 Candidate Deliverables Checklist", fill="#10B981", font_size=30)

deliv_bullets = [
    "📂 Submission Archive: vishnu_vardhan_m_genar_challenge.zip",
    "🌐 Public GitHub Repo: Rythamo8055/genar-ai-safety-reporting",
    "🖥️ Live Deployed Link: quickhyre.streamlit.app",
    "📄 Published Reports: pader_report_output.md / .html",
    "📖 Comprehensive README answering all 7 Questions"
]

y_p2 = 360
for b in deliv_bullets:
    draw4.text((1020, y_p2), b, fill="#F1F5F9", font_size=24)
    y_p2 += 65

img4.save("slide4.png")

print("All 4 slides generated successfully!")
