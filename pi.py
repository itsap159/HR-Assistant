import streamlit as st
from pypdf import PdfReader
import google.generativeai as genai
import io
import markdown2
from xhtml2pdf import pisa
# -------------------------
# Setup
# -------------------------
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------------
# Prompt Template
# -------------------------
PROMPT_TEMPLATE = """
You are an expert resume sanitizer and formatter.

Your goal is to return a clean, professional resume in well-structured Markdown.

Sanitization Rules:
- Remove ALL personal information: emails, phone numbers, LinkedIn, GitHub, addresses, and any other contact details.
- Remove the labels too (e.g., "Email:", "Phone:", "LinkedIn:").
- Do not insert placeholders like [REMOVED] or [REDACTED].

Markdown Formatting Rules:
1. Use:
   - `#` for the candidate's full name (first + last name, separated by space) and the main professional field/role if explicitly mentioned**.  
     Example: `# John Doe — Data Scientist`
   - `##` for major sections (e.g., ## EXPERIENCE, ## EDUCATION, ## SKILLS).
   - `-` for bullet points, 
2. Preserve all sentences and bullet points exactly as written. Do not insert extra line breaks inside sentences or after commas. But make sure to have new lines after every bullet point.
3. Leave **one blank line**:
   - Between sections.
   - Between groups of bullet points.
4. Dates, designations, organizations, and locations must be formatted professionally:
   - Organization + designation on the left.
   - Dates aligned to the right.
   - Location placed below the dates, also right-aligned.
   - Example:

     **Software Engineer**  
     ABC Corp | Jan 2020 – Dec 2022  
     New York, USA  

     - Developed XYZ...
     - Improved ABC...

5. Skills, certifications, and education must be formatted as clean bullet lists or short paragraphs when appropriate.
6. Do not add commentary, explanations, or any text outside of the sanitized Markdown resume.
7. You know how to differentitate between project and designation. But always follow the formatting as in the resume.
Here is the resume to sanitize:

**MOST IMPORTANT**: Do not add anything in the resume.

{resume_text}
"""

# -------------------------
# Function
# -------------------------
def sanitize_resume_llm(resume_text: str) -> str:
    prompt = PROMPT_TEMPLATE.format(resume_text=resume_text)
    response = model.generate_content(prompt)
    return response.text.strip()

def markdown_to_pdf(md_text: str) -> io.BytesIO:
    """Convert Markdown text to a compact single-page PDF."""
    html = markdown2.markdown(md_text)

    # Compact styling to reduce space usage
    styled_html = f"""
    <html>
    <head>
      <style>
        @page {{
            size: A4;
            margin: 0.5cm;
        }}
        body {{
            font-family: Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.1;
        }}
        h1, h2, h3 {{
            margin: 4px 0;
        }}
        p {{
            margin: 2px 0;
        }}
        ul {{
            margin: 2px 0 2px 15px;
            padding: 0;
        }}
        li {{
            margin: 0;
            padding: 0;
        }}
      </style>
    </head>
    <body>{html}</body>
    </html>
    """

    pdf_buffer = io.BytesIO()
    pisa.CreatePDF(src=styled_html, dest=pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer