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
    justification: str = Field(description="Why this model fits the stakeholder input and regulatory profile.")


def recommend_sdlc(
    requirements_summary: str = "",
    retrieved_policies: str = "",
) -> dict:
    """
    Recommends the optimal SDLC methodology.
    Uses the configured Gemini agent to select the model. There is intentionally
    no local SDLC fallback.
    """
    prompt = (
        "You are an expert Software Architect. Recommend an optimal SDLC "
        "methodology based directly on the stakeholder input and "
        "referenced policies below.\n"
        f"Stakeholder Input:\n{requirements_summary}\n\n"
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
        "Spiral, Agile. Return only the selected model and a specific justification. "
        "Do not return confidence, phases, or a workflow."
    )

    result = invoke_gemini_safely(SDLCRecommendation, prompt)
    if result is None:
        raise RuntimeError("The SDLC agent could not generate a model and justification.")

    return result.model_dump()
