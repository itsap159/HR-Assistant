import io
import streamlit as st
import pandas as pd
from resume_parser import extract_resume_text, guess_candidate_name
from compare import analyze_candidate
from similarity import match_resume_to_jd
from increment_agent import predict_relocation_salary_simple
from pi import sanitize_resume_llm, markdown_to_pdf
from skills_gap import analyze_skills_gap, generate_interview_questions, generate_rank_brief
from batch import rank_candidates, rank_roles, FIT_TAKEAWAY, fit_reason

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
    [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-segmented_control"] {{
        background: {p['input_bg']} !important;
        color: {p['text_primary']} !important;
        border-color: {p['input_border']} !important;
    }}
    [data-testid="stBaseButton-segmented_control"] p {{ color: {p['text_primary']} !important; }}
    [data-testid="stBaseButton-tertiary"] {{
        background: transparent !important;
        color: {p['primary']} !important;
        padding: 0.15rem 0.4rem !important;
    }}
    [data-testid="stBaseButton-tertiary"] p {{ color: {p['primary']} !important; font-weight: 600; }}
    [data-testid="stBaseButton-tertiary"]:hover {{ background: {p['input_bg']} !important; }}
    [data-testid="stWidgetLabel"] * {{ color: {p['text_primary']} !important; }}
    [data-testid="stAlertContainer"] * {{ color: {p['text_primary']} !important; }}
    [data-testid="stMarkdownContainer"] {{ color: {p['text_primary']}; }}
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {{
        background: {p['input_bg']} !important;
        border-color: {p['input_border']} !important;
    }}
    [data-testid="stMultiSelect"] span {{ color: {p['text_primary']} !important; }}

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

    /* ---- Skill chips ---- */
    .skill-chip-wrap {{ display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.4rem 0 0.2rem 0; }}
    .skill-chip {{
        display: inline-block;
        padding: 0.28rem 0.75rem;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
    }}
    .skill-chip-match {{ background: {p['badge_excellent_bg']}; color: {p['badge_excellent_text']}; }}
    .skill-chip-gap {{ background: {p['badge_poor_bg']}; color: {p['badge_poor_text']}; }}

    /* ---- Ranked table ---- */
    .rank-table {{ display: flex; flex-direction: column; }}
    .rank-item {{
        padding: 0.7rem 0.25rem;
        border-bottom: 1px solid {p['card_border']};
    }}
    .rank-item:last-child {{ border-bottom: none; }}
    .rank-row {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    .rank-why {{
        font-size: 0.82rem;
        color: {p['text_secondary']};
        margin-top: 0.35rem;
        padding-left: 2.6rem;
    }}
    .rank-badge {{
        width: 26px; height: 26px;
        min-width: 26px;
        border-radius: 50%;
        background: {p['step_pending_bg']};
        color: {p['text_secondary']};
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.76rem;
        font-weight: 700;
    }}
    .rank-name {{ flex: 1; font-weight: 600; color: {p['text_primary']}; }}
    .rank-score {{ font-weight: 700; color: {p['text_primary']}; min-width: 68px; text-align: right; }}
    .rank-fit {{ min-width: 108px; text-align: right; }}
    .rank-sub {{ font-size: 0.78rem; color: {p['text_secondary']}; margin-top: 0.1rem; }}
    .rank-divider {{ border: none; border-top: 1px solid {p['card_border']}; margin: 0.15rem 0; }}

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

    /* ---- Mode switch ---- */
    [data-testid="stSegmentedControl"] {{ margin-bottom: 1.25rem; }}
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


def skill_chip_list(skills: list, variant: str) -> None:
    if not skills:
        st.caption("None identified.")
        return
    chips = "".join(f'<span class="skill-chip skill-chip-{variant}">{s}</span>' for s in skills)
    st.markdown(f'<div class="skill-chip-wrap">{chips}</div>', unsafe_allow_html=True)


def render_detail_panel(analysis: str, gap: dict) -> None:
    gcol1, gcol2 = st.columns(2)
    with gcol1:
        st.markdown("**✅ Matched Skills**")
        skill_chip_list(gap["matched_skills"], "match")
    with gcol2:
        st.markdown("**⚠️ Missing Skills**")
        skill_chip_list(gap["missing_skills"], "gap")
    st.markdown(analysis)


def render_role_ranked_table(df: pd.DataFrame, resume_text: str, roles: list) -> None:
    st.session_state.setdefault("row_analysis", {})
    st.session_state.setdefault("row_expanded", {})
    text_by_label = {r["label"]: r["text"] for r in roles}
    total = len(df)
    for _, row in df.iterrows():
        rank = int(row["Rank"])
        crown = "🏆 " if rank == 1 else ""
        role_label = row["Role"]
        rcol1, rcol2, rcol3, rcol4 = st.columns([0.5, 4.1, 1.1, 1.5], vertical_alignment="center")
        with rcol1:
            st.markdown(f'<div class="rank-badge">{rank}</div>', unsafe_allow_html=True)
        with rcol2:
            st.markdown(f'<div class="rank-name">{crown}{role_label}</div>', unsafe_allow_html=True)
        with rcol3:
            st.markdown(f'<div class="rank-score">{row["Score (%)"]:.2f}%</div>', unsafe_allow_html=True)
        with rcol4:
            st.markdown(fit_badge(row["Fit"]), unsafe_allow_html=True)

        st.markdown(f'<div class="rank-why">💡 {row["Why"]}</div>', unsafe_allow_html=True)

        key = f"role::{role_label}"
        is_open = st.session_state.row_expanded.get(key, False)
        arrow = "▲" if is_open else "▼"
        _, bcol, _ = st.columns([0.5, 1.5, 5.2])
        with bcol:
            if st.button(f"🔍 Detailed analysis {arrow}", key=f"detail_btn_{key}_{rank}", type="tertiary"):
                if not is_open and key not in st.session_state.row_analysis:
                    with st.spinner("Analyzing..."):
                        jd_for_role = text_by_label.get(role_label, "")
                        analysis = analyze_candidate(resume_text, jd_for_role, (row["Score (%)"], row["Fit"]))
                        gap = analyze_skills_gap(resume_text, jd_for_role)
                        st.session_state.row_analysis[key] = {"analysis": analysis, "gap": gap}
                st.session_state.row_expanded[key] = not is_open
                st.rerun()

        if is_open and key in st.session_state.row_analysis:
            with st.container(border=True):
                render_detail_panel(**st.session_state.row_analysis[key])

        if rank != total:
            st.markdown('<hr class="rank-divider">', unsafe_allow_html=True)


def render_candidate_ranked_table(df: pd.DataFrame, candidates: list, jd_text: str) -> None:
    st.session_state.setdefault("row_analysis", {})
    st.session_state.setdefault("row_expanded", {})
    by_filename = {c["filename"]: c for c in candidates}
    total = len(df)
    for _, row in df.iterrows():
        rank = int(row["Rank"])
        crown = "🏆 " if rank == 1 else ""
        filename = row["Candidate"]
        c = by_filename.get(filename, {})
        key = f"candidate::{filename}"
        is_open = st.session_state.row_expanded.get(key, False)
        arrow = "▲" if is_open else "▼"

        rcol1, rcol2, rcol3, rcol4, rcol5 = st.columns(
            [0.5, 3.0, 1.0, 1.2, 2.0], vertical_alignment="center"
        )
        with rcol1:
            st.markdown(f'<div class="rank-badge">{rank}</div>', unsafe_allow_html=True)
        with rcol2:
            st.markdown(
                f'<div class="rank-name">{crown}{row["Name"]}</div>'
                f'<div class="rank-sub">{filename}</div>',
                unsafe_allow_html=True,
            )
        with rcol3:
            st.markdown(f'<div class="rank-score">{row["Score (%)"]:.2f}%</div>', unsafe_allow_html=True)
        with rcol4:
            st.markdown(fit_badge(row["Fit"]), unsafe_allow_html=True)
        with rcol5:
            if st.button(f"🔍 Detailed analysis {arrow}", key=f"detail_btn_{key}", type="tertiary"):
                if not is_open and key not in st.session_state.row_analysis:
                    with st.spinner("Analyzing..."):
                        text = c.get("text", "")
                        analysis = analyze_candidate(text, jd_text, (row["Score (%)"], row["Fit"]))
                        gap = analyze_skills_gap(text, jd_text)
                        st.session_state.row_analysis[key] = {"analysis": analysis, "gap": gap}
                st.session_state.row_expanded[key] = not is_open
                st.rerun()

        st.markdown(f'<div class="rank-why">💡 {row["Why"]}</div>', unsafe_allow_html=True)

        if is_open and key in st.session_state.row_analysis:
            with st.container(border=True):
                render_detail_panel(**st.session_state.row_analysis[key])

        if rank != total:
            st.markdown('<hr class="rank-divider">', unsafe_allow_html=True)


def df_download_buttons(df: pd.DataFrame, base_filename: str) -> None:
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            f"{base_filename}.csv",
            "text/csv",
            use_container_width=True,
        )
    with d2:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Results")
        st.download_button(
            "📥 Download Excel",
            buf.getvalue(),
            f"{base_filename}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


# -------------------------
# Session state
# -------------------------
for k in [
    "analysis", "score", "salary_prediction", "sanitized_md",
    "skills_gap", "interview_questions", "best_fit_df", "best_fit_roles_used",
    "batch_ranked_df", "batch_candidates", "compare_results",
]:
    st.session_state.setdefault(k, None)
st.session_state.setdefault("jd_roles", [{"label": "Role 1", "text": ""}, {"label": "Role 2", "text": ""}])
st.session_state.setdefault("row_analysis", {})
st.session_state.setdefault("row_expanded", {})

# -------------------------
# Hero header
# -------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">🧭</div>
        <h1>HR Resume Assistant</h1>
        <p>Match candidates to a job description, rank an entire batch, estimate relocation salary, and strip personal information — all in one place.</p>
        <div class="hero-chips">
            <span class="hero-chip">🎯 Match Score</span>
            <span class="hero-chip">👥 Batch Rank</span>
            <span class="hero-chip">💰 Salary Insight</span>
            <span class="hero-chip">🧹 PII Sanitize</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Mode switch
# -------------------------
mode = st.segmented_control(
    "Mode",
    ["📄 Single Candidate", "👥 Batch & Compare"],
    default="📄 Single Candidate",
    label_visibility="collapsed",
    key="app_mode",
)
if mode is None:
    mode = "📄 Single Candidate"

uploaded_resume = None
jd_text = ""
resume_text = ""

# =========================================================
# SINGLE CANDIDATE MODE
# =========================================================
if mode == "📄 Single Candidate":
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            uploaded_resume = st.file_uploader(
                "📂 Upload Resume (PDF or DOCX)", type=["pdf", "docx"], key="single_resume_uploader"
            )
        with col2:
            jd_text = st.text_area(
                "📝 Paste Job Description here (optional)", height=180, key="single_jd_text"
            )

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
            for k in [
                "analysis", "score", "salary_prediction", "sanitized_md",
                "skills_gap", "interview_questions", "best_fit_df", "best_fit_roles_used",
            ]:
                st.session_state[k] = None
            st.session_state.row_analysis = {}
            st.session_state.jd_roles = [{"label": "Role 1", "text": ""}, {"label": "Role 2", "text": ""}]
            st.rerun()

    if uploaded_resume is None:
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            feature_card("🎯", "indigo", "Match & Analyze", "Score a resume against a job description, see a skills-gap breakdown, and get suggested interview questions.")
        with fc2:
            feature_card("💰", "emerald", "Salary Insights", "Estimate a fair relocation salary using live market trend data.")
        with fc3:
            feature_card("🧹", "cyan", "Sanitize & Export", "Strip personal information and export a clean, formatted resume.")
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
        st.info("👋 Upload a resume above to get started.")
        st.stop()

    resume_text = extract_resume_text(uploaded_resume)

    if not resume_text.strip():
        st.error("Could not extract any text from that file.")
        st.stop()

    candidate_name = guess_candidate_name(resume_text, uploaded_resume.name)
    st.markdown(
        f"""
        <div class="file-strip">
            ✅ <b>{candidate_name}</b> ({uploaded_resume.name}) loaded — {len(resume_text.split())} words extracted.
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_match, tab_bestfit, tab_salary, tab_sanitize = st.tabs(
        ["🎯 Match & Analyze", "🧭 Best-Fit Role", "💰 Salary Insights", "🧹 Sanitize & Export"]
    )

    # ---- Tab: Match & Analyze ----
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
                        gap = analyze_skills_gap(resume_text, jd_text)
                        st.session_state.score = score
                        st.session_state.analysis = analysis
                        st.session_state.skills_gap = gap
                        st.session_state.interview_questions = None
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

            if st.session_state.skills_gap:
                with st.container(border=True):
                    section_eyebrow("📊", "Skills Gap", "emerald")
                    gcol1, gcol2 = st.columns(2)
                    with gcol1:
                        st.markdown("**✅ Matched Skills**")
                        skill_chip_list(st.session_state.skills_gap["matched_skills"], "match")
                    with gcol2:
                        st.markdown("**⚠️ Missing Skills**")
                        skill_chip_list(st.session_state.skills_gap["missing_skills"], "gap")

                if st.button("❓ Generate Interview Questions"):
                    with st.spinner("Drafting interview questions..."):
                        try:
                            st.session_state.interview_questions = generate_interview_questions(
                                resume_text, jd_text, st.session_state.skills_gap["missing_skills"]
                            )
                        except Exception as e:
                            st.error(f"Error generating questions: {e}")

                if st.session_state.interview_questions:
                    with st.container(border=True):
                        section_eyebrow("❓", "Suggested Interview Questions", "emerald")
                        st.markdown(st.session_state.interview_questions)

    # ---- Tab: Best-Fit Role (multi-JD matching) ----
    with tab_bestfit:
        st.caption("Compare this one candidate against several open roles to see which they fit best.")
        for i, role in enumerate(st.session_state.jd_roles):
            with st.container(border=True):
                rcol1, rcol2 = st.columns([4, 1])
                with rcol1:
                    role["label"] = st.text_input("Role name", value=role["label"], key=f"role_label_{i}")
                with rcol2:
                    st.markdown("<div style='height: 1.85rem'></div>", unsafe_allow_html=True)
                    if st.button("✕ Remove", key=f"role_remove_{i}", use_container_width=True):
                        if len(st.session_state.jd_roles) > 1:
                            st.session_state.jd_roles.pop(i)
                            st.rerun()
                role["text"] = st.text_area(
                    "Job description", value=role["text"], key=f"role_text_{i}", height=120
                )

        if st.button("➕ Add another role"):
            st.session_state.jd_roles.append({"label": f"Role {len(st.session_state.jd_roles) + 1}", "text": ""})
            st.rerun()

        if st.button("🧭 Find Best Fit", type="primary"):
            valid_roles = [r for r in st.session_state.jd_roles if r["text"].strip()]
            if not valid_roles:
                st.warning("Add at least one job description with text.")
            else:
                with st.spinner("Scoring roles..."):
                    df = rank_roles(resume_text, valid_roles)
                with st.spinner("Summarizing why each role ranked where it did..."):
                    text_by_label = {r["label"]: r["text"] for r in valid_roles}
                    briefs = []
                    for _, row in df.iterrows():
                        try:
                            briefs.append(generate_rank_brief(
                                resume_text, text_by_label[row["Role"]], row["Score (%)"], row["Fit"]
                            ))
                        except Exception:
                            briefs.append(fit_reason(row["Fit"]))
                    df["Why"] = briefs
                st.session_state.best_fit_df = df
                st.session_state.best_fit_roles_used = valid_roles
                st.session_state.row_analysis = {}

        if st.session_state.best_fit_df is not None:
            with st.container(border=True):
                section_eyebrow("🧭", "Best-Fit Ranking", "indigo")
                render_role_ranked_table(
                    st.session_state.best_fit_df, resume_text, st.session_state.best_fit_roles_used
                )
            df_download_buttons(st.session_state.best_fit_df, "best_fit_roles")

    # ---- Tab: Salary Insights ----
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

    # ---- Tab: Sanitize & Export ----
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

# =========================================================
# BATCH & COMPARE MODE
# =========================================================
else:
    with st.container(border=True):
        uploaded_batch = st.file_uploader(
            "📂 Upload Resumes (PDF or DOCX, multiple allowed)",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            key="batch_resume_uploader",
        )
        batch_jd_text = st.text_area(
            "📝 Paste Job Description here", height=180, key="batch_jd_text"
        )

    with st.sidebar:
        is_light = st.session_state.theme == "light"
        toggled = st.toggle("☀️ Light mode", value=is_light, key="theme_toggle")
        if toggled != is_light:
            st.session_state.theme = "light" if toggled else "dark"
            st.rerun()
        st.markdown("### 🧭 HR Resume Assistant")
        st.caption("AI-assisted resume screening, salary insight & PII sanitization.")
        st.markdown("---")
        st.markdown("**Batch mode**")
        n_queued = len(uploaded_batch) if uploaded_batch else 0
        st.caption(f"{n_queued} resume(s) queued for ranking.")
        st.markdown("---")
        st.markdown("**Connection status**")
        st.markdown(secret_status("GOOGLE_API_KEY"), unsafe_allow_html=True)
        st.markdown(secret_status("HF_TOKEN"), unsafe_allow_html=True)
        st.markdown(secret_status("TAVILY_API_KEY"), unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🔄 Start Over", use_container_width=True):
            for k in ["batch_ranked_df", "batch_candidates", "compare_results"]:
                st.session_state[k] = None
            st.session_state.row_analysis = {}
            st.rerun()

    if not uploaded_batch:
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            feature_card("👥", "indigo", "Rank a Batch", "Upload every resume for a role and get them scored and ranked against the job description.")
        with fc2:
            feature_card("🔍", "emerald", "Compare Finalists", "Pick 2-4 top candidates for a side-by-side pros/cons and skills-gap comparison.")
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
        st.info("👋 Upload two or more resumes above to get started.")
        st.stop()

    if not batch_jd_text.strip():
        with st.container(border=True):
            empty_state("🔒", "Job description required", "Paste a job description above to rank the uploaded resumes.")
        st.stop()

    candidates = []
    for f in uploaded_batch:
        text = extract_resume_text(f)
        if text.strip():
            candidates.append({
                "filename": f.name,
                "text": text,
                "name": guess_candidate_name(text, f.name),
                "bytes": f.getvalue(),
                "mime": f.type,
            })

    st.markdown(
        f"""
        <div class="file-strip">
            ✅ <b>{len(candidates)} resume(s)</b> loaded and ready to rank.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("📊 Rank Candidates", type="primary"):
        with st.spinner("Scoring candidates..."):
            df = rank_candidates(candidates, batch_jd_text)
        with st.spinner("Summarizing why each candidate ranked where they did..."):
            text_by_filename = {c["filename"]: c["text"] for c in candidates}
            briefs = []
            for _, row in df.iterrows():
                try:
                    briefs.append(generate_rank_brief(
                        text_by_filename[row["Candidate"]], batch_jd_text, row["Score (%)"], row["Fit"]
                    ))
                except Exception:
                    briefs.append(fit_reason(row["Fit"]))
            df["Why"] = briefs
        st.session_state.batch_ranked_df = df
        st.session_state.batch_candidates = candidates
        st.session_state.compare_results = None
        st.session_state.row_analysis = {}

    if st.session_state.batch_ranked_df is not None:
        with st.container(border=True):
            section_eyebrow("📊", "Ranked Candidates", "indigo")
            render_candidate_ranked_table(
                st.session_state.batch_ranked_df, st.session_state.batch_candidates, batch_jd_text
            )
        df_download_buttons(st.session_state.batch_ranked_df, "ranked_candidates")

        st.markdown("---")
        section_eyebrow("🔍", "Side-by-Side Comparison", "emerald")
        name_by_filename = {c["filename"]: c["name"] for c in st.session_state.batch_candidates}
        filenames = st.session_state.batch_ranked_df["Candidate"].tolist()
        selected = st.multiselect(
            "Select 2-4 candidates to compare in depth",
            filenames,
            format_func=lambda fn: name_by_filename.get(fn, fn),
            max_selections=4,
        )

        if st.button("🔍 Compare Selected", type="primary"):
            if len(selected) < 2:
                st.warning("Select at least 2 candidates to compare.")
            else:
                with st.spinner("Comparing candidates..."):
                    results = {}
                    for filename in selected:
                        c = next(c for c in st.session_state.batch_candidates if c["filename"] == filename)
                        score = match_resume_to_jd(c["text"], batch_jd_text)
                        analysis = analyze_candidate(c["text"], batch_jd_text, score)
                        gap = analyze_skills_gap(c["text"], batch_jd_text)
                        results[filename] = {
                            "score": score, "analysis": analysis, "gap": gap,
                            "name": c["name"], "bytes": c["bytes"], "mime": c["mime"],
                        }
                    st.session_state.compare_results = results

        if st.session_state.compare_results:
            cols = st.columns(len(st.session_state.compare_results))
            for col, (filename, data) in zip(cols, st.session_state.compare_results.items()):
                with col:
                    with st.container(border=True):
                        section_eyebrow("👤", data["name"], "cyan")
                        st.caption(filename)
                        st.download_button(
                            "📄 Download resume", data=data["bytes"], file_name=filename,
                            mime=data["mime"] or "application/octet-stream",
                            key=f"dl_compare_{filename}", use_container_width=True,
                        )
                        score_val, fit_cat = data["score"]
                        st.metric("Score", f"{score_val:.2f}%")
                        st.markdown(fit_badge(fit_cat), unsafe_allow_html=True)
                        st.markdown("**✅ Matched**")
                        skill_chip_list(data["gap"]["matched_skills"], "match")
                        st.markdown("**⚠️ Missing**")
                        skill_chip_list(data["gap"]["missing_skills"], "gap")
                        with st.expander("Full analysis"):
                            st.markdown(data["analysis"])
