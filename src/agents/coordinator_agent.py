from src.rag.compliance_rag import retrieve_compliance_guidelines
from src.agents.re_agent import process_requirements
from src.agents.sdlc_agent import recommend_sdlc
from src.db.repository import RequirementRepository
from src.db.models import RequirementModel
from src.security.pii_masker import sanitize_input

def extract_requirements(raw_input: str):
    """Run the security, RAG, and requirements-extraction stages only."""
    # 1. Security Check (Mask PII)
    safe_text, detected_pii = sanitize_input(raw_input)
    
    # 2. Knowledge Base Retrieval (RAG)
    # Retrieved strictly from the stakeholder's input
    rag_results = retrieve_compliance_guidelines(query=safe_text, top_k=2)
    retrieved_policies = "\n".join([f"[{r['source']}] {r['content']}" for r in rag_results]) if rag_results else ""
    
    # 3. Super RE Agent (Extraction, Classification, Compliance, Risk)
    # Formats requirements considering strictly stakeholder input and RAG policies
    raw_reqs = process_requirements(text=safe_text, retrieved_policies=retrieved_policies)
    
    return {
        "masked_input": safe_text,
        "detected_pii": detected_pii,
        "rag_sources_used": [r["source"] for r in rag_results] if rag_results else [],
        "retrieved_policies": retrieved_policies,
        "requirements": raw_reqs,
    }


def save_requirements(requirements, user: str = "Stakeholder", role: str = "Analyst"):
    """Persist the final, possibly edited, requirements."""
    processed_reqs = []
    for req_dict in requirements:
        req_model = RequirementModel(**req_dict)
        RequirementRepository.save_requirement(req=req_model, user=user, role=role)
        processed_reqs.append(req_dict)
    return processed_reqs


def recommend_from_requirements(requirements, retrieved_policies: str = ""):
    """Ask the SDLC agent to recommend a model from the final requirements."""
    req_summary = ", ".join([r["statement"] for r in requirements])
    return recommend_sdlc(
        requirements_summary=req_summary,
        retrieved_policies=retrieved_policies,
    )


def run_full_pipeline(raw_input: str, user: str = "Stakeholder", role: str = "Analyst"):
    """Run the complete workflow for non-interactive callers."""
    extracted = extract_requirements(raw_input)
    processed_reqs = save_requirements(extracted["requirements"], user=user, role=role)

    sdlc_rec = recommend_from_requirements(processed_reqs, extracted["retrieved_policies"])

    return {
        "masked_input": extracted["masked_input"],
        "detected_pii": extracted["detected_pii"],
        "rag_sources_used": extracted["rag_sources_used"],
        "requirements": processed_reqs,
        "sdlc_recommendation": sdlc_rec
    }
