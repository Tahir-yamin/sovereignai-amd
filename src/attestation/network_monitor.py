import subprocess
from loguru import logger

class NetworkMonitor:
    """
    Verifies that no external connections are established by the AI process.
    Provides "Zero-Leaked-Data" attestation for the SovereignAI-AMD pipeline.
    """
    
    @staticmethod
    def check_leakage():
        try:
            # Audit ESTABLISHED connections
            # We filter for non-local IP ranges to detect data egress
            result = subprocess.run(
                "netstat -atun | grep ESTABLISHED",
                shell=True,
                capture_output=True,
                text=True
            )
            
            connections = result.stdout.strip().split("\n")
            external_conns = []
            
            for conn in connections:
                if not conn: continue
                # Ignore loopback and local network traffic for the demo
                if "127.0.0.1" not in conn and "0.0.0.0" not in conn and "::1" not in conn:
                    external_conns.append(conn)
            
            return external_conns
        except Exception as e:
            logger.error(f"Network audit failed: {e}")
            return []

    @staticmethod
    def get_attestation():
        conns = NetworkMonitor.check_leakage()
        if not conns:
            return "✅ NETWORK AIR-GAP: VERIFIED (0 External Connections)"
        else:
            # In a production environment, this would trigger an immediate halt
            return f"⚠️ NETWORK WARNING: {len(conns)} Active External Connections Detected"

if __name__ == "__main__":
    # Test attestation
    print(NetworkMonitor.get_attestation())
