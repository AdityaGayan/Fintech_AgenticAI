from concurrent.futures import ThreadPoolExecutor

from src.rag.compliance_rag import retrieve_compliance_guidelines
from src.agents.re_agent import process_requirements
from src.agents.srs_agent import generate_srs_document
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
    """Compatibility wrapper for selecting a model from requirement statements."""
    req_summary = ", ".join([r["statement"] for r in requirements])
    return recommend_sdlc(
        requirements_summary=req_summary,
        retrieved_policies=retrieved_policies,
    )


def generate_srs_from_input(raw_input: str):
    """Generate the SRS and SDLC model together from the stakeholder input."""
    safe_text, detected_pii = sanitize_input(raw_input)
    rag_results = retrieve_compliance_guidelines(query=safe_text, top_k=2)
    retrieved_policies = "\n".join(
        f"[{r['source']}] {r['content']}" for r in rag_results
    ) if rag_results else ""
    extracted_requirements = process_requirements(
        text=safe_text,
        retrieved_policies=retrieved_policies,
    )
    with ThreadPoolExecutor(max_workers=2) as executor:
        srs_future = executor.submit(
            generate_srs_document,
            stakeholder_context=safe_text,
            retrieved_policies=retrieved_policies,
            requirements=extracted_requirements,
        )
        sdlc_future = executor.submit(
            recommend_sdlc,
            requirements_summary=safe_text,
            retrieved_policies=retrieved_policies,
        )
        srs_document = srs_future.result()
        try:
            sdlc_recommendation = sdlc_future.result()
        except RuntimeError:
            # Gemini structured-output requests can occasionally collide when
            # submitted together. Retry the same AI call sequentially; this is
            # not a deterministic recommendation fallback.
            sdlc_recommendation = recommend_sdlc(
                requirements_summary=safe_text,
                retrieved_policies=retrieved_policies,
            )
    return {
        "masked_input": safe_text,
        "detected_pii": detected_pii,
        "rag_sources_used": [r["source"] for r in rag_results] if rag_results else [],
        "retrieved_policies": retrieved_policies,
        "requirements": extracted_requirements,
        "srs_document": srs_document,
        "sdlc_recommendation": sdlc_recommendation,
    }


def recommend_from_srs(srs_document: dict, retrieved_policies: str = ""):
    """Compatibility wrapper for selecting a model from an SRS."""
    return recommend_sdlc(
        requirements_summary=srs_document["markdown"],
        retrieved_policies=retrieved_policies,
    )


def generate_srs_from_requirements(
    requirements,
    stakeholder_context: str = "",
    retrieved_policies: str = "",
):
    """Ask the SRS agent to generate an IEEE-style SRS from extracted requirements."""
    return generate_srs_document(
        requirements=requirements,
        stakeholder_context=stakeholder_context,
        retrieved_policies=retrieved_policies,
    )


def run_full_pipeline(raw_input: str, user: str = "Stakeholder", role: str = "Analyst"):
    """Run the SRS-first workflow for non-interactive callers."""
    prepared = generate_srs_from_input(raw_input)

    return {
        "masked_input": prepared["masked_input"],
        "detected_pii": prepared["detected_pii"],
        "rag_sources_used": prepared["rag_sources_used"],
        "sdlc_recommendation": prepared["sdlc_recommendation"],
        "srs_document": prepared["srs_document"],
    }
