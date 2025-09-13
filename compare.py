# compare.py
from google import genai
import os
import streamlit as st
from datetime import datetime
import google.generativeai as genai
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
from tools.increment_tool import fetch_salary_trends

tools = [fetch_salary_trends]

model = genai.GenerativeModel("gemini-2.5-flash")

def analyze_candidate(resume_text, jd_text, score):
    prompt = f"""
    You are an HR assistant. A candidate's resume has been matched with a job description. 

    Job Description:
    {jd_text}

    Resume:
    {resume_text}

    Similarity Score: {score}

    Task:
    1. List PROS (skills/experience that match well with JD) in bullet points. Make sure, HR can just glance over it and understand.
    2. List CONS (missing skills, gaps, or weaknesses) in bullet points. Make sure, HR can just glance over it and understand.
    3. Explain overall FIT with the JD (good, moderate, poor) and why.
    4. Write a short professional SUMMARY NOTE for HR to share with the hiring manager.
    5. Give a final verdict.
    
    This is the current date which might help in analyzing : {datetime.now()}
    """

    response = model.generate_content(prompt)



    return response.text

