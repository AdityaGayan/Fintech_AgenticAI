import streamlit as st
from src.db.connection import init_db
from src.agents.coordinator_agent import run_full_pipeline

# Initialize database on startup
init_db()

st.set_page_config(page_title="FinTech Agentic RE Platform", layout="wide", initial_sidebar_state="collapsed")

st.title("🏦 Agentic AI Requirements Engineering Platform")
st.markdown("Automated RE, Compliance Mapping, Risk Analysis, and SDLC Selection.")
st.divider()

tabs = st.tabs(["Agent Processing"])

with tabs[0]:
    st.subheader("Stakeholder Input")
    raw_input = st.text_area(
        "Paste interview transcripts, customer emails, or raw notes:",
        height=150,
        placeholder="E.g., We need the new payment system to log out users after 10 minutes of inactivity..."
    )
    
    if st.button("Run Multi-Agent Analysis", type="primary"):
        if not raw_input.strip():
            st.warning("Please enter text to analyze.")
        else:
            with st.spinner("Agents are analyzing, checking RAG policies, and assessing risk..."):
                result = run_full_pipeline(raw_input=raw_input)
            
            st.success("Analysis Complete!")
            
            # Display Recommended Model immediately after analysis completes
            sdlc = result["sdlc_recommendation"]
            st.subheader("SDLC Recommendation")
            st.metric(
                label="Recommended Model", 
                value=sdlc["recommended_model"], 
                delta=f"{sdlc['confidence_percentage']}% Match"
            )
            st.write(f"**Justification:** {sdlc['justification']}")
            st.write(f"**Key Phases:** {sdlc['key_phases']}")
            st.divider()

            if result["detected_pii"]:
                st.error(f"🔒 PII Masked: {', '.join(result['detected_pii'])}")
                
            if result["rag_sources_used"]:
                st.info(f"📚 RAG Policies Referenced: {', '.join(set(result['rag_sources_used']))}")
            
            st.subheader("Extracted Requirements")
            for req in result["requirements"]:
                with st.expander(f"{req['id']} | Priority: {req['priority']} | Risk: {req['risk_level']}"):
                    st.write(f"**Statement:** {req['statement']}")
                    st.write(f"**Category:** {req['category']}")
                    st.write(f"**Compliance Mapping:** {req['compliance_mapping']}")
                    st.write(f"**Justification/Ambiguities:** {req['business_justification']}")
