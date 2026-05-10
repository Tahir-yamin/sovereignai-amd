import os
from src.document.parser import DocumentParser
from src.pipeline.graph import pipeline
from src.models.model_manager import model_manager
from loguru import logger
import uuid

def run_file_test(file_path: str):
    logger.info(f"🚀 Testing Pipeline with file: {file_path}")
    
    # 1. Parse File
    text = DocumentParser.parse(file_path)
    if not text:
        logger.error("Failed to parse text from file.")
        return

    # 2. Models will lazy-load via agents in the pipeline
    
    # 3. Setup Initial State
    initial_state = {
        "document_id": str(uuid.uuid4()),
        "original_filename": os.path.basename(file_path),
        "raw_text": text,
        "pii_entities": [],
        "audit_trail": [],
        "errors": [],
        "is_complete": False
    }
    
    # 4. Run Pipeline
    logger.info("Executing LangGraph workflow...")
    final_state = pipeline.invoke(initial_state)
    
    logger.success("Pipeline Execution Complete!")
    print("\n" + "="*50)
    print(f"FILE: {file_path}")
    print("SANITIZED TEXT (PREVIEW):")
    print(final_state.get("sanitized_text", "N/A")[:500] + "...")
    print("\nANALYSIS REPORT SUMMARY:")
    print(final_state.get("analysis_report", "N/A")[:500] + "...")
    print("\nCOMPLIANCE SCORE:", final_state.get("compliance_score", "N/A"))
    print("="*50)

if __name__ == "__main__":
    # Test with the medical DOCX we just created
    run_file_test("sample_docs/medical_demo.docx")
