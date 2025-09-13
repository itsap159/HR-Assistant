from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from tools.increment_tool import fetch_salary_trends
import streamlit as st
from datetime import datetime

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=st.secrets["GOOGLE_API_KEY"],
)
tools = [fetch_salary_trends]
graph = create_react_agent(llm, tools)

def predict_relocation_salary_simple(resume_text, jd_text, current_salary, new_location, current_location):

    prompt = f"""
    You are an expert HR compensation analyst. Analyze the following relocation scenario carefully:

    Resume: {resume_text}
    Job Description: {jd_text}
    Current Salary: {current_salary} INR
    Current Location: {current_location}
    New Location: {new_location}

    Tasks:
    1. Extract candidate's total years of experience and experience in the most recent role.
    2. Evaluate candidate's skills, education, and relevant industry experience.
    3. Assess market salary trends, adjusting for:
    - Role and seniority
    - Industry benchmarks
    - Location differences and cost-of-living
    - Years of experience and progression in current role
    4. Use the fetch_salary_trends tool if needed to obtain accurate market data.

    Output:
    1. **Expected Salary Range (INR)**: Provide a realistic range.
    2. **% Adjustment**: Show the difference between old and new location salaries.
    3. **Reasoning**: Summarize your market-based analysis in 5-7 lines. Also provide relevant sources.
    4. **HR Recommendation Note**: Provide a short 2-3 line actionable note for HR.

    Rules:
    - Always consider both total experience and experience in the most recent role.
    - Adjust the salary range for market trends, role demand, and cost-of-living differences.
    - Keep reasoning concise but informative.
    - Format the output clearly in bullet points or numbered sections.
    - Here is the current date: {datetime.now()}
    """
    result = graph.invoke({"messages": [HumanMessage(content=prompt)]})
    # Ensure result parsing is robust
    print(result)
    message = result.get('messages', [])
    answer = message[-1].content if message else "No response"
    return answer
