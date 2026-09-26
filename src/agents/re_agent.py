import uuid
from typing import List, Optional
from pydantic import BaseModel, Field
from src.agents.base_agent import get_llm

class AnalyzedRequirement(BaseModel):
    statement: str = Field(description="The extracted formal requirement.")
    category: List[str] = Field(description="Categories: Business, Technical, Security, Compliance, etc.")
    is_clear: bool = Field(description="Is the requirement unambiguous and testable?")
    ambiguities_or_conflicts: List[str] = Field(description="List of vague terms or conflicts. Empty if clear.")
    compliance_and_privacy: List[str] = Field(description="Relevant regulations (e.g., GDPR, PCI-DSS).")
    risk_assessment: str = Field(description="Brief assessment of technical/business risks.")
    priority: str = Field(description="Low, Medium, High, Critical")

class REAgentOutput(BaseModel):
    requirements: List[AnalyzedRequirement]

def process_requirements(text: str, domain: str, retrieved_policies: str = "") -> List[dict]:
    """
    One-pass Super Agent: Extracts, classifies, checks compliance, and assesses risk.
    """
    llm = get_llm()
    
    try:
        structured_llm = llm.with_structured_output(REAgentOutput)
        
        prompt = (
            f"You are a master Financial Requirements Engineer. Analyze the stakeholder input for the '{domain}' domain.\n"
            f"1. Extract distinct software requirements.\n"
            f"2. Classify them.\n"
            f"3. Detect ambiguities or conflicts.\n"
            f"4. Map to security/privacy controls (Use provided policies if any: {retrieved_policies}).\n"
            f"5. Assess implementation risk.\n\n"
            f"Stakeholder Input:\n{text}"
        )
        
        result = structured_llm.invoke(prompt)
        
        # Map Pydantic output to our database dictionary structure
        formatted_reqs = []
        for r in result.requirements:
            formatted_reqs.append({
                "id": f"REQ-{domain.upper()[:3]}-{uuid.uuid4().hex[:4].upper()}",
                "domain": domain,
                "statement": r.statement,
                "category": ", ".join(r.category),
                "source": "Stakeholder Input",
                "business_justification": f"Risk: {r.risk_assessment} | Ambiguities: {', '.join(r.ambiguities_or_conflicts) or 'None'}",
                "priority": r.priority,
                "compliance_mapping": ", ".join(r.compliance_and_privacy),
                "risk_level": "High" if "Critical" in r.priority else "Medium", # Simplified logic
                "confidence_score": 0.9 if r.is_clear else 0.5,
                "status": "Pending Review"
            })
        return formatted_reqs
    except Exception as e:
        # We print the error so you can see if it's an API Key issue when testing
        print(f"\n[Agent Warning] LLM Call Failed, using fallback. Error: {e}")
        
        # This fallback now matches the exact schema the database and tests expect
        return [{
            "id": f"REQ-{domain.upper()[:3]}-TEST",
            "domain": domain,
            "statement": "Mock extracted requirement due to API error.",
            "category": "Functional",
            "source": "System Fallback",
            "business_justification": "Fallback justification",
            "priority": "Medium",
            "compliance_mapping": "None",
            "risk_level": "Low",
            "confidence_score": 0.5,
            "status": "Pending Review"
        }]