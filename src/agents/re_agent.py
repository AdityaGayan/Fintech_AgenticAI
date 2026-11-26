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
    """Detect the financial domain from stakeholder text and retrieved policies."""
    combined = (text + " " + policies).lower()
    if any(word in combined for word in ["fraud", "suspicious", "aml", "anti-money", "anomaly"]):
        return "Fraud Detection"
    if any(word in combined for word in ["loan", "lending", "credit score", "mortgage", "borrower"]):
        return "Loan Origination"
    if any(word in combined for word in ["payment", "transaction", "checkout", "card", "pci", "gateway", "pay"]):
        return "Payment Processing"
    if any(word in combined for word in ["account", "balance", "deposit", "transfer", "banking", "customer"]):
        return "Digital Banking"
    return "FinTech"


def extract_requirements_from_input_and_rag(
    text: str,
    domain: str,
    retrieved_policies: str = "",
) -> List[dict]:
    """Provide a deterministic extraction result when the RE model is unavailable."""
    sentences = [sentence.strip() for sentence in re.split(r"[\n\.?!]+", text) if len(sentence.strip()) > 12]
    if not sentences:
        sentences = [text.strip() or f"The system must fulfill operational requirements for {domain}."]

    policy_text = retrieved_policies.lower()
    compliance = "Standard Financial Regulatory Guidelines"
    if "pci" in policy_text or "card" in policy_text:
        compliance = "PCI-DSS Req 8 (Access Control & Encryption)"
    elif "gdpr" in policy_text or "privacy" in policy_text:
        compliance = "GDPR Article 5 (Lawful & Transparent Processing)"
    elif "sox" in policy_text or "audit" in policy_text:
        compliance = "SOX Section 404 (Internal Financial Controls)"

    extracted = []
    prefix = domain.upper()[:3] if domain else "REQ"
    for sentence in sentences[:6]:
        lowered = sentence.lower()
        is_security = any(word in lowered for word in [
            "encrypt", "auth", "login", "password", "pci", "gdpr", "token", "privacy", "secure", "mask", "logout",
        ])
        is_performance = any(word in lowered for word in [
            "fast", "latency", "instant", "second", "response", "throughput", "scale",
        ])
        if is_security:
            category, priority, risk = "Security, Compliance", "Critical", "High"
            mapped_compliance = compliance if "PCI" in compliance else "PCI-DSS / GDPR Baseline"
        elif is_performance:
            category, priority, risk = "Technical, Performance", "High", "Medium"
            mapped_compliance = "Fintech SLA Guidelines"
        else:
            category, priority, risk = "Functional, Business", "Medium", "Low"
            mapped_compliance = compliance

        statement = sentence if sentence.endswith(".") else sentence + "."
        extracted.append({
            "id": f"REQ-{prefix}-{uuid.uuid4().hex[:4].upper()}",
            "domain": domain,
            "statement": statement,
            "category": category,
            "source": "Stakeholder Input",
            "business_justification": f"Core requirement derived from stakeholder specification and aligned with {mapped_compliance}.",
            "priority": priority,
            "compliance_mapping": mapped_compliance,
            "risk_level": risk,
            "confidence_score": 0.9 if is_security else 0.85,
            "status": "Pending Review",
        })
    return extracted


def process_requirements(
    text: str,
    domain: Optional[str] = None,
    retrieved_policies: str = "",
) -> List[dict]:
    """Extract, classify, and map stakeholder requirements for the SRS."""
    active_domain = domain or detect_domain_from_input(text, retrieved_policies)
    prompt = (
        "You are a master Financial Requirements Engineer. Analyze the stakeholder "
        "input strictly using the provided input and referenced policies.\n"
        f"Referenced Compliance Policies:\n{retrieved_policies or 'None'}\n\n"
        f"Stakeholder Input:\n{text}\n\n"
        "Extract distinct software requirements, classify them, detect ambiguities "
        "or conflicts, map security and privacy controls, and assess risk and priority."
    )
    result = invoke_gemini_safely(REAgentOutput, prompt)
    if result and result.requirements:
        formatted = []
        prefix = active_domain.upper()[:3] if active_domain else "REQ"
        for requirement in result.requirements:
            formatted.append({
                "id": f"REQ-{prefix}-{uuid.uuid4().hex[:4].upper()}",
                "domain": active_domain,
                "statement": requirement.statement,
                "category": ", ".join(requirement.category),
                "source": "Stakeholder Input",
                "business_justification": (
                    f"Risk: {requirement.risk_assessment} | "
                    f"Ambiguities: {', '.join(requirement.ambiguities_or_conflicts) or 'None'}"
                ),
                "priority": requirement.priority,
                "compliance_mapping": ", ".join(requirement.compliance_and_privacy)
                or "Standard Financial Regulatory Guidelines",
                "risk_level": "High" if "Critical" in requirement.priority else "Medium",
                "confidence_score": 0.9 if requirement.is_clear else 0.8,
                "status": "Pending Review",
            })
        return formatted
    return extract_requirements_from_input_and_rag(text, active_domain, retrieved_policies)
