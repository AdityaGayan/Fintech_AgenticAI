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
    justification: str = Field(
        description=(
            "A clear five-mark justification covering stakeholder evidence, "
            "risk and regulatory fit, how the model addresses the needs, "
            "why alternatives are less suitable, and the expected outcome."
        )
    )


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
        "Write the justification as a strong five-mark academic answer in one coherent response. "
        "It must explicitly cover: (1) evidence from the stakeholder input, "
        "(2) regulatory, security, business-risk, or complexity considerations, "
        "(3) how the selected lifecycle manages those needs, "
        "(4) why the most plausible alternative models are less suitable, and "
        "(5) the expected project outcome. Use only facts supported by the input "
        "and policies; do not invent requirements. "
        "Do not return confidence, phases, or a workflow."
    )

    result = invoke_gemini_safely(SDLCRecommendation, prompt)
    if result is None:
        raise RuntimeError("The SDLC agent could not generate a model and justification.")

    return result.model_dump()
