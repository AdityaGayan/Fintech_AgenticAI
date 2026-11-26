import hashlib

import streamlit as st

from src.agents.coordinator_agent import (
    generate_srs_from_input,
)
from src.db.connection import init_db


st.set_page_config(page_title="FinTech AI Studio", page_icon="F", layout="wide", initial_sidebar_state="collapsed")
init_db()

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root { --bg:#080d18; --panel:#101827; --panel2:#141f31; --line:#22314a; --text:#edf4ff; --muted:#8ea1bc; --blue:#62a1ff; --cyan:#5eead4; }
        .stApp { background:radial-gradient(circle at 80% -10%,#172d52 0,var(--bg) 38rem); color:var(--text); }
        [data-testid="stHeader"] { background:transparent; }
        .block-container { max-width:1320px; padding:1.6rem 3.2rem 4rem; }
        h1,h2,h3,p,label,.stMarkdown { font-family:'DM Sans',sans-serif; }
        h1,h2,h3,strong { color:var(--text)!important; }
        h1 { font-family:'Space Grotesk',sans-serif; letter-spacing:-.045em; }
        .hero { display:flex; align-items:flex-end; justify-content:space-between; border-bottom:1px solid var(--line); padding:.7rem 0 1.5rem; margin-bottom:1.6rem; }
        .eyebrow,.section-label { color:var(--blue); font-size:.72rem; font-weight:700; letter-spacing:.15em; text-transform:uppercase; }
        .hero h1 { font-size:2.55rem; margin:.35rem 0; }
        .hero p { color:var(--muted); margin:0; max-width:760px; }
        .hero-mark { color:var(--cyan); font-family:'Space Grotesk',sans-serif; font-size:1.1rem; font-weight:700; letter-spacing:.08em; }
        .section-label { color:var(--muted); margin:.2rem 0 .65rem; }
        .workflow-card,.recommendation,.detail-card { background:rgba(16,24,39,.92); border:1px solid var(--line); border-radius:14px; }
        .workflow-card { padding:1.25rem; min-height:218px; }
        .workflow-title { color:var(--text); font-size:1.03rem; font-weight:700; margin-bottom:1rem; }
        .workflow-step { display:flex; gap:.7rem; align-items:center; color:var(--muted); font-size:.9rem; padding:.47rem 0; border-bottom:1px solid rgba(34,49,74,.6); }
        .workflow-step:last-child { border-bottom:0; }
        .step-dot { width:8px; height:8px; background:var(--cyan); border-radius:50%; box-shadow:0 0 12px rgba(94,234,212,.6); }
        .input-help,.caption { color:var(--muted); font-size:.82rem; }
        textarea,[data-baseweb="textarea"] textarea { background:#0b1322!important; color:var(--text)!important; border-color:var(--line)!important; }
        [data-testid="stMetric"] { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:1rem; }
        [data-testid="stMetricLabel"] { color:var(--muted)!important; }
        [data-testid="stMetricValue"] { color:var(--text)!important; font-family:'Space Grotesk',sans-serif; }
        .stButton>button { background:var(--blue); color:#07101e; border:0; border-radius:9px; font-weight:700; min-height:2.85rem; }
        .stButton>button:hover { background:#8bbaff; color:#07101e; }
        [data-testid="stExpander"] { background:var(--panel); border:1px solid var(--line); border-radius:11px; margin-bottom:.65rem; }
        [data-testid="stExpander"] summary p { color:var(--text)!important; font-weight:600; }
        .recommendation { padding:1.3rem 1.45rem; margin-bottom:1rem; border-color:#315b91; background:linear-gradient(110deg,#122b4d,#101827 70%); }
        .recommendation .model { color:var(--cyan); font-family:'Space Grotesk',sans-serif; font-size:1.75rem; font-weight:700; }
        .detail-card { padding:1rem 1.15rem; height:100%; }
        .detail-card .label { color:var(--blue); font-size:.7rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
        .detail-card .text { color:#c5d2e5; line-height:1.55; margin-top:.45rem; }
        [data-testid="stAlert"] { background:var(--panel2); border-color:var(--line); color:var(--text); }
        hr { border-color:var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div><div class="eyebrow">FinTech AI Studio / Operations Console</div>
        <h1>Requirements intelligence, in one view.</h1>
        <p>Transform stakeholder language into traceable requirements, compliance insights, risk signals, and an SDLC recommendation.</p></div>
        <div class="hero-mark">LIVE READY</div>
    </div>
    """,
    unsafe_allow_html=True,
)

input_col, workflow_col = st.columns([1.55, 1], gap="large")
with input_col:
    st.markdown('<div class="section-label">01 / Intake</div>', unsafe_allow_html=True)
    with st.container(border=True):
        raw_input = st.text_area(
            "Stakeholder context",
            height=205,
            placeholder="Example: The payment platform must log out users after 10 minutes of inactivity and encrypt stored card data.",
        )
        st.markdown('<div class="input-help">PII is masked before the request reaches the analysis pipeline.</div>', unsafe_allow_html=True)
        run_analysis = st.button("Start analysis", type="primary", use_container_width=True)

with workflow_col:
    st.markdown('<div class="section-label">Pipeline status</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="workflow-card"><div class="workflow-title">SRS first. SDLC second.</div>
        <div class="workflow-step"><span class="step-dot"></span>Secure and sanitize input</div>
        <div class="workflow-step"><span class="step-dot"></span>Retrieve compliance guidance</div>
        <div class="workflow-step"><span class="step-dot"></span>Generate and review the IEEE SRS</div>
        <div class="workflow-step"><span class="step-dot"></span>Generate the SDLC model and justification</div></div>
        """,
        unsafe_allow_html=True,
    )

if run_analysis:
    if not raw_input.strip():
        st.warning("Add stakeholder context before starting the analysis.")
    else:
        with st.status("Generating SRS...", expanded=True) as srs_status:
            st.write("Sanitizing stakeholder input")
            st.write("Retrieving compliance guidance")
            st.write("Generating the detailed SRS with the RE agent")
            st.session_state["draft_analysis"] = {
                **generate_srs_from_input(raw_input),
                "input_signature": hashlib.sha256(raw_input.strip().encode("utf-8")).hexdigest(),
            }
            st.session_state.pop("recommendation", None)
            srs_status.update(label="SRS ready", state="complete", expanded=False)

input_signature = hashlib.sha256(raw_input.strip().encode("utf-8")).hexdigest()
draft = st.session_state.get("draft_analysis")
if draft and draft.get("input_signature") != input_signature:
    draft = None
if draft:
    if draft["detected_pii"]:
        st.error(f"PII masked: {', '.join(draft['detected_pii'])}")

    st.markdown('<div class="section-label">02 / IEEE SRS</div>', unsafe_allow_html=True)
    srs_document = draft["srs_document"]
    st.download_button(
        "Download SRS (Markdown)",
        data=srs_document["markdown"],
        file_name="software_requirements_specification.md",
        mime="text/markdown",
        use_container_width=True,
    )
    st.markdown(srs_document["markdown"])

    recommendation = draft["sdlc_recommendation"]
    if recommendation:
        st.markdown('<div class="section-label">03 / SDLC decision</div>', unsafe_allow_html=True)
        metrics = st.columns(1, gap="medium")
        metrics[0].metric("Recommended model", recommendation["recommended_model"])
        st.markdown(
            f"""<div class="recommendation"><div class="model">{recommendation['recommended_model']}</div>
            <div class="caption">Selected directly from the stakeholder input by the SDLC agent.</div></div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="detail-card"><div class="label">Why this model was chosen</div><div class="text">{recommendation["justification"]}</div></div>',
            unsafe_allow_html=True,
        )

