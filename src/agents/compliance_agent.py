from src.pipeline.state import SovereignAIState, ComplianceViolation
from src.models.model_manager import model_manager
from loguru import logger

class ComplianceAgent:
    def __init__(self):
        logger.info("Initializing ComplianceAgent (HIPAA/GDPR Checks)")
        self.system_prompt = """You are a Sovereign AI Compliance Officer. Your task is to audit the provided analysis for HIPAA, GDPR, and SOC2 compliance.
Identify any potential violations and provide recommendations for remediation.
Format your output as a list of violations and a final compliance score (0-100)."""

    def run(self, state: SovereignAIState) -> dict:
        logger.info(f"ComplianceAgent auditing document: {state.get('document_id', 'unknown')}")
        
        prompt = f"Audit the following document analysis for compliance:\n\n{state.get('analysis_report', '')}"
        
        audit_result = model_manager.generate("compliance", prompt, self.system_prompt)
        
        # Simple parsing for demo
        violations = []
        if "VIOLATION" in audit_result.upper():
            violations.append(ComplianceViolation(
                rule_id="RULE_001",
                rule_name="Data Sovereignty Check",
                severity="HIGH",
                description="Potential unmasked PII detected in summary.",
                recommendation="Re-run sanitizer with stricter name detection."
            ))

        return {
            "compliance_violations": violations,
            "compliance_score": 95.0 if not violations else 70.0,
            "current_agent": "compliance",
            "is_complete": True
        }
