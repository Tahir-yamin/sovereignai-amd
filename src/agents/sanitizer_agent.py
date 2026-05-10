import re
from src.pipeline.state import SovereignAIState, PIIEntity
from src.models.model_manager import model_manager
from loguru import logger
from datetime import datetime

class SanitizerAgent:
    def __init__(self):
        logger.info("Initializing SanitizerAgent (PII Redaction)")
        self.patterns = {
            "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            "PHONE": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            "SSN": r"\d{3}-\d{2}-\d{4}",
            "CREDIT_CARD": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}"
        }

    def run(self, state: SovereignAIState) -> dict:
        text = state.get("raw_text", "")
        pii_entities = []
        sanitized_text = text

        # 1. Regex Layer
        for entity_type, pattern in self.patterns.items():
            matches = list(re.finditer(pattern, sanitized_text))
            for match in reversed(matches):
                original = match.group()
                replacement = f"[{entity_type}_{len(pii_entities)}]"
                
                pii_entities.append(PIIEntity(
                    entity_type=entity_type,
                    original_value=original,
                    token_replacement=replacement,
                    position_start=match.start(),
                    position_end=match.end(),
                    confidence=1.0
                ))
                
                sanitized_text = sanitized_text[:match.start()] + replacement + sanitized_text[match.end():]

        logger.info(f"SanitizerAgent found {len(pii_entities)} PII entities via regex.")

        # 2. TODO: Add LLM layer (Qwen 7B) for name/address detection
        
        return {
            "sanitized_text": sanitized_text,
            "pii_entities": pii_entities,
            "pii_count": len(pii_entities),
            "current_agent": "sanitizer"
        }
