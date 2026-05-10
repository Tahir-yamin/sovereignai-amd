from typing import TypedDict, Annotated, List, Optional
from pydantic import BaseModel
from datetime import datetime
import operator

class PIIEntity(BaseModel):
    entity_type: str
    original_value: str
    token_replacement: str
    position_start: int
    position_end: int
    confidence: float

class ComplianceViolation(BaseModel):
    rule_id: str
    rule_name: str
    severity: str
    description: str
    recommendation: str

class AuditEntry(BaseModel):
    timestamp: datetime
    agent_name: str
    action: str
    input_hash: str
    output_hash: str
    tokens_used: int
    processing_time_ms: int
    gpu_memory_used_gb: float

class SovereignAIState(TypedDict):
    document_id: str
    original_filename: str
    raw_text: str
    document_hash: str
    sanitized_text: str
    pii_entities: List[PIIEntity]
    pii_count: int
    analysis_report: str
    key_findings: List[str]
    risk_summary: str
    document_type: str
    compliance_violations: List[ComplianceViolation]
    compliance_score: float
    compliance_framework: str
    audit_trail: Annotated[List[AuditEntry], operator.add]
    total_processing_time_ms: int
    bytes_sent_external: int
    current_agent: str
    errors: List[str]
    is_complete: bool
