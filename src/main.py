import os
from src.pipeline.graph import pipeline
from src.models.model_manager import model_manager
from loguru import logger
import uuid

def run_demo():
    logger.info("Starting SovereignAI-AMD Demo Pipeline")
    
    # 1. Models will initialize on-demand via the model_manager
    
    # 2. Mock input document
    sample_text = """
    MEDICAL REPORT - CONFIDENTIAL
    Patient: John Doe (SSN: 123-45-6789)
    Email: john.doe@example.com
    Date: 2024-05-10
    
    Findings: The patient shows signs of acute MI. Recommend immediate cardiovascular intervention.
    """
    
    initial_state = {
        "document_id": str(uuid.uuid4()),
        "original_filename": "demo_medical_report.txt",
        "raw_text": sample_text,
        "pii_entities": [],
        "audit_trail": [],
        "errors": [],
        "is_complete": False
    }
    
    # 3. Run Pipeline
    logger.info("Executing LangGraph workflow...")
    final_state = pipeline.invoke(initial_state)
    
    logger.success("Pipeline Execution Complete!")
    print("\n" + "="*50)
    print("SANITIZED TEXT:")
    print(final_state["sanitized_text"])
    print("\nANALYSIS REPORT:")
    print(final_state["analysis_report"])
    print("\nCOMPLIANCE SCORE:", final_state["compliance_score"])
    print("="*50)

if __name__ == "__main__":
    run_demo()
