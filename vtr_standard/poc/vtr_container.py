# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import json
import time
import os
import logging
import uuid
from .mock_prnu import MockPRNU
from .schemas import VTRSidecar, HardwareSignature, LegalAssertions, VTR_VERSION
from .config import VTRConfig
from pathlib import Path
from .validator import VTRValidator

# Configure module-level logger
logger = logging.getLogger(__name__)

class VTRContainer:
    """Manages the creation of Video Truth Record (VTR) containers.

    This is the canonical V2.1 generator. It handles the association of a raw video
    file with a hardware root of trust (via MockPRNU), generating a sidecar file
    containing cryptographic proofs and legal assertions.
    """

    def __init__(self, raw_video_path, sensor_id_mock, config: VTRConfig):
        """Initializes the VTRContainer."""
        # STRICT PATH SANITIZATION
        self.video_path = str(Path(raw_video_path).resolve())
        self.timestamp = time.time()
        self.config = config
        # Initialize the hardware root of trust (the Merged MockPRNU)
        self.prnu = MockPRNU(sensor_id_mock, self.config)

    def create_sidecar(self, allow_ai_training=False, previous_sidecar_path=None, overwrite=False):
        """Generates the .vtr sidecar JSON file.

        Args:
            allow_ai_training (bool, optional): A flag indicating whether the content
                may be used for AI training datasets. Defaults to False.
            previous_sidecar_path (str, optional): Path to the previous sidecar in the chain.
            overwrite (bool, optional): If True, overwrites an existing sidecar file. Defaults to False.

        Returns:
            None: This method writes the sidecar file to disk.
        """
        filename = f"{self.video_path}.vtr.json"
        if not overwrite and os.path.exists(filename):
            raise FileExistsError(f"Sidecar file already exists: {filename}")

        previous_signature = None
        if previous_sidecar_path:
            # STRICT CHAIN OF CUSTODY CHECK
            # If a previous link is requested, it MUST be valid.
            validator = VTRValidator(self.config)
            res = validator.validate_sidecar_only(previous_sidecar_path)

            if not res.is_valid:
                raise ValueError(f"Chain of Custody Failure: Previous sidecar is invalid. {res.error_code}: {res.message}")

            # The schema validation passed, extract the proof directly from the result
            previous_signature = res.details.get("zk_proof")
            if not previous_signature:
                raise ValueError(f"Chain of Custody Failure: Could not extract zk_proof from valid sidecar.")

        # --- 1. Hardware Signature Components ---
        # Calculate liveness and location first to bind them in the proof
        liveness_flag = self.prnu.check_liveness()

        if not liveness_flag:
            logger.warning("⚠️  WARNING: Liveness check FAILED. The generated VTR will be cryptographically valid but flagged as 'Synthetic' by validators.")

        location_block_hash = self.prnu.calculate_location_block_hash()

        # Generate Nonce for Replay Protection
        nonce = uuid.uuid4().hex

        # Calculate Merkle Root once to optimize IO
        actual_merkle_root = self.prnu._hash_video_content(self.video_path)

        zk_proof = self.prnu.generate_zk_proof(
            self.video_path,
            self.timestamp,
            liveness_flag=liveness_flag,
            location_block_hash=location_block_hash,
            nonce=nonce,
            previous_signature=previous_signature,
            video_hash=actual_merkle_root
        )

        hardware_signature = HardwareSignature(
            public_key=self.prnu.get_public_key(),
            zk_proof=zk_proof,
            liveness_flag=liveness_flag,
            timestamp=self.timestamp,
            merkle_root=actual_merkle_root,
            location_block_hash=location_block_hash,
            previous_signature_link=previous_signature,
            nonce=nonce
        )

        # --- 2. Construct Final Sidecar ---
        legal_assertions = LegalAssertions(
            x_vtr_ai_training=allow_ai_training,
            copyright_notice="Scraping this data without consent violates DMCA Sec 1202."
        )

        sidecar = VTRSidecar(
            vtr_version=VTR_VERSION,
            hardware_signature=hardware_signature,
            legal_assertions=legal_assertions
        )

        # Write to disk
        with open(filename, 'w') as f:
            f.write(sidecar.model_dump_json(indent=4))

        logger.info(f"✅ VTR Sidecar created: {filename}")
        logger.info(f"🔒 AI Training Permission: {allow_ai_training}")

if __name__ == "__main__":
    import sys
    # DEMO MODE: Initialize config from environment
    config = VTRConfig.from_env()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(message)s')
    logger.info("--- OntoLogics VTR Generator v2.0 (Merged POC) ---")

    # DEMO MODE: Auto-generate dummy files if they don't exist
    def ensure_dummy_video(filename):
        if not os.path.exists(filename):
            logger.info(f"🎥 Generating dummy video file: {filename}")
            # Generate 1MB of random bytes to simulate video content
            with open(filename, 'wb') as f:
                f.write(os.urandom(1024 * 1024))

    ensure_dummy_video("first_video.mp4")
    ensure_dummy_video("second_video.mp4")

    # Simulate a "Potato Phone" capturing a video (First Link in the Chain)
    camera_1 = VTRContainer("first_video.mp4", "SENSOR_PRNU_XYZ_999", config)
    camera_1.create_sidecar(allow_ai_training=True)

    # Simulate capturing a subsequent video (Second Link in the Chain)
    camera_2 = VTRContainer("second_video.mp4", "SENSOR_PRNU_XYZ_999", config)
    # Link to the first sidecar to create the Chain of Custody
    camera_2.create_sidecar(allow_ai_training=False, previous_sidecar_path="first_video.mp4.vtr.json")