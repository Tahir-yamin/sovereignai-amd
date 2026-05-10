import subprocess
import json
from loguru import logger

class HardwareMonitor:
    """
    Interfaces with rocm-smi to provide live telemetry of the MI300X.
    Used for the Attestation Dashboard to prove local, hardware-bound execution.
    """
    
    @staticmethod
    def get_gpu_stats():
        try:
            # Execute rocm-smi with JSON output for robust parsing
            result = subprocess.run(
                ["rocm-smi", "--showgpuload", "--showmeminfo", "--json"],
                capture_output=True,
                text=True,
                check=True
            )
            stats = json.loads(result.stdout)
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch ROCm stats: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_summary():
        stats = HardwareMonitor.get_gpu_stats()
        if "error" in stats:
            return "AMD MI300X: OFFLINE (Check ROCm Drivers)"
            
        # SMI JSON structure usually keys by 'cardX' or 'deviceX'
        # We'll look for the first available card
        card_key = next((k for k in stats.keys() if 'card' in k or 'device' in k), None)
        
        if not card_key:
            return "AMD MI300X: Detected but no telemetry available."

        card_data = stats[card_key]
        load = card_data.get('GPU use (%)', 'N/A')
        mem_used = card_data.get('FB memory usage (MB)', 'N/A')
        
        return f"AMD MI300X Status | Load: {load}% | VRAM Used: {mem_used}MB"

if __name__ == "__main__":
    # Test output
    print(HardwareMonitor.get_summary())
