import streamlit as st
import pandas as pd
from src.db.connection import init_db
from src.db.repository import RequirementRepository, AuditRepository
from src.agents.coordinator_agent import run_full_pipeline

# Initialize database on startup
init_db()

st.set_page_config(page_title="FinTech Agentic RE Platform", layout="wide")

st.title("🏦 Agentic AI Requirements Engineering Platform")
st.markdown("Automated RE, Compliance Mapping, Risk Analysis, and SDLC Selection.")

# Sidebar - User Session & Config
st.sidebar.header("User Context")
current_user = st.sidebar.text_input("Username", value="Aditya")
current_role = st.sidebar.selectbox("Role", ["Admin", "Compliance_Officer", "Business_Analyst", "Project_Manager"])

st.sidebar.divider()
st.sidebar.header("Project Configuration")
domain = st.sidebar.selectbox("Financial Domain", [
    "Digital Banking", "Loan Origination", "Payment Processing", "Fraud Detection"
])
change_frequency = st.sidebar.selectbox("Requirement Volatility", ["High", "Moderate", "Stable"])

tabs = st.tabs(["1. Agent Processing", "2. Traceability & HITL Approval", "3. Audit Logs"])

with tabs[0]:
    st.header("Stakeholder Input")
    raw_input = st.text_area(
        "Paste interview transcripts, customer emails, or raw notes:",
        height=150,
        placeholder="E.g., We need the new payment system to log out users after 10 minutes of inactivity..."
    )
    
    if st.button("Run Multi-Agent Analysis"):
        if not raw_input.strip():
            st.warning("Please enter text to analyze.")
        else:
            with st.spinner("Agents are analyzing, checking RAG policies, and assessing risk..."):
                result = run_full_pipeline(
                    raw_input=raw_input, 
                    domain=domain, 
                    change_frequency=change_frequency,
                    user=current_user,
                    role=current_role
                )
            
            st.success("Analysis Complete!")
            
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
                    
            st.subheader("SDLC Recommendation")
            sdlc = result["sdlc_recommendation"]
            st.metric(label="Recommended Model", value=sdlc["recommended_model"], delta=f"{sdlc['confidence_percentage']}% Match")
            st.write(f"**Justification:** {sdlc['justification']}")
            st.write(f"**Key Phases:** {sdlc['key_phases']}")

with tabs[1]:
    st.header("Requirements Traceability & Approval")
    reqs = RequirementRepository.get_all_requirements()
    
    if reqs:
        df = pd.DataFrame(reqs)
        # Reorder columns for readability
        df = df[["id", "status", "priority", "risk_level", "statement", "compliance_mapping"]]
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Human-in-the-Loop (HITL) Action")
        col1, col2, col3 = st.columns(3)
        req_to_approve = col1.selectbox("Select Requirement ID", df["id"].tolist())
        new_status = col2.selectbox("New Status", ["Approved", "Rejected", "Modified"])
        
        if col3.button("Update Status"):
            RequirementRepository.update_status(req_to_approve, new_status, current_user, current_role)
            st.success(f"Status of {req_to_approve} updated to {new_status}!")
            st.rerun() # Refresh the UI
    else:
        st.info("No requirements generated yet.")

with tabs[2]:
    st.header("Security & Audit Logs")
    req_to_audit = st.text_input("Enter Requirement ID to view history (e.g., REQ-PAY-...):")
    if req_to_audit:
        logs = AuditRepository.get_logs_for_requirement(req_to_audit)
        if logs:
            st.table(logs)
        else:
            st.warning("No logs found for this ID.")