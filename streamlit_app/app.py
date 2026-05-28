import os
from dotenv import load_dotenv
import streamlit as st
# FIX: Direct Google official AI library import ki
import google.generativeai as genai

# Local aur Production dono ke liye load_dotenv configuration
if os.path.exists(".env"):
    load_dotenv()
else:
    load_dotenv(r"C:\Users\hp\OneDrive\Desktop\AI_Agent\.venv\.env")

st.set_page_config(page_title="Blood Work Analyzer", layout="wide")

# API Key fallback routing
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API Key missing! Please check your Streamlit Advanced Secrets configuration.")
    st.stop()

# FIX: Direct Google AI Client config aur initialization
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

st.markdown("""
<style>
.scroll-box {
    height: 230px;
    overflow-y: auto;
    padding: 12px 16px;
    border: 1px solid #333;
    border-radius: 8px;
    background-color: #1e1e1e;
    font-size: 0.9rem;
    line-height: 1.6;
}
.scroll-box p, .scroll-box li {
    color: #e0e0e0;
}
.section-label {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 6px;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

st.title("Blood Work Analyzer")

left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("Blood Work Report")
    blood_report = st.text_area(
        label="Paste your report below",
        height=500,
        placeholder="Paste your blood work report here...",
        label_visibility="collapsed"
    )
    analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

with right_col:
    st.subheader("Health Summary")
    health_box = st.empty()
    health_box.markdown('<div class="scroll-box"></div>', unsafe_allow_html=True)

    st.subheader("Suggested Diet Plan")
    diet_box = st.empty()
    diet_box.markdown('<div class="scroll-box"></div>', unsafe_allow_html=True)

if analyze_clicked:
    if not blood_report.strip():
        with left_col:
            st.warning("Please paste a blood work report before analyzing.")
    else:
        with st.spinner("Analyzing your blood work..."):
            try:
                # Stage 1: Native Extraction
                extraction_prompt = f"""
You are a medical data extraction assistant.

From the blood report below, extract ALL test values and classify each one as HIGH, LOW, or NORMAL 
based on the reference ranges provided in the report.

Format your response exactly as:
- Test Name: value | Status: HIGH/LOW/NORMAL | Reference: range

Blood Report:
{blood_report}
"""
                # FIX: Native invocation without complex array wrappers
                extraction_response = model.generate_content(extraction_prompt)
                extracted_values = extraction_response.text

                # Stage 2: Native Clinical Indian Diet Planner
                diet_prompt = f"""
You are a clinical nutritionist specializing in Indian dietary habits.

Based on the blood work analysis below, provide two clearly separated sections:

SECTION 1 - HEALTH SUMMARY:
Write 4-5 lines explaining the patient's condition in simple, non-technical language.

SECTION 2 - INDIAN DIET PLAN:
List foods to eat more of and foods to avoid, using commonly available Indian foods 
like dal, sabzi, roti, rice, etc. Keep it practical and concise.

Blood Work Analysis:
{extracted_values}
"""
                diet_response = model.generate_content(diet_prompt)
                full_response = diet_response.text

                # Split response into two sections
                if "SECTION 2" in full_response:
                    parts = full_response.split("SECTION 2")
                    health_summary = parts[0].replace("SECTION 1 - HEALTH SUMMARY:", "").replace("SECTION 1", "").strip()
                    diet_plan = ("SECTION 2" + parts[1]).replace("SECTION 2 - INDIAN DIET PLAN:", "").replace("SECTION 2", "").strip()
                else:
                    health_summary = full_response
                    diet_plan = ""

                # Render into fixed-height scrollable boxes
                health_box.markdown(
                    f'<div class="scroll-box">{health_summary}</div>',
                    unsafe_allow_html=True
                )
                diet_box.markdown(
                    f'<div class="scroll-box">{diet_plan if diet_plan else full_response}</div>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"Google AI Studio Error: {str(e)}")