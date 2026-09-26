from pydantic import BaseModel, Field
from src.agents.base_agent import get_llm

class SDLCRecommendation(BaseModel):
    recommended_model: str = Field(description="e.g., Agile, Waterfall, DevSecOps, V-Model, Spiral")
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
            f"Evaluate risk, compliance needs, and agility to pick the best model."
        )
        
        result = structured_llm.invoke(prompt)
        return result.model_dump()
    except Exception as e:
        return {"recommended_model": "DevSecOps", "confidence_percentage": 85, "justification": "Mock SDLC", "key_phases": "Design, Test"}