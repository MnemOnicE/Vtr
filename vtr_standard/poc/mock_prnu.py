# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import hashlib
import time
import random
import os
from .merkle import MerkleTree

class MockPRNU:
    """Simulates the Hardware Root of Trust and PRNU (Photo Response Non-Uniformity) logic.

    This is the canonical V2.0 implementation, merging real Merkle hashing
    with V2.0 schema mock functions (Liveness, Semantic Score, Location).
    """

    def __init__(self, sensor_id):
        """Initializes the MockPRNU instance."""
        self.sensor_id = sensor_id
        # Mock GPS Block used for location hashing.
        # Check env var for deterministic override: VTR_TEST_GPS
        self.gps_salt = os.environ.get("VTR_TEST_GPS", "34.0522,118.2437")

    def get_public_key(self):
        """Derives a simulated Public Verification Key from the sensor ID."""
        return hashlib.sha256(self.sensor_id.encode()).hexdigest()

    def _hash_video_content(self, video_path):
        """Calculates the Merkle Root of the video file content."""
        return MockPRNU._static_hash_video_content(video_path)

    def generate_zk_proof(self, video_path, timestamp, liveness_flag, location_block_hash, previous_signature=None):
        """Simulates generating a Zero-Knowledge Proof (ZKP) for V2.0.

        Binds the Verification Key, Merkle Root, Timestamp, Liveness, Location,
        and optional Chain-of-Custody link.
        """
        # 1. Calculate Hash of the actual Video Content (Merkle Root)
        video_hash = self._hash_video_content(video_path)

        # 2. Derive the Public Verification Key
        verification_key = self.get_public_key()

        # 3. Create the Proof (Signs Key + Timestamp + Video Hash + Liveness + Location + Previous Signature)
        # We cast liveness_flag (bool) to str explicitly for consistent hashing.
        data_to_sign = f"{verification_key}{timestamp}{video_hash}{str(liveness_flag)}{location_block_hash}"

        if previous_signature:
            data_to_sign += previous_signature

        proof_hash = hashlib.sha256(data_to_sign.encode()).hexdigest()
        # Match the prefix from the older standard poc logic for proof readability
        return f"zk_snark_{proof_hash[:16]}"

    def check_liveness(self):
        """Simulates the Passive Liveness / Anti-Matrix Check.

        Now supports deterministic control via VTR_TEST_LIVENESS env var.
        """
        env_liveness = os.environ.get("VTR_TEST_LIVENESS")
        if env_liveness is not None:
            # Accepts "true", "1", "pass" as True; anything else as False (if set)
            return env_liveness.lower() in ("true", "1", "pass")

        # Mock logic: Randomly pass for demo purposes
        liveness_score = random.uniform(0.8, 1.0)
        return liveness_score > 0.9

    def calculate_location_block_hash(self):
        """Calculates the hash of the location data (salted)."""
        return hashlib.sha256(self.gps_salt.encode()).hexdigest()

    def _calculate_semantic_score(self):
        """Simulates AI analysis of scene complexity for economic data."""
        env_score = os.environ.get("VTR_TEST_SEMANTIC_SCORE")
        if env_score is not None:
            try:
                return float(env_score)
            except ValueError:
                pass # Fallback to default if invalid
        return 88.4

    def get_economic_data(self):
        """Returns the fully mocked economic data block."""
        return {
            "semantic_score": self._calculate_semantic_score(),
            "device_tier": "Potato_Phone_Tier_1"
        }

    @staticmethod
    def _static_hash_video_content(video_path):
        """Static helper to hash video content using Merkle Tree."""
        return MerkleTree(video_path).get_root()

    @staticmethod
    def verify_zk_proof(public_key, video_path, timestamp, zk_proof, liveness_flag, location_block_hash, previous_signature=None):
        """Verifies a simulated Zero-Knowledge Proof.

        Now requires liveness_flag and location_block_hash to reconstruct the hash.
        """

        video_hash = MockPRNU._static_hash_video_content(video_path)

        # Must match the order in generate_zk_proof
        expected_data = f"{public_key}{timestamp}{video_hash}{str(liveness_flag)}{location_block_hash}"

        if previous_signature:
            expected_data += previous_signature

        expected_proof_hash = hashlib.sha256(expected_data.encode()).hexdigest()
        expected_proof = f"zk_snark_{expected_proof_hash[:16]}"

        return expected_proof == zk_proof
