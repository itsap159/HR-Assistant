import streamlit as st
from pypdf import PdfReader
from compare import analyze_candidate
from similarity import match_resume_to_jd
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="HR Resume Automation")
st.title("📄 HR Resume Automation (Prototype)")
st.markdown("Upload a candidate's resume and paste a job description to get an automated analysis.")

# --- File Upload and JD Input ---
col1, col2 = st.columns(2)
with col1:
    uploaded_resume = st.file_uploader("📂 Upload Resume (PDF only)", type=["pdf"])
with col2:
    jd_text = st.text_area("📝 Paste Job Description here", height=200)

# --- Process Resume & JD ---
if uploaded_resume is not None and jd_text.strip():
    with st.spinner('Analyzing...'):
        try:
            # Extract text
            reader = PdfReader(uploaded_resume)
            resume_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

            if not resume_text.strip():
                st.error("Could not extract any text from the PDF.")
            else:
                # --- Similarity ---
                score = match_resume_to_jd(resume_text, jd_text)
                st.success("Similarity analysis complete!")
                st.subheader("🎯 Similarity Score")
                st.info(f"{score[1]} : {score[0]:.2f}% ")

                # --- AI Analysis ---
                analysis = analyze_candidate(resume_text, jd_text, score)
                
                # Display Pros & Cons
                st.subheader("Analysis")
                st.info(f"{analysis}")
            

                # Download button for Markdown file
                st.download_button(
                    label="📥 Download Analysis as Markdown",
                    data=analysis,
                    file_name="candidate_analysis.md",
                    mime="text/markdown"
                )
                # Downloadable summary

        except Exception as e:
            st.error(f"Error occurred: {e}")
else:
    st.info("Please upload a resume and paste a job description to begin.")
