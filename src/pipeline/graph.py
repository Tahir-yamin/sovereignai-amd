from langgraph.graph import StateGraph, END
from loguru import logger
from src.pipeline.state import SovereignAIState
from src.agents.sanitizer_agent import SanitizerAgent
from src.agents.analyst_agent import AnalystAgent
from src.agents.compliance_agent import ComplianceAgent

def build_pipeline() -> StateGraph:
    sanitizer = SanitizerAgent()
    analyst = AnalystAgent()
    compliance = ComplianceAgent()

    workflow = StateGraph(SovereignAIState)
    workflow.add_node("sanitizer", sanitizer.run)
    workflow.add_node("analyst", analyst.run)
    workflow.add_node("compliance", compliance.run)

    workflow.set_entry_point("sanitizer")
    workflow.add_edge("sanitizer", "analyst")
    workflow.add_edge("analyst", "compliance")
    workflow.add_edge("compliance", END)

    return workflow.compile()

pipeline = build_pipeline()
