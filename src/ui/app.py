import gradio as gr
import os
import uuid
import time
from src.pipeline.graph import pipeline
from src.document.parser import DocumentParser
from src.attestation.hardware_monitor import HardwareMonitor
from src.attestation.network_monitor import NetworkMonitor
from src.attestation.audit_logger import AuditLogger
from loguru import logger

# Initialize Audit Logger
audit_log = AuditLogger()

def process_document(file_obj):
    if not file_obj:
        return "Please upload a document.", "", 0, "N/A"
    
    # 1. Parse File
    text = DocumentParser.parse(file_obj.name)
    if not text:
        return "Failed to parse document text.", "", 0, "N/A"
    
    # 2. Run Pipeline (Lazy loads models on MI300X)
    initial_state = {
        "document_id": str(uuid.uuid4()),
        "original_filename": os.path.basename(file_obj.name),
        "raw_text": text,
        "pii_entities": [],
        "audit_trail": [],
        "errors": [],
        "is_complete": False
    }
    
    logger.info(f"🚀 Starting MI300X Pipeline for: {initial_state['original_filename']}")
    start_time = time.time()
    
    try:
        final_state = pipeline.invoke(initial_state)
        duration = round(time.time() - start_time, 2)
        logger.success(f"✅ Pipeline finished in {duration}s")
        
        # 3. Log to Cryptographic Audit Trail
        audit_log.log_decision(
            "Gradio_UI", 
            f"Processed {initial_state['original_filename']}", 
            f"Result: Score {final_state.get('compliance_score')} | PII Detected: {final_state.get('pii_count')}"
        )
        
        return (
            final_state.get("sanitized_text", ""),
            final_state.get("analysis_report", ""),
            final_state.get("compliance_score", 0),
            f"{duration} seconds"
        )
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return f"Error: {e}", "", 0, "N/A"

def get_telemetry():
    """Fetches live hardware and network state."""
    return HardwareMonitor.get_summary(), NetworkMonitor.get_attestation()

# Premium CSS for SovereignAI Aesthetic
custom_css = """
body { background-color: #0d0d0d; color: #e0e0e0; }
.gradio-container { border: 1px solid #333 !important; border-radius: 12px !important; }
#title { text-align: center; font-family: 'Inter', sans-serif; color: #ed1c24; margin-bottom: 0px; }
#subtitle { text-align: center; color: #888; margin-top: 0px; margin-bottom: 20px; }
.stat-box { background: rgba(237, 28, 36, 0.05); border: 1px solid #ed1c24 !important; border-radius: 8px !important; }
button.primary { background: #ed1c24 !important; border: none !important; }
"""

with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as demo:
    gr.Markdown("# 𝐒𝐨𝐯𝐞𝐫𝐞𝐢𝐠𝐧𝐀𝐈-𝐀𝐌𝐃", elem_id="title")
    gr.Markdown("### MI300X-Bound Private Intelligence & Attestation Dashboard", elem_id="subtitle")
    
    with gr.Row():
        with gr.Column(scale=1, variant="panel"):
            gr.Markdown("#### 🛡️ Hardware Attestation")
            hw_status = gr.Textbox(label="AMD MI300X Telemetry", value="Initializing...", interactive=False, elem_classes="stat-box")
            net_status = gr.Textbox(label="Network Privacy State", value="Verifying Air-Gap...", interactive=False, elem_classes="stat-box")
            
            # Auto-refresh telemetry every 5 seconds
            gr.Timer(5).tick(get_telemetry, outputs=[hw_status, net_status])
            
            gr.Markdown("---")
            gr.Markdown("#### 🏺 Session Integrity")
            audit_file = gr.File(label="Download SHA-256 Audit Ledger", value="logs/audit_trail.jsonl")
            
        with gr.Column(scale=3):
            with gr.Tabs():
                with gr.Tab("Document Processing"):
                    with gr.Row():
                        file_input = gr.File(label="Drop Medical/Legal Document (PDF, DOCX, TXT)")
                    
                    with gr.Row():
                        process_btn = gr.Button("🚀 Execute Sovereign Pipeline", variant="primary")
                    
                    with gr.Row():
                        with gr.Column():
                            sanitized_out = gr.Textbox(label="Step 1: Sanitized Text (PII Scrubbed)", lines=12)
                        with gr.Column():
                            report_out = gr.Textbox(label="Step 2: Qwen-72B Deep Analysis", lines=12)
                    
                    with gr.Row():
                        score_out = gr.Number(label="Step 3: Compliance Audit Score (0-100)")
                        timer_out = gr.Textbox(label="MI300X Compute Time")
                
                with gr.Tab("Pipeline Architecture"):
                    gr.Markdown("#### LangGraph Multi-Agent Flow")
                    gr.Markdown("1. **Sanitizer Agent (Qwen-7B)**: Regex + LLM PII Detection.")
                    gr.Markdown("2. **Analyst Agent (Qwen-72B)**: Deep Reasoning on HBM3.")
                    gr.Markdown("3. **Compliance Agent (Qwen-14B)**: Regulatory scoring.")

    process_btn.click(
        process_document, 
        inputs=[file_input], 
        outputs=[sanitized_out, report_out, score_out, timer_out]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
