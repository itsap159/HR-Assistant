import streamlit as st
from pypdf import PdfReader
from compare import analyze_candidate
from similarity import match_resume_to_jd
from increment_agent import predict_relocation_salary_simple
from pi import sanitize_resume_llm, markdown_to_pdf

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="HR Resume Assistant",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.session_state.setdefault("theme", "dark")

# -------------------------
# Theme palettes
# -------------------------
PALETTES = {
    "dark": dict(
        base_bg="#0B0C14",
        glow1="rgba(99, 102, 241, 0.24)", glow2="rgba(139, 92, 246, 0.20)",
        glow3="rgba(6, 182, 212, 0.14)", glow4="rgba(16, 185, 129, 0.12)",
        sidebar_bg="#12131F", sidebar_border="rgba(255,255,255,0.06)",
        text_primary="#E5E7EB", text_secondary="#9CA3AF", text_muted="#6B7280",
        card_border="rgba(255,255,255,0.10)",
        input_bg="#171827", input_border="rgba(255,255,255,0.14)",
        hero_from="#4338CA", hero_to="#7C3AED", hero_shadow="rgba(109, 40, 217, 0.65)",
        feature_icon_indigo="rgba(99, 102, 241, 0.18)", feature_icon_emerald="rgba(16, 185, 129, 0.16)", feature_icon_cyan="rgba(6, 182, 212, 0.16)",
        feature_hover_shadow="rgba(0, 0, 0, 0.35)", feature_hover_border="rgba(255,255,255,0.16)",
        file_strip_bg="rgba(16, 185, 129, 0.12)", file_strip_border="rgba(16, 185, 129, 0.35)", file_strip_text="#A7F3D0", file_strip_b="#6EE7B7",
        eyebrow_indigo="#A5B4FC", eyebrow_emerald="#6EE7B7", eyebrow_cyan="#67E8F9",
        badge_excellent_bg="rgba(34, 197, 94, 0.18)", badge_excellent_text="#86EFAC",
        badge_good_bg="rgba(59, 130, 246, 0.18)", badge_good_text="#93C5FD",
        badge_moderate_bg="rgba(245, 158, 11, 0.18)", badge_moderate_text="#FCD34D",
        badge_poor_bg="rgba(239, 68, 68, 0.18)", badge_poor_text="#FCA5A5",
        empty_text="#9CA3AF", empty_title="#E5E7EB",
        step_done_bg="#6366F1", step_pending_bg="rgba(255,255,255,0.08)", step_pending_text="#6B7280",
        step_text_done="#F3F4F6", step_text_pending="#6B7280",
        status_text="#D1D5DB",
        md_h2_color="#A5B4FC", md_h2_border="rgba(165, 180, 252, 0.25)",
        btn_hover_shadow="rgba(129, 140, 248, 0.35)",
        primary="#818CF8",
    ),
    "light": dict(
        base_bg="#FBFBFE",
        glow1="rgba(79, 70, 229, 0.10)", glow2="rgba(124, 58, 237, 0.08)",
        glow3="rgba(8, 145, 178, 0.07)", glow4="rgba(5, 150, 105, 0.06)",
        sidebar_bg="#F3F4F6", sidebar_border="#E5E7EB",
        text_primary="#111827", text_secondary="#4B5563", text_muted="#6B7280",
        card_border="#E5E7EB",
        input_bg="#F9FAFB", input_border="#E5E7EB",
        hero_from="#3730A3", hero_to="#6D28D9", hero_shadow="rgba(109, 40, 217, 0.25)",
        feature_icon_indigo="#EEF2FF", feature_icon_emerald="#ECFDF5", feature_icon_cyan="#ECFEFF",
        feature_hover_shadow="rgba(17, 24, 39, 0.08)", feature_hover_border="#D1D5DB",
        file_strip_bg="#ECFDF5", file_strip_border="#A7F3D0", file_strip_text="#065F46", file_strip_b="#065F46",
        eyebrow_indigo="#4F46E5", eyebrow_emerald="#059669", eyebrow_cyan="#0891B2",
        badge_excellent_bg="#DCFCE7", badge_excellent_text="#166534",
        badge_good_bg="#DBEAFE", badge_good_text="#1E40AF",
        badge_moderate_bg="#FEF3C7", badge_moderate_text="#92400E",
        badge_poor_bg="#FEE2E2", badge_poor_text="#991B1B",
        empty_text="#6B7280", empty_title="#374151",
        step_done_bg="#4F46E5", step_pending_bg="#E5E7EB", step_pending_text="#9CA3AF",
        step_text_done="#111827", step_text_pending="#9CA3AF",
        status_text="#374151",
        md_h2_color="#312E81", md_h2_border="#EEF2FF",
        btn_hover_shadow="rgba(79, 70, 229, 0.3)",
        primary="#4F46E5",
    ),
}
p = PALETTES[st.session_state.theme]

# -------------------------
# Styling
# -------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }}

    [data-testid="stApp"] {{
        background:
            radial-gradient(680px circle at 6% 4%, {p['glow1']}, transparent 60%),
            radial-gradient(600px circle at 96% 18%, {p['glow2']}, transparent 60%),
            radial-gradient(720px circle at 50% 100%, {p['glow3']}, transparent 55%),
            radial-gradient(460px circle at 18% 90%, {p['glow4']}, transparent 60%),
            {p['base_bg']};
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{
        background: transparent !important;
        color: {p['text_primary']} !important;
    }}
    [data-testid="stHeader"] * {{ color: {p['text_primary']} !important; }}
    [data-testid="stHeader"] svg[fill="currentColor"] {{ fill: {p['text_primary']} !important; }}
    [data-testid="stBaseButton-header"], [data-testid="stBaseButton-headerNoPadding"] {{
        background: transparent !important;
    }}

    [data-testid="stSidebar"] {{
        background: {p['sidebar_bg']} !important;
        border-right: 1px solid {p['sidebar_border']};
    }}
    [data-testid="stSidebar"] * {{ color: {p['text_primary']}; }}
    [data-testid="stCaptionContainer"] * {{ color: {p['text_secondary']} !important; }}
    [data-testid="stFileUploaderFile"] *, [data-testid="stFileUploaderFileName"] {{ color: {p['text_primary']} !important; }}
    [data-testid="stProgress"] [role="progressbar"],
    [data-testid="stProgress"] [role="progressbar"] > div,
    [data-testid="stProgress"] [role="progressbar"] > div > div {{ background: {p['input_bg']} !important; }}
    [data-testid="stProgress"] [role="progressbar"] > div > div > div {{ background: {p['primary']} !important; }}

    [data-testid="stTextAreaRootElement"], [data-testid="stTextAreaRootElement"] textarea {{
        background: {p['input_bg']} !important;
        border-color: {p['input_border']} !important;
        color: {p['text_primary']} !important;
    }}
    [data-testid="stTextInput"] input, [data-testid="stNumberInputField"] {{
        background: {p['input_bg']} !important;
        border-color: {p['input_border']} !important;
        color: {p['text_primary']} !important;
    }}
    [data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"] [data-baseweb="input"] {{
        background: {p['input_bg']} !important;
        border-color: {p['input_border']} !important;
    }}
    [data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] {{
        background: {p['input_bg']} !important;
    }}
    [data-testid="stNumberInputStepDown"] svg, [data-testid="stNumberInputStepUp"] svg {{
        color: {p['text_secondary']} !important;
    }}
    [data-testid="stFileUploaderDropzone"] {{
        background: {p['input_bg']} !important;
        border-color: {p['input_border']} !important;
    }}
    [data-testid="stFileUploaderDropzone"] * {{ color: {p['text_secondary']} !important; }}
    [data-testid="stBaseButton-secondary"] {{
        background: {p['input_bg']} !important;
        color: {p['text_primary']} !important;
        border-color: {p['input_border']} !important;
    }}
    [data-testid="stWidgetLabel"] * {{ color: {p['text_primary']} !important; }}
    [data-testid="stAlertContainer"] * {{ color: {p['text_primary']} !important; }}
    [data-testid="stMarkdownContainer"] {{ color: {p['text_primary']}; }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: {p['card_border']} !important;
    }}
    [data-testid="stMetricValue"] {{ color: {p['text_primary']} !important; }}
    [data-testid="stMetricLabel"] {{ color: {p['text_secondary']} !important; }}
    [data-testid="stTabs"] [data-baseweb="tab"] {{ color: {p['text_secondary']} !important; }}
    [data-testid="stTabs"] button[aria-selected="true"] p {{ color: {p['primary']} !important; }}
    [data-testid="stMarkdownContainer"] hr {{ border-color: {p['card_border']} !important; }}

    .block-container {{
        padding-top: 2.25rem;
        padding-bottom: 3rem;
        max-width: 1080px;
    }}

    /* ---- Hero ---- */
    .hero {{
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, {p['hero_from']} 0%, {p['hero_to']} 100%);
        border-radius: 20px;
        padding: 2.5rem 2.5rem;
        margin-bottom: 1.75rem;
        color: white;
        box-shadow: 0 25px 70px -25px {p['hero_shadow']};
    }}
    .hero::before {{
        content: "";
        position: absolute;
        top: -60px; right: -60px;
        width: 240px; height: 240px;
        background: radial-gradient(circle, rgba(255,255,255,0.16) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
    }}
    .hero::after {{
        content: "";
        position: absolute;
        bottom: -90px; left: 30%;
        width: 260px; height: 260px;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
    }}
    .hero-badge {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 52px; height: 52px;
        background: rgba(255,255,255,0.15);
        border-radius: 14px;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }}
    .hero h1 {{
        margin: 0 0 0.4rem 0;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }}
    .hero p {{
        margin: 0 0 1.1rem 0;
        opacity: 0.88;
        font-size: 1.05rem;
        max-width: 640px;
        position: relative;
        z-index: 1;
    }}
    .hero-chips {{ position: relative; z-index: 1; }}
    .hero-chip {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.22);
        padding: 0.32rem 0.85rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }}

    /* ---- Feature / landing cards ---- */
    .feature-card {{
        border: 1px solid {p['card_border']};
        border-radius: 16px;
        padding: 1.4rem 1.3rem;
        height: 100%;
        transition: box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
    }}
    .feature-card:hover {{
        box-shadow: 0 8px 28px {p['feature_hover_shadow']};
        border-color: {p['feature_hover_border']};
        transform: translateY(-2px);
    }}
    .feature-icon {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 42px; height: 42px;
        border-radius: 12px;
        font-size: 1.25rem;
        margin-bottom: 0.75rem;
    }}
    .feature-icon-indigo {{ background: {p['feature_icon_indigo']}; }}
    .feature-icon-emerald {{ background: {p['feature_icon_emerald']}; }}
    .feature-icon-cyan {{ background: {p['feature_icon_cyan']}; }}
    .feature-card h4 {{
        margin: 0 0 0.3rem 0;
        font-size: 1.02rem;
        font-weight: 700;
        color: {p['text_primary']};
    }}
    .feature-card p {{
        margin: 0;
        font-size: 0.88rem;
        color: {p['text_secondary']};
        line-height: 1.5;
    }}

    /* ---- Status strip ---- */
    .file-strip {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        background: {p['file_strip_bg']};
        border: 1px solid {p['file_strip_border']};
        border-radius: 12px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 1.5rem;
        font-size: 0.92rem;
        color: {p['file_strip_text']};
    }}
    .file-strip b {{ color: {p['file_strip_b']}; }}

    /* ---- Section eyebrow labels ---- */
    .eyebrow {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.6rem;
    }}
    .eyebrow-indigo {{ color: {p['eyebrow_indigo']}; }}
    .eyebrow-emerald {{ color: {p['eyebrow_emerald']}; }}
    .eyebrow-cyan {{ color: {p['eyebrow_cyan']}; }}

    /* ---- Badges ---- */
    .badge {{
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.85rem;
    }}
    .badge-excellent {{ background: {p['badge_excellent_bg']}; color: {p['badge_excellent_text']}; }}
    .badge-good {{ background: {p['badge_good_bg']}; color: {p['badge_good_text']}; }}
    .badge-moderate {{ background: {p['badge_moderate_bg']}; color: {p['badge_moderate_text']}; }}
    .badge-poor {{ background: {p['badge_poor_bg']}; color: {p['badge_poor_text']}; }}

    /* ---- Empty / locked state ---- */
    .empty-state {{
        text-align: center;
        padding: 2.75rem 1.5rem;
        color: {p['empty_text']};
    }}
    .empty-state .icon {{ font-size: 2.1rem; margin-bottom: 0.6rem; }}
    .empty-state .title {{ font-weight: 700; color: {p['empty_title']}; margin-bottom: 0.25rem; }}
    .empty-state .desc {{ font-size: 0.9rem; }}

    /* ---- Sidebar stepper ---- */
    .step-row {{
        display: flex;
        align-items: center;
        gap: 0.55rem;
        font-size: 0.88rem;
        padding: 0.3rem 0;
    }}
    .step-dot {{
        width: 20px; height: 20px;
        min-width: 20px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: 700;
    }}
    .step-done {{ background: {p['step_done_bg']}; color: white; }}
    .step-pending {{ background: {p['step_pending_bg']}; color: {p['step_pending_text']}; }}
    .step-text-done {{ color: {p['step_text_done']}; font-weight: 600; }}
    .step-text-pending {{ color: {p['step_text_pending']}; }}

    .status-row {{ font-size: 0.85rem; margin-bottom: 0.2rem; color: {p['status_text']}; }}
    .status-dot {{ font-size: 0.65rem; margin-right: 0.4rem; }}

    /* ---- Markdown content polish (LLM output) ---- */
    .stMarkdown h2 {{
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        margin-top: 1.1rem !important;
        padding-bottom: 0.35rem;
        border-bottom: 2px solid {p['md_h2_border']};
        color: {p['md_h2_color']};
    }}
    .stMarkdown ul {{ margin-top: 0.3rem; }}
    .stMarkdown li {{ margin-bottom: 0.3rem; line-height: 1.55; }}

    /* ---- Buttons ---- */
    .stButton > button {{
        border-radius: 10px;
        font-weight: 600;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }}
    .stButton > button[kind="primary"]:hover {{
        transform: translateY(-1px);
        box-shadow: 0 8px 20px {p['btn_hover_shadow']};
    }}

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab"] {{
        font-weight: 600;
        font-size: 0.95rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

BADGE_CLASS = {
    "Excellent": "badge-excellent",
    "Good": "badge-good",
    "Moderate": "badge-moderate",
    "Poor": "badge-poor",
}

FIT_TAKEAWAY = {
    "Excellent": "Strong alignment with the job description — a top candidate to prioritize.",
    "Good": "Solid overlap with the role — worth a closer look.",
    "Moderate": "Partial match — some gaps against the job description.",
    "Poor": "Limited overlap with the job description.",
}


def fit_badge(category: str) -> str:
    css_class = BADGE_CLASS.get(category, "badge-moderate")
    return f'<span class="badge {css_class}">{category} Fit</span>'


def section_eyebrow(icon: str, text: str, variant: str) -> None:
    st.markdown(
        f'<div class="eyebrow eyebrow-{variant}">{icon} {text}</div>',
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, desc: str) -> None:
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="icon">{icon}</div>
            <div class="title">{title}</div>
            <div class="desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_card(icon: str, variant: str, title: str, desc: str) -> None:
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-icon feature-icon-{variant}">{icon}</div>
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def secret_status(key: str) -> str:
    configured = bool(st.secrets.get(key))
    dot = "🟢" if configured else "🔴"
    return f'<div class="status-row"><span class="status-dot">{dot}</span>{key}</div>'


def step_row(done: bool, label: str) -> str:
    dot_cls = "step-done" if done else "step-pending"
    text_cls = "step-text-done" if done else "step-text-pending"
    mark = "✓" if done else "○"
    return f'<div class="step-row"><span class="step-dot {dot_cls}">{mark}</span><span class="{text_cls}">{label}</span></div>'


# -------------------------
# Session state
# -------------------------
for k in ["analysis", "score", "salary_prediction", "sanitized_md"]:
    st.session_state.setdefault(k, None)

# -------------------------
# Hero header
# -------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">🧭</div>
        <h1>HR Resume Assistant</h1>
        <p>Match candidates to a job description, estimate relocation salary, and strip personal information — all in one place.</p>
        <div class="hero-chips">
            <span class="hero-chip">🎯 Match Score</span>
            <span class="hero-chip">💰 Salary Insight</span>
            <span class="hero-chip">🧹 PII Sanitize</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Upload + JD input
# -------------------------
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        uploaded_resume = st.file_uploader("📂 Upload Resume (PDF only)", type=["pdf"])
    with col2:
        jd_text = st.text_area("📝 Paste Job Description here (optional)", height=180)

# -------------------------
# Sidebar (built after inputs so the stepper reflects live state)
# -------------------------
with st.sidebar:
    is_light = st.session_state.theme == "light"
    toggled = st.toggle("☀️ Light mode", value=is_light, key="theme_toggle")
    if toggled != is_light:
        st.session_state.theme = "light" if toggled else "dark"
        st.rerun()
    st.markdown("### 🧭 HR Resume Assistant")
    st.caption("AI-assisted resume screening, salary insight & PII sanitization.")
    st.markdown("---")
    st.markdown("**Progress**")
    st.markdown(step_row(uploaded_resume is not None, "Upload a resume"), unsafe_allow_html=True)
    st.markdown(step_row(bool(jd_text.strip()), "Paste a job description"), unsafe_allow_html=True)
    st.markdown(step_row(uploaded_resume is not None, "Explore the tabs"), unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Connection status**")
    st.markdown(secret_status("GOOGLE_API_KEY"), unsafe_allow_html=True)
    st.markdown(secret_status("HF_TOKEN"), unsafe_allow_html=True)
    st.markdown(secret_status("TAVILY_API_KEY"), unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 Start Over", use_container_width=True):
        for k in ["analysis", "score", "salary_prediction", "sanitized_md"]:
            st.session_state[k] = None
        st.rerun()

# -------------------------
# Landing state — no resume yet
# -------------------------
if uploaded_resume is None:
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        feature_card("🎯", "indigo", "Match & Analyze", "Score a resume against a job description and get an AI-written pros/cons breakdown.")
    with fc2:
        feature_card("💰", "emerald", "Salary Insights", "Estimate a fair relocation salary using live market trend data.")
    with fc3:
        feature_card("🧹", "cyan", "Sanitize & Export", "Strip personal information and export a clean, formatted resume.")
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    st.info("👋 Upload a resume above to get started.")
    st.stop()

reader = PdfReader(uploaded_resume)
resume_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

if not resume_text.strip():
    st.error("Could not extract any text from the PDF.")
    st.stop()

st.markdown(
    f"""
    <div class="file-strip">
        ✅ <b>{uploaded_resume.name}</b> loaded — {len(resume_text.split())} words extracted.
    </div>
    """,
    unsafe_allow_html=True,
)

tab_match, tab_salary, tab_sanitize = st.tabs(
    ["🎯 Match & Analyze", "💰 Salary Insights", "🧹 Sanitize & Export"]
)

# -------------------------
# Tab 1: Match & Analyze
# -------------------------
with tab_match:
    if not jd_text.strip():
        with st.container(border=True):
            empty_state("🔒", "Job description required", "Paste a job description above to unlock candidate matching.")
    else:
        if st.button("🔍 Analyze Candidate", type="primary"):
            with st.spinner("Analyzing candidate..."):
                try:
                    score = match_resume_to_jd(resume_text, jd_text)
                    analysis = analyze_candidate(resume_text, jd_text, score)
                    st.session_state.score = score
                    st.session_state.analysis = analysis
                except Exception as e:
                    st.error(f"Error during analysis: {e}")

        if st.session_state.score:
            score_val, fit_category = st.session_state.score
            with st.container(border=True):
                section_eyebrow("🎯", "Match Result", "indigo")
                mcol, bcol = st.columns([1, 2])
                with mcol:
                    st.metric("Similarity Score", f"{score_val:.2f}%")
                with bcol:
                    st.markdown("<br>" + fit_badge(fit_category), unsafe_allow_html=True)
                    st.caption(FIT_TAKEAWAY.get(fit_category, ""))
                st.progress(min(int(score_val), 100) / 100)

        if st.session_state.analysis:
            with st.container(border=True):
                section_eyebrow("📋", "Candidate Analysis", "indigo")
                st.markdown(st.session_state.analysis)
            st.download_button(
                label="📥 Download Analysis as Markdown",
                data=st.session_state.analysis,
                file_name="candidate_analysis.md",
                mime="text/markdown",
            )

# -------------------------
# Tab 2: Salary Insights
# -------------------------
with tab_salary:
    if not jd_text.strip():
        with st.container(border=True):
            empty_state("🔒", "Job description required", "Paste a job description above to unlock salary prediction.")
    else:
        with st.container(border=True):
            section_eyebrow("💰", "Relocation Details", "emerald")
            c1, c2, c3 = st.columns(3)
            with c1:
                current_salary = st.number_input("Current salary (INR)", min_value=0, step=1000)
            with c2:
                current_location = st.text_input("Current location")
            with c3:
                new_location = st.text_input("New location")

            if st.button("🔮 Predict Salary", type="primary"):
                if current_salary > 0:
                    with st.spinner("Fetching salary prediction..."):
                        try:
                            st.session_state.salary_prediction = predict_relocation_salary_simple(
                                resume_text, jd_text, current_salary, new_location, current_location
                            )
                        except Exception as e:
                            st.error(f"Error predicting salary: {e}")
                else:
                    st.warning("Please enter a valid current salary (INR).")

        if st.session_state.salary_prediction:
            with st.container(border=True):
                section_eyebrow("📊", "Salary Recommendation", "emerald")
                st.markdown(st.session_state.salary_prediction)

# -------------------------
# Tab 3: Sanitize & Export
# -------------------------
with tab_sanitize:
    if st.button("🧹 Sanitize & Format Resume", type="primary"):
        with st.spinner("Processing with LLM..."):
            try:
                st.session_state.sanitized_md = sanitize_resume_llm(resume_text)
            except Exception as e:
                st.error(f"Error sanitizing resume: {e}")

    if st.session_state.sanitized_md:
        with st.container(border=True):
            section_eyebrow("📄", "Sanitized Resume", "cyan")
            st.markdown(st.session_state.sanitized_md)

        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                label="📥 Download as Markdown",
                data=st.session_state.sanitized_md,
                file_name="resume_sanitized.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with dl2:
            pdf_buffer = markdown_to_pdf(st.session_state.sanitized_md)
            st.download_button(
                label="📥 Download as PDF",
                data=pdf_buffer,
                file_name="resume_sanitized.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    else:
        with st.container(border=True):
            empty_state("🧹", "No sanitized version yet", "Click the button above to generate a clean, PII-free resume.")
