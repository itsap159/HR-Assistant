# matcher.py
from sentence_transformers import SentenceTransformer, util
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

import os
HF_TOKEN = st.secrets["HF_TOKEN"]

@st.cache_resource
def get_model():
    return SentenceTransformer("Qwen/Qwen3-Embedding-0.6B", use_auth_token=HF_TOKEN)

def match_resume_to_jd(resume_text, jd_text):
    model = get_model()
    embeddings = model.encode([resume_text, jd_text], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
    percentage = similarity * 100
    def get_fit_category(score):
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Moderate"
        else:
            return "Poor"

    return round(percentage, 2), get_fit_category(similarity)
