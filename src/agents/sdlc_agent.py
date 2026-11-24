from typing import Literal
from pydantic import BaseModel, Field
from src.agents.base_agent import invoke_gemini_safely

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

def _score_sdlc_signals(text: str) -> dict:
    """
    Scores every SDLC model by counting how many signal words from the
    stakeholder input + RAG policies match each methodology's profile.
    Returns a dict of {model_name: score}.
    """
    t = text.lower()

    scores = {
        "Waterfall": 0,
        "V-Shaped": 0,
        "Incremental": 0,
        "Rapid Application Development": 0,
        "Prototyping": 0,
        "Spiral": 0,
        "Agile": 0,
    }

    # --- Waterfall signals: clear, complete, fixed, well-defined scope ---
    for kw in ["well-defined", "well defined", "clear", "fixed", "document",
               "specification", "complete", "defined", "finalized", "formal",
               "waterfall", "sequential", "linear", "plan-driven", "plan driven",
               "deadline", "budget", "contract", "regulatory", "mandate",
               "must comply", "log out", "logout", "timeout", "session",
               "inactivity", "within", "minutes", "seconds", "shall",
               "requirement", "policy", "standard", "process"]:
        if kw in t:
            scores["Waterfall"] += 1

    # --- V-Shaped signals: verification, validation, testing emphasis, compliance ---
    for kw in ["test", "verification", "validation", "v-model", "v-shaped",
               "acceptance", "quality", "qa", "verify", "validate",
               "pci", "gdpr", "sox", "hipaa", "compliance", "audit",
               "encrypt", "security", "access control", "mfa",
               "multi-factor", "authentication", "certified"]:
        if kw in t:
            scores["V-Shaped"] += 1

    # --- Incremental signals: phased, modular, staged delivery ---
    for kw in ["incremental", "phase", "staged", "module", "component",
               "release", "version", "iteration", "batch", "increment",
               "partial", "progressive"]:
        if kw in t:
            scores["Incremental"] += 1

    # --- RAD signals: rapid prototyping, quick delivery, user workshops ---
    for kw in ["rapid", "rad", "quick", "demo", "workshop", "reusable",
               "prototype quickly", "user design", "cutover"]:
        if kw in t:
            scores["Rapid Application Development"] += 1

    # --- Prototyping signals: poc, mockup, feasibility, throwaway ---
    for kw in ["prototype", "proof of concept", "poc", "mockup", "mock-up",
               "feasibility", "throwaway", "exploratory", "experiment",
               "concept", "try", "unclear", "unknown"]:
        if kw in t:
            scores["Prototyping"] += 1

    # --- Spiral signals: risk-driven, iterative risk, complex risk ---
    for kw in ["spiral", "risk", "risk-driven", "risk analysis", "mitigate",
               "fraud", "anomaly", "suspicious", "anti-money", "aml",
               "complex", "uncertainty", "uncertain", "evolving risk",
               "high risk", "critical risk", "vulnerability"]:
        if kw in t:
            scores["Spiral"] += 1

    # --- Agile signals: sprint, scrum, kanban, user story, backlog ---
    for kw in ["agile", "sprint", "scrum", "kanban", "user story",
               "backlog", "standup", "retrospective", "mvp",
               "user feedback", "iterative", "continuous delivery",
               "continuous improvement", "adapt to change", "flexible scope",
               "evolving requirements", "changing requirements", "frequent change"]:
        if kw in t:
            scores["Agile"] += 1

    return scores


# Justification and phases for each model (no hardcoded recommendation)
_MODEL_DETAILS = {
    "Waterfall": {
        "justification": (
            "The stakeholder requirements are well-defined with clear specifications, "
            "fixed scope, and regulatory constraints that benefit from a sequential, "
            "plan-driven development lifecycle with formal sign-offs at each stage."
        ),
        "key_phases": "Feasibility Study, Requirements Specification, System Design, Implementation, Integration & Testing, Deployment, Maintenance"
    },
    "V-Shaped": {
        "justification": (
            "The requirements demand rigorous verification and validation at each "
            "development phase, pairing every specification deliverable with formal "
            "acceptance and compliance testing criteria."
        ),
        "key_phases": "Requirements Analysis & Acceptance Testing, Architectural Design & System Testing, Detailed Design & Integration Testing, Implementation & Unit Testing"
    },
    "Incremental": {
        "justification": (
            "The project encompasses distinct functional modules that benefit from "
            "staged releases, allowing core capabilities to be validated in production "
            "early while enhancements are added progressively."
        ),
        "key_phases": "Core Architecture Specification, Incremental Build Planning, Phased Development & Testing, Progressive Integration"
    },
    "Rapid Application Development": {
        "justification": (
            "The requirements favour rapid iterative prototyping with active user "
            "feedback workshops and reusable software components to accelerate delivery."
        ),
        "key_phases": "Requirements Planning, User Design Workshop, Rapid Construction, Cutover & Deployment"
    },
    "Prototyping": {
        "justification": (
            "Key aspects of the system are exploratory or unclear, making early "
            "prototypes essential for validating feasibility and gathering concrete "
            "user feedback before committing to full-scale development."
        ),
        "key_phases": "Requirements Gathering, Rapid Prototype Construction, User Evaluation, Prototype Refinement, Final Implementation"
    },
    "Spiral": {
        "justification": (
            "The stakeholder input presents complex risk dynamics requiring iterative "
            "risk assessment, continuous prototype validation, and formal milestone "
            "reviews to systematically mitigate vulnerabilities before full release."
        ),
        "key_phases": "Risk Analysis & Planning, Prototype Engineering, Evaluation & Customer Review, Phased Deployment"
    },
    "Agile": {
        "justification": (
            "The requirements emphasize rapid delivery, evolving scope, and responsive "
            "adaptation through short iterative sprints with regular stakeholder "
            "feedback to continuously refine features."
        ),
        "key_phases": "Sprint Planning, Daily Standups, Iterative Development, Sprint Review & Retrospective"
    },
}


def derive_sdlc_from_input_and_rag(
    requirements_summary: str,
    retrieved_policies: str = "",
) -> dict:
    """
    Scores every SDLC model against the actual stakeholder input + RAG
    policies and picks the highest-scoring one.  No hardcoded default.
    """
    combined = requirements_summary + " " + retrieved_policies
    scores = _score_sdlc_signals(combined)

    best_model = max(scores, key=scores.get)
    best_score = scores[best_model]

    # Confidence scales with how dominant the winner is
    total = max(sum(scores.values()), 1)
    confidence = min(96, max(78, int(80 + (best_score / total) * 16)))

    details = _MODEL_DETAILS[best_model]
    return {
        "recommended_model": best_model,
        "confidence_percentage": confidence,
        "justification": details["justification"],
        "key_phases": details["key_phases"],
    }


def recommend_sdlc(
    requirements_summary: str = "",
    retrieved_policies: str = "",
) -> dict:
    """
    Recommends the optimal SDLC methodology.
    Uses the configured Gemini agent. The deterministic recommendation is used
    only when the AI call fails.
    """
    prompt = (
        "You are an expert Software Architect. Recommend an optimal SDLC "
        "methodology based ONLY on the stakeholder requirements and "
        "referenced policies below.\n"
        f"Stakeholder Requirements Summary:\n{requirements_summary}\n\n"
        f"Referenced Compliance Policies:\n{retrieved_policies or 'Standard Financial Policies'}\n\n"
        "Evaluate regulatory rigor, implementation risk, and feature "
        "complexity to choose the best model. "
        "Choose Agile only when the input explicitly describes changing or "
        "evolving requirements, sprints, Scrum, Kanban, a backlog, user "
        "stories, or continuous iterative delivery. Fixed regulatory scope "
        "should normally use Waterfall or V-Shaped; staged releases should "
        "use Incremental; significant uncertainty or risk should use Spiral. "
        "You MUST choose exactly one of these: Waterfall, V-Shaped, "
        "Incremental, Rapid Application Development, Prototyping, "
        "Spiral, Agile."
    )

    result = invoke_gemini_safely(SDLCRecommendation, prompt)
    if result:
        return {**result.model_dump(), "selection_source": "AI"}

    fallback = derive_sdlc_from_input_and_rag(
        requirements_summary=requirements_summary,
        retrieved_policies=retrieved_policies,
    )
    return {**fallback, "selection_source": "Fallback"}
