import streamlit as st
from pypdf import PdfReader
from compare import analyze_candidate
from similarity import match_resume_to_jd
from increment_agent import predict_relocation_salary_simple  # Replace with your actual agent file or path
import pandas as pd
from pi import sanitize_resume_llm, markdown_to_pdf
# -------------------------
# Streamlit App
# -------------------------
st.set_page_config(page_title="HR Resume Automation + PI Remover")
st.title("📄 HR Resume Automation + Resume PI Remover")

st.markdown("Upload a candidate's resume and (optionally) a job description for automated analysis, "
            "or sanitize the resume to remove personal information.")

# --- File Upload and JD Input ---
col1, col2 = st.columns(2)
with col1:
    uploaded_resume = st.file_uploader("📂 Upload Resume (PDF only)", type=["pdf"])
with col2:
    jd_text = st.text_area("📝 Paste Job Description here (optional)", height=200)

if uploaded_resume is not None:
    # Extract text
    reader = PdfReader(uploaded_resume)
    resume_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

    if not resume_text.strip():
        st.error("Could not extract any text from the PDF.")
    else:
        # -------------------------
        # Candidate Analysis Section
        # -------------------------
        if jd_text.strip():
            st.subheader("🎯 Resume vs JD Analysis")
            if st.button("🔍 Analyze Candidate"):
                with st.spinner('Analyzing candidate...'):
                    try:
                        # --- Similarity ---
                        score = match_resume_to_jd(resume_text, jd_text)
                        st.success("Similarity analysis complete!")
                        st.info(f"Similarity Score: {score[0]:.2f}%")
                        st.info(f"Similarity Match: {score[1]}")
                        

                        # --- AI Analysis ---
                        analysis = analyze_candidate(resume_text, jd_text, score)
                        st.subheader("Analysis")
                        st.info(f"{analysis}")

                        # Download button for Markdown file
                        st.download_button(
                            label="📥 Download Analysis as Markdown",
                            data=analysis,
                            file_name="candidate_analysis.md",
                            mime="text/markdown"
                        )
                    except Exception as e:
                        st.error(f"Error during analysis: {e}")

            # --- Salary Prediction Section ---
            st.markdown("---")
            st.subheader("💰 Salary Prediction (Optional)")
            current_salary = st.number_input("Enter current salary (INR)", min_value=0, step=1000)
            current_location = st.text_input("Enter current Location")
            new_location = st.text_input("Enter New Location")

            if st.button("🔮 Predict Salary"):
                if current_salary > 0:
                    with st.spinner("Fetching salary prediction..."):
                        try:
                            salary_prediction = predict_relocation_salary_simple(
                                resume_text, jd_text, current_salary, new_location, current_location
                            )
                            st.success("Salary prediction complete!")
                            st.write(salary_prediction)
                        except Exception as e:
                            st.error(f"Error predicting salary: {e}")
                else:
                    st.warning("Please enter a valid current salary (INR).")

        # -------------------------
        # Resume Sanitization Section
        # -------------------------
        st.markdown("---")
        st.subheader("🧹 Resume PI Remover (LLM Only)")

        if st.button("Sanitize & Format Resume"):
            with st.spinner("Processing with LLM..."):
                md_resume = sanitize_resume_llm(resume_text)

            st.subheader("Sanitized Resume (Markdown)")
            st.markdown(md_resume)

            # Download options
            st.download_button(
                label="📥 Download Sanitized Resume (Markdown)",
                data=md_resume,
                file_name="resume_sanitized.md",
                mime="text/markdown"
            )
            pdf_buffer = markdown_to_pdf(md_resume)
            st.download_button(
                label="📥 Download Sanitized Resume (PDF)",
                data=pdf_buffer,
                file_name="resume_sanitized.pdf",
                mime="application/pdf"
            )

else:
    st.info("Please upload a resume to begin.")
