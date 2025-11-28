import json
import time
import os
from .mock_prnu import MockPRNU

class VTRContainer:
    """Manages the creation of Video Truth Record (VTR) containers.

    This class handles the association of a raw video file with a hardware
    root of trust, generating a sidecar file containing cryptographic proofs
    and legal assertions.
    """

    def __init__(self, raw_video_path, sensor_id_mock):
        """Initializes the VTRContainer.

        Args:
            raw_video_path (str): The file path to the raw video content.
            sensor_id_mock (str): The unique identifier for the simulated hardware sensor.
        """
        self.video_path = raw_video_path
        self.timestamp = time.time()
        # Initialize the hardware root of trust
        self.prnu = MockPRNU(sensor_id_mock)

    def create_sidecar(self, allow_ai_training=False, previous_sidecar_path=None):
        """Generates the .vtr sidecar JSON file.

        This method creates a sidecar file that includes the VTR version,
        hardware signature (including a simulated Zero-Knowledge Proof and liveness flag),
        and legal assertions regarding AI training usage. The file is saved to disk
        with a `.vtr.json` extension appended to the original video filename.

        Args:
            allow_ai_training (bool, optional): A flag indicating whether the content
                may be used for AI training datasets. Defaults to False.
            previous_sidecar_path (str, optional): Path to the previous sidecar in the chain.

        Returns:
            None: This method writes the sidecar file to disk and does not return a value.
        """
        previous_signature = None
        if previous_sidecar_path:
            try:
                with open(previous_sidecar_path, 'r') as f:
                    prev_data = json.load(f)
                    previous_signature = prev_data.get("hardware_signature", {}).get("zk_proof")
                    if not previous_signature:
                        print(f"⚠️ Warning: Could not extract zk_proof from {previous_sidecar_path}")
            except Exception as e:
                print(f"⚠️ Warning: Failed to read previous sidecar: {e}")

        # Generate proof, linking to previous signature if available
        zk_proof = self.prnu.generate_zk_proof(
            self.video_path,
            self.timestamp,
            previous_signature=previous_signature
        )

        # Explicitly get the merkle root for transparency in the sidecar
        merkle_root = self.prnu._hash_video_content(self.video_path)

        sidecar = {
            "vtr_version": "2.0",
            "hardware_signature": {
                "public_key": self.prnu.get_public_key(),
                "zk_proof": zk_proof,
                "liveness_flag": self.prnu.check_liveness(),
                "timestamp": self.timestamp,
                "merkle_root": merkle_root
            },
            "legal_assertions": {
                "x_vtr_ai_training": allow_ai_training,
                "note": "Scraping this data without consent violates DMCA Sec 1202."
            }
        }

        # Include the link in the sidecar if it exists
        if previous_signature:
            sidecar["hardware_signature"]["previous_signature_link"] = previous_signature

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
