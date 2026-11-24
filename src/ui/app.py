import hashlib

import streamlit as st

from src.agents.coordinator_agent import (
    extract_requirements,
    recommend_from_requirements,
    save_requirements,
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
        <div class="workflow-card"><div class="workflow-title">Four agents. One decision surface.</div>
        <div class="workflow-step"><span class="step-dot"></span>Secure and sanitize input</div>
        <div class="workflow-step"><span class="step-dot"></span>Retrieve compliance guidance</div>
        <div class="workflow-step"><span class="step-dot"></span>Extract and assess requirements</div>
        <div class="workflow-step"><span class="step-dot"></span>Recommend the SDLC model</div></div>
        """,
        unsafe_allow_html=True,
    )

if run_analysis:
    if not raw_input.strip():
        st.warning("Add stakeholder context before starting the analysis.")
    else:
        with st.status("Extracting requirements...", expanded=True) as extraction_status:
            st.write("Sanitizing stakeholder input")
            st.write("Extracting and assessing requirements")
            st.session_state["draft_analysis"] = {
                **extract_requirements(raw_input),
                "input_signature": hashlib.sha256(raw_input.strip().encode("utf-8")).hexdigest(),
            }
            st.session_state.pop("recommendation", None)
            st.session_state.pop("final_requirements", None)
            extraction_status.update(label="Requirements ready for review", state="complete", expanded=False)

input_signature = hashlib.sha256(raw_input.strip().encode("utf-8")).hexdigest()
draft = st.session_state.get("draft_analysis")
if draft and draft.get("input_signature") != input_signature:
    draft = None
if draft:
    requirements = draft["requirements"]

    if draft["detected_pii"]:
        st.error(f"PII masked: {', '.join(draft['detected_pii'])}")

    st.markdown('<div class="section-label">02 / Requirements gathered</div>', unsafe_allow_html=True)
    st.caption("Review or edit the extracted requirements before asking the AI to select an SDLC model.")

    with st.form("requirements_review"):
        edited_requirements = []
        for index, req in enumerate(requirements):
            with st.expander(f"{req['id']}   |   {req['priority']} priority   |   {req['risk_level']} risk", expanded=True):
                # Give each submission its own widget state so a new
                # stakeholder input cannot reuse the previous values.
                widget_key = f"{input_signature}_{index}"
                statement = st.text_area("Requirement", value=req["statement"], key=f"statement_{widget_key}")
                details = st.columns(3)
                category = details[0].text_input("Category", value=req["category"], key=f"category_{widget_key}")
                priority = details[1].selectbox("Priority", ["Low", "Medium", "High", "Critical"], index=["Low", "Medium", "High", "Critical"].index(req["priority"]) if req["priority"] in ["Low", "Medium", "High", "Critical"] else 1, key=f"priority_{widget_key}")
                risk = details[2].selectbox("Risk level", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(req["risk_level"]) if req["risk_level"] in ["Low", "Medium", "High"] else 1, key=f"risk_{widget_key}")
                edited = dict(req)
                edited.update(statement=statement, category=category, priority=priority, risk_level=risk)
                edited_requirements.append(edited)

        determine_model = st.form_submit_button("Save edits and determine SDLC model", type="primary", use_container_width=True)

    if determine_model:
        with st.status("Determining the SDLC model...", expanded=True) as recommendation_status:
            st.write("Saving reviewed requirements")
            final_requirements = save_requirements(edited_requirements)
            st.write("Sending the reviewed requirements to the SDLC agent")
            recommendation = recommend_from_requirements(final_requirements, draft["retrieved_policies"])
            recommendation_status.update(label="SDLC recommendation ready", state="complete", expanded=False)
        st.session_state["final_requirements"] = final_requirements
        st.session_state["recommendation"] = recommendation

    recommendation = st.session_state.get("recommendation")
    final_requirements = st.session_state.get("final_requirements", requirements)
    if recommendation:
        st.markdown('<div class="section-label">03 / Decision output</div>', unsafe_allow_html=True)
        metrics = st.columns(3, gap="medium")
        metrics[0].metric("Recommended model", recommendation["recommended_model"])
        metrics[1].metric("Confidence", f"{recommendation['confidence_percentage']}%")
        metrics[2].metric("Requirements reviewed", len(final_requirements))
        st.markdown(
            f"""<div class="recommendation"><div class="model">{recommendation['recommended_model']}</div>
            <div class="caption">Generated from the requirements you reviewed ({recommendation.get("selection_source", "AI")} selection).</div></div>""",
            unsafe_allow_html=True,
        )
        detail_cols = st.columns(2, gap="medium")
        with detail_cols[0]:
            st.markdown(f'<div class="detail-card"><div class="label">Rationale</div><div class="text">{recommendation["justification"]}</div></div>', unsafe_allow_html=True)
        with detail_cols[1]:
            st.markdown(f'<div class="detail-card"><div class="label">Key phases</div><div class="text">{recommendation["key_phases"]}</div></div>', unsafe_allow_html=True)
