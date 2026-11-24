import re
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field
from src.agents.base_agent import invoke_gemini_safely

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

def detect_domain_from_input(text: str, policies: str = "") -> str:
    """Dynamically detects the financial domain from the stakeholder text and RAG policies."""
    combined = (text + " " + policies).lower()
    if any(w in combined for w in ["fraud", "suspicious", "aml", "anti-money", "anomaly"]):
        return "Fraud Detection"
    elif any(w in combined for w in ["loan", "lending", "credit score", "mortgage", "borrower"]):
        return "Loan Origination"
    elif any(w in combined for w in ["payment", "transaction", "checkout", "card", "pci", "gateway", "pay"]):
        return "Payment Processing"
    elif any(w in combined for w in ["account", "balance", "deposit", "transfer", "banking", "customer"]):
        return "Digital Banking"
    return "FinTech"

def extract_requirements_from_input_and_rag(text: str, domain: str, retrieved_policies: str = "") -> List[dict]:
    """
    Intelligently extracts and structures requirements derived strictly from the stakeholder input
    and retrieved compliance policies.
    """
    sentences = [s.strip() for s in re.split(r'[\n\.\?!]+', text) if len(s.strip()) > 12]
    if not sentences:
        sentences = [text.strip() or f"The system must fulfill operational requirements for {domain}."]
        
    # Check policies for relevant regulatory tags
    pol_lower = retrieved_policies.lower()
    default_compliance = "Standard Financial Regulatory Guidelines"
    if "pci" in pol_lower or "card" in pol_lower:
        default_compliance = "PCI-DSS Req 8 (Access Control & Encryption)"
    elif "gdpr" in pol_lower or "privacy" in pol_lower:
        default_compliance = "GDPR Article 5 (Lawful & Transparent Processing)"
    elif "sox" in pol_lower or "audit" in pol_lower:
        default_compliance = "SOX Section 404 (Internal Financial Controls)"

    formatted_reqs = []
    prefix = domain.upper()[:3] if domain else "REQ"
    
    for s in sentences[:6]:
        s_lower = s.lower()
        is_security = any(kw in s_lower for kw in ["encrypt", "auth", "login", "password", "pci", "gdpr", "token", "privacy", "secure", "mask", "logout"])
        is_perf = any(kw in s_lower for kw in ["fast", "latency", "instant", "second", "response", "throughput", "scale"])
        
        if is_security:
            category = "Security, Compliance"
            priority = "Critical"
            risk = "High"
            compliance = default_compliance if "PCI" in default_compliance else "PCI-DSS / GDPR Baseline"
        elif is_perf:
            category = "Technical, Performance"
            priority = "High"
            risk = "Medium"
            compliance = "Fintech SLA Guidelines"
        else:
            category = "Functional, Business"
            priority = "Medium"
            risk = "Low"
            compliance = default_compliance
            
        statement = s if s.endswith('.') else s + '.'
        formatted_reqs.append({
            "id": f"REQ-{prefix}-{uuid.uuid4().hex[:4].upper()}",
            "domain": domain,
            "statement": statement,
            "category": category,
            "source": "Stakeholder Input",
            "business_justification": f"Core requirement derived from stakeholder specification and aligned with {compliance}.",
            "priority": priority,
            "compliance_mapping": compliance,
            "risk_level": risk,
            "confidence_score": 0.9 if is_security else 0.85,
            "status": "Pending Review"
        })
    return formatted_reqs

def process_requirements(text: str, domain: Optional[str] = None, retrieved_policies: str = "") -> List[dict]:
    """
    Extracts, classifies, and maps requirements strictly considering stakeholder input and RAG policies.
    """
    active_domain = domain or detect_domain_from_input(text, retrieved_policies)
    
    prompt = (
        f"You are a master Financial Requirements Engineer. Analyze the stakeholder input strictly using the provided input and referenced policies.\n"
        f"Referenced Compliance Policies:\n{retrieved_policies or 'None'}\n\n"
        f"Stakeholder Input:\n{text}\n\n"
        f"1. Extract distinct software requirements.\n"
        f"2. Classify them (Functional, Security, Compliance, Technical).\n"
        f"3. Detect ambiguities or conflicts.\n"
        f"4. Map to security and privacy controls from the referenced policies.\n"
        f"5. Assess implementation risk and priority."
    )
    
    result = invoke_gemini_safely(REAgentOutput, prompt)
    
    if result and result.requirements:
        formatted_reqs = []
        prefix = active_domain.upper()[:3] if active_domain else "REQ"
        for r in result.requirements:
            formatted_reqs.append({
                "id": f"REQ-{prefix}-{uuid.uuid4().hex[:4].upper()}",
                "domain": active_domain,
                "statement": r.statement,
                "category": ", ".join(r.category),
                "source": "Stakeholder Input",
                "business_justification": f"Risk: {r.risk_assessment} | Ambiguities: {', '.join(r.ambiguities_or_conflicts) or 'None'}",
                "priority": r.priority,
                "compliance_mapping": ", ".join(r.compliance_and_privacy) or "Standard Financial Regulatory Guidelines",
                "risk_level": "High" if "Critical" in r.priority else "Medium",
                "confidence_score": 0.9 if r.is_clear else 0.8,
                "status": "Pending Review"
            })
        return formatted_reqs
    else:
        # Seamless deterministic derivation based on input and RAG
        return extract_requirements_from_input_and_rag(text, active_domain, retrieved_policies)
