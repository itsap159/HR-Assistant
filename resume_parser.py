from pypdf import PdfReader
from docx import Document

_NAME_BLOCKLIST = {"resume", "cv", "curriculum vitae", "bio-data", "biodata", "profile"}


def extract_resume_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    if name.endswith(".docx"):
        document = Document(uploaded_file)
        return "\n".join(para.text for para in document.paragraphs if para.text.strip())

    reader = PdfReader(uploaded_file)
    return " ".join(page.extract_text() for page in reader.pages if page.extract_text())


def guess_candidate_name(resume_text: str, fallback: str) -> str:
    checked = 0
    for line in resume_text.splitlines():
        line = line.strip()
        if not line:
            continue
        checked += 1
        if checked > 5:
            break
        if "@" in line or "http" in line.lower() or any(ch.isdigit() for ch in line):
            continue
        if line.lower() in _NAME_BLOCKLIST or len(line) > 60:
            continue
        return line
    return fallback
