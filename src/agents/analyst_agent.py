from src.pipeline.state import SovereignAIState
from src.models.model_manager import model_manager
from loguru import logger

class AnalystAgent:
    def __init__(self):
        logger.info("Initializing AnalystAgent (Deep Analysis with Qwen 72B)")
        self.system_prompt = """You are a Sovereign AI Analyst. Your task is to perform a deep analysis of the provided document.
Extract key findings, summarize risks, and provide a comprehensive report.
Format your output as a clear, professional analysis."""

    def run(self, state: SovereignAIState) -> dict:
        logger.info(f"AnalystAgent processing document: {state.get('document_id', 'unknown')}")
        
        prompt = f"Analyze the following document and provide key findings and a risk summary:\n\n{state.get('sanitized_text', '')}"
        
        report = model_manager.generate("analyst", prompt, self.system_prompt)
        
        # Simple extraction logic for demo
        findings = [line.strip("- ") for line in report.split("\n") if line.strip().startswith("-")]
        
        return {
            "analysis_report": report,
            "key_findings": findings[:5],
            "current_agent": "analyst"
        }
