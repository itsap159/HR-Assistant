# compare.py
from google import genai
import os
import streamlit as st

import google.generativeai as genai
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")  # or "gemini-1.5-pro"

def analyze_candidate(resume_text, jd_text, score):
    prompt = f"""
    You are an HR assistant. A candidate's resume has been matched with a job description.

    Job Description:
    {jd_text}

    Resume:
    {resume_text}

    Similarity Score: {score}

    Task:
    1. List PROS (skills/experience that match well with JD) in bullet points.
    2. List CONS (missing skills, gaps, or weaknesses) in bullet points.
    3. Explain overall FIT with the JD (good, moderate, poor) and why.
    4. Write a short professional SUMMARY NOTE for HR to share with the hiring manager.
    """

    response = model.generate_content(prompt)



    return response.text
