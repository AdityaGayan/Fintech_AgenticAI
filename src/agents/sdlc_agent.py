from pydantic import BaseModel, Field
from typing import Literal
from src.agents.base_agent import get_llm

# 1. We force the AI to ONLY pick from this exact list
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

def recommend_sdlc(domain: str, requirements_summary: str, change_frequency: str) -> dict:
    """Recommends an SDLC methodology based on project profile."""
    llm = get_llm()
    
    try:
        structured_llm = llm.with_structured_output(SDLCRecommendation)
        prompt = (
            f"Recommend an SDLC for a {domain} financial project.\n"
            f"Expected change frequency: {change_frequency}\n"
            f"Requirements Profile: {requirements_summary}\n\n"
            f"Evaluate risk, compliance needs, and agility to pick the best model. "
            f"You MUST choose exactly one of these: Waterfall, V-Shaped, Incremental, Rapid Application Development, Prototyping, Spiral, Agile."
        )
        
        result = structured_llm.invoke(prompt)
        return result.model_dump()
    except Exception as e:
        print(f"\n[SDLC Agent Warning] API Failed: {e}")
        return {
            "recommended_model": "Agile", 
            "confidence_percentage": 80, 
            "justification": "Mock SDLC due to API key error. Please check your .env file.", 
            "key_phases": "Design, Develop, Test"
        }