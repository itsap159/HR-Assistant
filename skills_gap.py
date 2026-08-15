import json
import google.generativeai as genai
import streamlit as st

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-3.5-flash-lite")

SKILLS_GAP_PROMPT = """
You are an expert technical recruiter comparing a resume against a job description.

Job Description:
{jd_text}

Resume:
{resume_text}

Identify the skills, tools, and qualifications required or strongly implied by the job description,
then classify each as either matched (clearly present in the resume) or missing (not evident in the resume).

Return ONLY a JSON object with this exact shape, no other text:
{{
  "matched_skills": ["skill 1", "skill 2", ...],
  "missing_skills": ["skill 1", "skill 2", ...]
}}

Keep each skill name short (1-4 words). Limit each list to at most 8 items, ordered by relevance.
"""

INTERVIEW_QUESTIONS_PROMPT = """
You are an expert technical interviewer preparing for a candidate screen.

Job Description:
{jd_text}

Resume:
{resume_text}

The candidate has these apparent gaps against the job description: {missing_skills}

Write 5-7 targeted interview questions that probe these gaps and verify the candidate's real depth
on the skills they do claim. Format as a clean Markdown bullet list, one question per line.
Do not add any commentary or text outside the list.
"""


def analyze_skills_gap(resume_text: str, jd_text: str) -> dict:
    prompt = SKILLS_GAP_PROMPT.format(resume_text=resume_text, jd_text=jd_text)
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"},
    )
    data = json.loads(response.text)
    return {
        "matched_skills": data.get("matched_skills", []),
        "missing_skills": data.get("missing_skills", []),
    }


def generate_interview_questions(resume_text: str, jd_text: str, missing_skills: list) -> str:
    prompt = INTERVIEW_QUESTIONS_PROMPT.format(
        resume_text=resume_text,
        jd_text=jd_text,
        missing_skills=", ".join(missing_skills) if missing_skills else "none identified",
    )
    response = model.generate_content(prompt)
    return response.text.strip()


RANK_BRIEF_PROMPT = """
You are an HR recruiter explaining why a candidate landed at a particular match score against a job description.

Job Description:
{jd_text}

Resume:
{resume_text}

Similarity Score: {score:.1f}% ({fit})

In ONE short sentence (max 25 words), give the concrete, specific reason for this score — name the actual
skills, experience, or gaps that most influenced it. Be specific, not generic. Do not restate the score or
fit label. Output only the sentence, no preamble or quotes.
"""


def generate_rank_brief(resume_text: str, jd_text: str, score: float, fit: str) -> str:
    prompt = RANK_BRIEF_PROMPT.format(resume_text=resume_text, jd_text=jd_text, score=score, fit=fit)
    response = model.generate_content(prompt)
    return response.text.strip()
