from src.rag.compliance_rag import retrieve_compliance_guidelines
from src.agents.re_agent import process_requirements
from src.agents.sdlc_agent import recommend_sdlc
from src.db.repository import RequirementRepository
from src.db.models import RequirementModel
from src.security.pii_masker import sanitize_input

def run_full_pipeline(raw_input: str, domain: str, change_frequency: str, user: str, role: str):
    """Orchestrates the entire Agentic AI workflow."""
    
    # 1. Security Check (Mask PII)
    safe_text, detected_pii = sanitize_input(raw_input)
    
    # 2. Knowledge Base Retrieval (RAG)
    # We retrieve policies based on the domain and the input text
    rag_results = retrieve_compliance_guidelines(query=f"{domain} {safe_text}", top_k=2)
    retrieved_policies = "\n".join([f"[{r['source']}] {r['content']}" for r in rag_results])
    
    # 3. Super RE Agent (Extraction, Classification, Compliance, Risk)
    raw_reqs = process_requirements(text=safe_text, domain=domain, retrieved_policies=retrieved_policies)
    
    # 4. Save to Database
    processed_reqs = []
    for req_dict in raw_reqs:
        req_model = RequirementModel(**req_dict)
        RequirementRepository.save_requirement(req=req_model, user=user, role=role)
        processed_reqs.append(req_dict)

    # 5. SDLC Agent Recommendation
    req_summary = ", ".join([r["statement"] for r in raw_reqs])
    sdlc_rec = recommend_sdlc(domain=domain, requirements_summary=req_summary, change_frequency=change_frequency)

    return {
        "masked_input": safe_text,
        "detected_pii": detected_pii,
        "rag_sources_used": [r["source"] for r in rag_results],
        "requirements": processed_reqs,
        "sdlc_recommendation": sdlc_rec
    }