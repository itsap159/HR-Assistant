import pandas as pd
from similarity import match_resume_to_jd

FIT_TAKEAWAY = {
    "Excellent": "Strong alignment with the job description — a top candidate to prioritize.",
    "Good": "Solid overlap with the role — worth a closer look.",
    "Moderate": "Partial match — some gaps against the job description.",
    "Poor": "Limited overlap with the job description.",
}


def fit_reason(fit: str) -> str:
    return FIT_TAKEAWAY.get(fit, "")


def rank_candidates(candidates: list, jd_text: str) -> pd.DataFrame:
    rows = []
    for c in candidates:
        score, fit = match_resume_to_jd(c["text"], jd_text)
        rows.append({
            "Name": c["name"], "Candidate": c["filename"],
            "Score (%)": score, "Fit": fit, "Why": fit_reason(fit),
        })
    df = pd.DataFrame(rows).sort_values("Score (%)", ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df


def rank_roles(resume_text: str, roles: list) -> pd.DataFrame:
    rows = []
    for role in roles:
        score, fit = match_resume_to_jd(resume_text, role["text"])
        rows.append({"Role": role["label"], "Score (%)": score, "Fit": fit, "Why": fit_reason(fit)})
    df = pd.DataFrame(rows).sort_values("Score (%)", ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df
