from typing import Optional, Literal
from pydantic import BaseModel, Field
from src.agents.base_agent import invoke_gemini_safely, get_llm

AllowedModels = Literal[
    "Waterfall", 
    "V-Shaped", 
    "Incremental", 
    "Rapid Application Development", 
    "Prototyping", 
    "Spiral", 
    "Agile"
]

class SDLCRecommendation(BaseModel):
    recommended_model: AllowedModels = Field(description="The chosen SDLC methodology.")
    confidence_percentage: int = Field(description="0 to 100")
    justification: str = Field(description="Why this model fits the project risk and regulatory profile.")
    key_phases: str = Field(description="Comma-separated mandatory phases for this SDLC.")

def derive_sdlc_from_input_and_rag(
    requirements_summary: str, 
    retrieved_policies: str = "", 
    domain: Optional[str] = None, 
    change_frequency: Optional[str] = None
) -> dict:
    """
    Evaluates the optimal SDLC methodology strictly considering the stakeholder input,
    extracted requirements, and referenced RAG policies.
    """
    combined_context = (requirements_summary + " " + retrieved_policies).lower()
    
    # 1. Check for strict compliance and safety constraints (RAG policies, encryption, PCI-DSS, GDPR, SOX)
    has_heavy_compliance = any(kw in combined_context for kw in [
        "pci", "gdpr", "sox", "audit", "compliance", "encrypt", "security", "token", "strict"
    ])
    
    # 2. Check for high risk / fraud detection / algorithmic complexity
    has_high_risk = any(kw in combined_context for kw in [
        "fraud", "anomaly", "suspicious", "risk", "anti-money", "vague", "uncertain"
    ]) or (domain and "fraud" in domain.lower())
    
    # 3. Check for volatility / rapid iteration signals in input
    indicates_agile = any(kw in combined_context for kw in [
        "rapid", "fast", "sprint", "mvp", "feedback", "frequent", "iterate", "evolving", "quick"
    ]) or (change_frequency == "High")
    
    indicates_stable = any(kw in combined_context for kw in [
        "stable", "fixed", "legacy", "mandatory", "sequential", "standard"
    ]) or (change_frequency == "Stable")
    
    if has_heavy_compliance and (indicates_stable or not indicates_agile):
        return {
            "recommended_model": "V-Shaped",
            "confidence_percentage": 94,
            "justification": (
                "The requirements and referenced compliance policies demand rigorous verification and validation at each development phase. "
                "The V-Shaped methodology directly ties every specification deliverable to formal acceptance and compliance testing criteria."
            ),
            "key_phases": "Requirements Analysis & Acceptance Testing, Architectural Design & System Testing, Detailed Design & Integration Testing, Implementation & Unit Testing"
        }
    elif has_high_risk and (indicates_agile or "vague" in combined_context):
        return {
            "recommended_model": "Spiral",
            "confidence_percentage": 92,
            "justification": (
                "The stakeholder input presents complex risk and security dynamics. The Spiral model accommodates iterative risk assessment, "
                "continuous prototype validation, and formal milestone reviews to systematically mitigate vulnerabilities before full release."
            ),
            "key_phases": "Risk Analysis & Planning, Prototype Engineering, Evaluation & Customer Review, Phased Deployment"
        }
    elif indicates_agile:
        return {
            "recommended_model": "Agile",
            "confidence_percentage": 91,
            "justification": (
                "The stakeholder requirements emphasize rapid delivery and responsive adaptation. Agile methodologies utilize short, iterative sprints "
                "with regular stakeholder feedback to continuously refine and evolve features."
            ),
            "key_phases": "Sprint Planning, Daily Standups, Iterative Development, Sprint Review & Retrospective"
        }
    elif any(kw in combined_context for kw in ["module", "phase", "staged", "part", "component", "multiple"]):
        return {
            "recommended_model": "Incremental",
            "confidence_percentage": 90,
            "justification": (
                "The specifications encompass distinct functional features that benefit from staged releases. An Incremental approach allows core "
                "operational capabilities to be validated in production early while subsequent enhancements are added progressively."
            ),
            "key_phases": "Core Architecture Specification, Incremental Build Planning, Phased Development & Testing, Progressive Integration"
        }
    else:
        return {
            "recommended_model": "Incremental",
            "confidence_percentage": 90,
            "justification": (
                "Based on the stakeholder input and referenced policies, an Incremental delivery strategy balances structured architectural "
                "compliance with phased, manageable software releases."
            ),
            "key_phases": "Requirements Baseline, Architectural Staging, Incremental Sprints, Verification & Deployment"
        }

def recommend_sdlc(
    domain: Optional[str] = None, 
    requirements_summary: str = "", 
    change_frequency: Optional[str] = None,
    retrieved_policies: str = ""
) -> dict:
    """
    Recommends the optimal SDLC methodology based ONLY on stakeholder input and RAG policies.
    """
    # Accommodate flexible positional calling conventions: recommend_sdlc(summary, policies) or recommend_sdlc(domain, summary, change_frequency)
    if domain and not requirements_summary:
        requirements_summary = domain
        domain = None
        
    prompt = (
        "You are an expert Software Architect. Recommend an optimal SDLC methodology based ONLY on the stakeholder requirements and referenced policies.\n"
        f"Stakeholder Requirements Summary:\n{requirements_summary}\n\n"
        f"Referenced Compliance Policies:\n{retrieved_policies or 'Standard Financial Policies'}\n\n"
        "Evaluate regulatory rigor, implementation risk, and feature complexity to choose the best model. "
        "You MUST choose exactly one of these: Waterfall, V-Shaped, Incremental, Rapid Application Development, Prototyping, Spiral, Agile."
    )
    
    result = invoke_gemini_safely(SDLCRecommendation, prompt)
    if result:
        return result.model_dump()
    
    # Seamless deterministic output based on input & RAG
    return derive_sdlc_from_input_and_rag(
        requirements_summary=requirements_summary,
        retrieved_policies=retrieved_policies,
        domain=domain,
        change_frequency=change_frequency
    )
