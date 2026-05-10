import hashlib
import json
import time
from datetime import datetime
from loguru import logger

class AuditLogger:
    """
    Creates a tamper-evident audit trail of AI decisions.
    Each log entry contains a hash of the previous entry, ensuring integrity.
    Used for the Attestation Dashboard to provide "Proof of Reasoning".
    """
    
    def __init__(self, log_file="logs/audit_trail.jsonl"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        self.last_hash = self._get_last_hash()
        
    def _get_last_hash(self):
        if not os.path.exists(self.log_file):
            return "0" * 64 # Genesis state
            
        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()
                if not lines:
                    return "0" * 64
                last_entry = json.loads(lines[-1])
                return last_entry.get("hash", "0" * 64)
        except Exception:
            return "0" * 64

    def log_decision(self, agent_name: str, input_summary: str, decision: str):
        timestamp = datetime.now().isoformat()
        
        # We hash the input summary to protect PII while still proving what was processed
        input_hash = hashlib.sha256(input_summary.encode()).hexdigest()
        
        entry = {
            "timestamp": timestamp,
            "agent": agent_name,
            "input_hash": input_hash,
            "decision": decision,
            "prev_hash": self.last_hash
        }
        
        # Create high-fidelity hash of the current entry
        entry_json = json.dumps(entry, sort_keys=True)
        current_hash = hashlib.sha256(entry_json.encode()).hexdigest()
        entry["hash"] = current_hash
        
        # Write to append-only JSONL file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        self.last_hash = current_hash
        logger.info(f"Audit log entry created for {agent_name} | Hash: {current_hash[:10]}")
        return current_hash

if __name__ == "__main__":
    import os
    logger_inst = AuditLogger()
    logger_inst.log_decision("System", "Initial Pipeline Boot", "MI300X Hardware Verified")
