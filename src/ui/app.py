import hashlib

import streamlit as st

from src.agents.coordinator_agent import generate_srs_from_input
from src.db.connection import init_db


st.set_page_config(
    page_title="FinTech Requirements Studio",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)
init_db()

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root {
            --ink: #eaf2ff;
            --muted: #8fa4c2;
            --line: rgba(137, 170, 219, .18);
            --panel: rgba(13, 24, 43, .78);
            --panel-strong: #111f36;
            --blue: #80aefc;
            --mint: #62e6c4;
            --orange: #ffb86b;
        }
        .stApp {
            color: var(--ink);
            background:
                radial-gradient(circle at 8% 0%, rgba(49, 104, 192, .28), transparent 30rem),
                radial-gradient(circle at 95% 18%, rgba(44, 180, 161, .13), transparent 25rem),
                #07101e;
        }
        [data-testid="stHeader"] { background: transparent; }
        .block-container { max-width: 1420px; padding: 2.2rem 3.5rem 5rem; }
        h1, h2, h3, p, label, .stMarkdown { font-family: 'DM Sans', sans-serif; }
        h1, h2, h3, strong { color: var(--ink) !important; }
        h1 { font: 700 3.35rem/1.02 'Space Grotesk', sans-serif; letter-spacing: -.065em; margin: .35rem 0 1rem; }
        h2 { font: 600 1.55rem 'Space Grotesk', sans-serif; }
        .brand-row { display:flex; justify-content:space-between; align-items:center; margin-bottom:3.2rem; }
        .brand { color:var(--ink); font:700 1.1rem 'Space Grotesk', sans-serif; letter-spacing:-.03em; }
        .brand span { color:var(--mint); }
        .live-pill { border:1px solid rgba(98,230,196,.3); color:var(--mint); border-radius:999px; padding:.38rem .75rem; font-size:.68rem; font-weight:700; letter-spacing:.12em; }
        .eyebrow, .section-kicker { color:var(--blue); font-size:.68rem; font-weight:700; letter-spacing:.17em; text-transform:uppercase; }
        .hero-copy { color:var(--muted); font-size:1.02rem; line-height:1.65; max-width:660px; }
        .hero-note { border-left:2px solid var(--mint); padding:1rem 1.2rem; color:#c9d8ed; background:rgba(98,230,196,.05); border-radius:0 12px 12px 0; line-height:1.55; }
        .section-kicker { margin:2.6rem 0 .75rem; color:var(--muted); }
        [data-testid="stVerticalBlockBorderWrapper"] { background:var(--panel); border:1px solid var(--line); border-radius:18px; }
        textarea, [data-baseweb="textarea"] textarea { background:#091627 !important; color:var(--ink) !important; border:1px solid var(--line) !important; border-radius:12px !important; line-height:1.6 !important; }
        textarea:focus { border-color:var(--blue) !important; box-shadow:0 0 0 1px var(--blue) !important; }
        .hint { color:var(--muted); font-size:.78rem; margin-top:.65rem; }
        .stButton > button, .stDownloadButton > button { min-height:2.85rem; border:0; border-radius:10px; color:#07121f; background:linear-gradient(135deg, #a6c7ff, #6ee8cf); font-weight:700; transition:transform .2s, box-shadow .2s; }
        .stButton > button:hover, .stDownloadButton > button:hover { transform:translateY(-1px); box-shadow:0 8px 24px rgba(98,230,196,.18); color:#07121f; }
        [data-testid="stTab"] { color:var(--muted); font-weight:600; }
        [aria-selected="true"] { color:var(--ink) !important; }
        [data-baseweb="tab-highlight"] { background:var(--mint); }
        .model-card { padding:1.45rem 1.6rem; border:1px solid rgba(98,230,196,.28); border-radius:16px; background:linear-gradient(135deg, rgba(19,66,78,.8), rgba(15,29,51,.92)); }
        .model-label { color:var(--muted); font-size:.7rem; letter-spacing:.15em; text-transform:uppercase; }
        .model-name { color:var(--mint); font:700 2.15rem 'Space Grotesk', sans-serif; margin:.3rem 0 1.1rem; }
        .justification { color:#d8e5f5; font-size:1rem; line-height:1.7; }
        .source-chip { display:inline-block; color:#b8cbee; border:1px solid var(--line); background:rgba(128,174,252,.06); border-radius:999px; padding:.4rem .7rem; margin:.25rem .25rem 0 0; font-size:.78rem; }
        .pii-note { color:#ffd29b; border:1px solid rgba(255,184,107,.25); background:rgba(255,184,107,.08); border-radius:10px; padding:.75rem 1rem; }
        [data-testid="stStatusWidget"] { border-color:var(--line); background:var(--panel-strong); }
        .footer { margin-top:4rem; color:#607694; text-align:center; font-size:.75rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="brand-row"><div class="brand">FINTECH <span>◈</span> REQUIREMENTS STUDIO</div><div class="live-pill">AI PIPELINE READY</div></div>',
    unsafe_allow_html=True,
)

hero_left, hero_right = st.columns([1.35, .65], gap="large")
with hero_left:
    st.markdown('<div class="eyebrow">Requirements intelligence / v2</div>', unsafe_allow_html=True)
    st.title("Turn stakeholder language into an engineering decision.")
    st.markdown(
        '<div class="hero-copy">Generate a detailed IEEE-style SRS and an evidence-grounded SDLC recommendation from one stakeholder brief.</div>',
        unsafe_allow_html=True,
    )
with hero_right:
    st.markdown(
        '<div class="hero-note"><strong>One brief. Two expert agents.</strong><br>RE creates the specification. SDLC evaluates the original stakeholder context and explains the model choice.</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-kicker">01 / Stakeholder brief</div>', unsafe_allow_html=True)
with st.container(border=True):
    raw_input = st.text_area(
        "What are you building?",
        height=190,
        label_visibility="visible",
        placeholder="Example: Build a payment platform for small businesses. It must support card payments, encrypt stored card data, log users out after 10 minutes of inactivity, and provide audit-ready transaction records.",
    )
    action_col, hint_col = st.columns([.34, .66], vertical_alignment="center")
    with action_col:
        run_analysis = st.button("Generate SRS + SDLC decision", type="primary", use_container_width=True)
    with hint_col:
        st.markdown('<div class="hint">PII is masked before retrieval and model calls. Both agents run together after compliance context is retrieved.</div>', unsafe_allow_html=True)

if run_analysis:
    if not raw_input.strip():
        st.warning("Add a stakeholder brief before generating the specification.")
    else:
        with st.spinner("Generating your SRS and SDLC decision…"):
            st.session_state["analysis"] = {
                **generate_srs_from_input(raw_input),
                "input_signature": hashlib.sha256(raw_input.strip().encode("utf-8")).hexdigest(),
            }

input_signature = hashlib.sha256(raw_input.strip().encode("utf-8")).hexdigest()
analysis = st.session_state.get("analysis")
if analysis and analysis.get("input_signature") != input_signature:
    analysis = None

if analysis:
    if analysis["detected_pii"]:
        st.markdown(
            f'<div class="pii-note">Protected data masked: {", ".join(analysis["detected_pii"])}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-kicker">02 / Generated intelligence</div>', unsafe_allow_html=True)
    requirements_tab, srs_tab, decision_tab, evidence_tab = st.tabs([
        "Extracted requirements", "SRS document", "SDLC decision", "Evidence & controls"
    ])

    with requirements_tab:
        st.caption("Requirements extracted by the RE agent and used to enrich the SRS.")
        for requirement in analysis["requirements"]:
            with st.container(border=True):
                heading_col, priority_col = st.columns([.8, .2])
                with heading_col:
                    st.markdown(f"**{requirement['id']}** · {requirement['category']}")
                with priority_col:
                    st.caption(f"{requirement['priority']} priority")
                st.write(requirement["statement"])
                st.caption(
                    f"Risk: {requirement['risk_level']} · "
                    f"Compliance: {requirement['compliance_mapping']}"
                )

    with srs_tab:
        download_col, _ = st.columns([.28, .72])
        with download_col:
            st.download_button(
                "Download PDF",
                data=analysis["srs_document"]["pdf_bytes"],
                file_name=analysis["srs_document"]["pdf_filename"],
                mime="application/pdf",
                use_container_width=True,
            )
        st.markdown(analysis["srs_document"]["markdown"])

    with decision_tab:
        recommendation = analysis["sdlc_recommendation"]
        st.markdown(
            f'<div class="model-card"><div class="model-label">Recommended SDLC model</div><div class="model-name">{recommendation["recommended_model"]}</div><div class="model-label">Why this model was chosen</div><div class="justification">{recommendation["justification"]}</div></div>',
            unsafe_allow_html=True,
        )

    with evidence_tab:
        st.markdown("#### Retrieved compliance context")
        st.caption("These local policy sources were supplied to both agents as grounding context.")
        sources = analysis["rag_sources_used"]
        if sources:
            st.markdown("".join(f'<span class="source-chip">{source}</span>' for source in sources), unsafe_allow_html=True)
        else:
            st.info("No matching local policy source was returned for this brief.")

st.markdown('<div class="footer">FinTech Requirements Studio · traceable specifications for regulated software</div>', unsafe_allow_html=True)
