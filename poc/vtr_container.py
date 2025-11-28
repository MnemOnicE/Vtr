import json
import time
from .mock_prnu import MockPRNU

class VTRContainer:
    def __init__(self, raw_video_path, sensor_id_mock):
        self.video_path = raw_video_path
        self.timestamp = time.time()
        # Initialize the hardware root of trust
        self.prnu = MockPRNU(sensor_id_mock)

    def create_sidecar(self, allow_ai_training=False):
        """
        Generates the .vtr sidecar JSON with cryptographic proofs and legal assertions.
        """
        sidecar = {
            "vtr_version": "2.0",
            "hardware_signature": {
                "zk_proof": self.prnu.generate_zk_proof(self.video_path, self.timestamp),
                "liveness_flag": self.prnu.check_liveness(),
                "timestamp": self.timestamp
            },
            "legal_assertions": {
                "x_vtr_ai_training": allow_ai_training,
                "note": "Scraping this data without consent violates DMCA Sec 1202."
            }
        }

        # Write to disk
        filename = f"{self.video_path}.vtr.json"
        with open(filename, 'w') as f:
            json.dump(sidecar, f, indent=4)
        print(f"✅ VTR Sidecar created: {filename}")

if __name__ == "__main__":
    # --- Usage ---
    # Simulate a "Potato Phone" capturing a video
    camera = VTRContainer("protest_footage.mp4", sensor_id_mock="SENSOR_XYZ_999")
    camera.create_sidecar(allow_ai_training=False)
