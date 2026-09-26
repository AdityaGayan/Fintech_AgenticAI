from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RequirementModel(BaseModel):
    id: str = Field(..., description="Unique Requirement Identifier (e.g., REQ-PAY-001)")
    domain: str = Field(..., description="Financial Domain (e.g., Payment Processing)")
    statement: str = Field(..., description="The finalized requirement text")
    category: str = Field(..., description="Comma-separated list of classifications")
    source: str = Field(..., description="Originating stakeholder or document")
    business_justification: str
    priority: str = Field(default="Medium", pattern="^(Low|Medium|High|Critical)$")
    compliance_mapping: str = Field(default="None")
    risk_level: str = Field(default="Medium", pattern="^(Low|Medium|High|Critical)$")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    status: str = Field(default="Pending Review", pattern="^(Pending Review|Approved|Rejected|Modified)$")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TraceabilityRecord(BaseModel):
    requirement_id: str
    source_document: str
    regulatory_framework: str
    control_id: str
    
class AuditLogModel(BaseModel):
    requirement_id: str
    action: str
    performed_by: str
    role: str
    previous_state: Optional[str] = None
    new_state: Optional[str] = None