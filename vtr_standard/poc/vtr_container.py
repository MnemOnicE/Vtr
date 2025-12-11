# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import json
import time
import os
from .mock_prnu import MockPRNU

class VTRContainer:
    """Manages the creation of Video Truth Record (VTR) containers.

    This is the canonical V2.0 generator. It handles the association of a raw video
    file with a hardware root of trust (via MockPRNU), generating a sidecar file
    containing cryptographic proofs and legal assertions.
    """

    def __init__(self, raw_video_path, sensor_id_mock):
        """Initializes the VTRContainer."""
        self.video_path = raw_video_path
        self.timestamp = time.time()
        # Initialize the hardware root of trust (the Merged MockPRNU)
        self.prnu = MockPRNU(sensor_id_mock)

    def create_sidecar(self, allow_ai_training=False, previous_sidecar_path=None):
        """Generates the .vtr sidecar JSON file.

        Args:
            allow_ai_training (bool, optional): A flag indicating whether the content
                may be used for AI training datasets. Defaults to False.
            previous_sidecar_path (str, optional): Path to the previous sidecar in the chain.

        Returns:
            None: This method writes the sidecar file to disk.
        """
        previous_signature = None
        if previous_sidecar_path:
            try:
                with open(previous_sidecar_path, 'r') as f:
                    prev_data = json.load(f)
                    # Extract the ZK Proof for the Chain of Custody link
                    previous_signature = prev_data.get("hardware_signature", {}).get("zk_proof")
                    if not previous_signature:
                        print(f"⚠️ Warning: Could not extract zk_proof from {previous_sidecar_path}")
            except Exception as e:
                print(f"⚠️ Warning: Failed to read previous sidecar: {e}")

        # --- 1. Hardware Signature Components ---
        zk_proof = self.prnu.generate_zk_proof(
            self.video_path,
            self.timestamp,
            previous_signature=previous_signature
        )

        hardware_signature = {
            "public_key": self.prnu.get_public_key(),
            "zk_proof": zk_proof,
            "liveness_flag": self.prnu.check_liveness(),
            "timestamp": self.timestamp,
            "merkle_root": self.prnu._hash_video_content(self.video_path),
            "location_block_hash": self.prnu.calculate_location_block_hash()
        }
        # Add Chain of Custody link if present
        if previous_signature:
            hardware_signature["previous_signature_link"] = previous_signature


        # --- 2. Construct Final Sidecar ---
        sidecar = {
            "vtr_version": "2.0",
            "hardware_signature": hardware_signature,
            "legal_assertions": {
                "x_vtr_ai_training": allow_ai_training,
                "copyright_notice": "Scraping this data without consent violates DMCA Sec 1202."
            },
            "economic_data": self.prnu.get_economic_data()
        }


        # Write to disk
        filename = f"{self.video_path}.vtr.json"
        with open(filename, 'w') as f:
            json.dump(sidecar, f, indent=4)

        print(f"✅ VTR Sidecar created: {filename}")
        print(f"🔒 AI Training Permission: {allow_ai_training}")

if __name__ == "__main__":
    print("--- OntoLogics VTR Generator v2.0 (Merged POC) ---")

    # Simulate a "Potato Phone" capturing a video (First Link in the Chain)
    camera_1 = VTRContainer("first_video.mp4", sensor_id_mock="SENSOR_PRNU_XYZ_999")
    camera_1.create_sidecar(allow_ai_training=True)

    # Simulate capturing a subsequent video (Second Link in the Chain)
    camera_2 = VTRContainer("second_video.mp4", sensor_id_mock="SENSOR_PRNU_XYZ_999")
    # Link to the first sidecar to create the Chain of Custody
    camera_2.create_sidecar(allow_ai_training=False, previous_sidecar_path="first_video.mp4.vtr.json")
