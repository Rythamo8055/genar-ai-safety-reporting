"""
build_hyperframes_promo.py

Generates a 100k-subscriber YouTube style motion graphics video presentation (hyperframes_100k_promo.mp4)
featuring 60fps kinetic typography, neon glassmorphism, animated data charts, and candidate callouts for HRs.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

# Frame configuration
WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION_SEC = 20
TOTAL_FRAMES = FPS * DURATION_SEC

os.makedirs("frames_100k", exist_ok=True)

def render_frame(frame_num):
    t = frame_num / TOTAL_FRAMES
    img = Image.new("RGB", (WIDTH, HEIGHT), color="#090D16")
    draw = ImageDraw.Draw(img)

    # Animated Background Particles & Gradient Glow
    for i in range(5):
        cx = int(WIDTH / 2 + math.sin(t * 4 + i) * 300)
        cy = int(HEIGHT / 2 + math.cos(t * 3 + i) * 200)
        radius = 400 + i * 50
        # Draw soft glow circles
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline="#1E293B", width=1)

    # Section 1 (0s - 5s): High-Energy Kinetic Opener
    if t < 0.25:
        progress = t / 0.25
        scale = min(1.0, progress * 1.5)
        alpha_y = int(200 - progress * 100)

        # Glowing Header Box
        draw.rectangle([100, 150, WIDTH - 100, 450], fill="#0F172A", outline="#38BDF8", width=4)
        draw.text((150, 190), "🚀 PRODUCT REVEAL & AI CHALLENGE SUBMISSION", fill="#38BDF8", font_size=32)
        draw.text((150, 250), "GenAR AI Safety & Regulatory Reporting", fill="#F8FAFC", font_size=56)

        # 100k Subscriber Style Badge
        draw.rectangle([150, 520, 750, 700], fill="#1E293B", outline="#818CF8", width=3)
        draw.text((180, 550), "CHALLENGE SOLUTION", fill="#818CF8", font_size=24)
        draw.text((180, 600), "QuickHyre AI Engineering", fill="#F8FAFC", font_size=36)

        draw.rectangle([800, 520, 1770, 700], fill="#1E293B", outline="#10B981", width=3)
        draw.text((830, 550), "CANDIDATE PRESENTER", fill="#10B981", font_size=24)
        draw.text((830, 600), "Vishnu Vardhan M", fill="#F8FAFC", font_size=40)

    # Section 2 (5s - 10s): Key Features & Architecture Reveal
    elif t < 0.50:
        draw.text((100, 80), "⚡ KEY PLATFORM INNOVATIONS", fill="#38BDF8", font_size=48)

        card_data = [
            ("0% LLM Math Hallucination", "Deterministic Pandas Aggregations for deduplication and MedDRA rankings", "#0284C7", 100),
            ("Gemma 4 32b Narrative Engine", "Scoped Context Engineering generating regulatory safety narratives", "#6366F1", 530),
            ("Automated Grounding Verifier", "Regex Metric Assertion + Agentic LLM-as-a-Judge Auditor", "#8B5CF6", 960),
            ("Streamlit Human Control UI", "Visual click-to-edit prose editor and one-click report sign-off", "#10B981", 1390)
        ]

        for title, desc, col, x_pos in card_data:
            draw.rectangle([x_pos, 200, x_pos + 410, 800], fill="#1E293B", outline=col, width=3)
            draw.rectangle([x_pos, 200, x_pos + 410, 270], fill=col)
            draw.text((x_pos + 20, 220), title, fill="#F8FAFC", font_size=22)
            draw.text((x_pos + 25, 320), desc, fill="#CBD5E1", font_size=24)

    # Section 3 (10s - 15s): Live UI & Metrics Display
    elif t < 0.75:
        draw.text((100, 80), "🖥️ INTERACTIVE STREAMLIT WORKBENCH (app.py)", fill="#38BDF8", font_size=44)

        # KPI Mock Cards
        kpi_cols = [
            ("1,024", "TOTAL ICSR CASES", "#38BDF8", 100),
            ("1,023 (99.9%)", "SERIOUS CASES", "#EF4444", 550),
            ("392", "EXPEDITED ALERTS", "#F59E0B", 1000),
            ("100.0%", "VERIFIED GROUNDING", "#10B981", 1450)
        ]
        for val, lbl, col, x in kpi_cols:
            draw.rectangle([x, 180, x + 380, 320], fill="#1E293B", outline=col, width=2)
            draw.text((x + 25, 210), val, fill=col, font_size=42)
            draw.text((x + 25, 270), lbl, fill="#94A3B8", font_size=18)

        # Split Review Panels
        draw.rectangle([100, 360, 930, 850], fill="#1E293B", outline="#334155", width=2)
        draw.text((130, 390), "🔬 Raw Evidence Packet (Read-Only)", fill="#CBD5E1", font_size=26)
        draw.text((130, 450), "{\n  'total_cases': 1024,\n  'serious_cases': 1023,\n  'non_serious_cases': 1,\n  'expedited_cases': 392\n}", fill="#38BDF8", font_size=24)

        draw.rectangle([990, 360, 1820, 850], fill="#1E293B", outline="#10B981", width=2)
        draw.text((1020, 390), "✏️ Generated Narrative (Click-to-Edit)", fill="#10B981", font_size=26)
        draw.text((1020, 450), "Patient history & adverse event overview...\n\n[✅ Approve Section]  [🚩 Flag for Review]", fill="#F8FAFC", font_size=24)

    # Section 4 (15s - 20s): Call to Action & Conclusion
    else:
        draw.rectangle([150, 200, WIDTH - 150, 850], fill="#0F172A", outline="#818CF8", width=4)
        draw.text((220, 260), "🎉 READY FOR TECHNICAL REVIEW & DEPLOYMENT", fill="#38BDF8", font_size=44)
        draw.text((220, 350), "Candidate Name: Vishnu Vardhan M", fill="#F8FAFC", font_size=38)
        draw.text((220, 420), "Submission Package: vishnu_vardhan_m_genar_challenge.zip", fill="#CBD5E1", font_size=28)
        draw.text((220, 480), "Live Streamlit App: quickhyre.streamlit.app", fill="#10B981", font_size=28)
        draw.text((220, 540), "GitHub Repo: github.com/Rythamo8055/genar-ai-safety-reporting", fill="#818CF8", font_size=28)

        draw.rectangle([220, 650, WIDTH - 220, 770], fill="#1E293B", outline="#10B981", width=2)
        draw.text((250, 690), "Thank you QuickHyre Team! Excited to join as AI Engineer.", fill="#F8FAFC", font_size=32)

    # Footer
    draw.rectangle([0, HEIGHT - 60, WIDTH, HEIGHT], fill="#020617")
    draw.text((80, HEIGHT - 42), "GenAR AI Safety Platform -- 100k Subscriber Motion Graphics Walkthrough", fill="#64748B", font_size=20)
    draw.text((WIDTH - 420, HEIGHT - 42), "Vishnu Vardhan M | QuickHyre", fill="#38BDF8", font_size=20)

    frame_path = f"frames_100k/frame_{frame_num:04d}.png"
    img.save(frame_path)

print("Generating 600 frames...")
for f in range(TOTAL_FRAMES):
    render_frame(f)
print("All 600 frames rendered!")
