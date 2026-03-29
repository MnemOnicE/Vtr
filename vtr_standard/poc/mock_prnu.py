# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import hashlib
import hmac
import os
import random
from typing import Optional

from .merkle import MerkleTree

class MockPRNU:
    """Simulates the Hardware Root of Trust and PRNU (Photo Response Non-Uniformity) logic.

    This is the canonical V2.0 implementation, merging real Merkle hashing
    with V2.2 schema mock functions (Liveness, Location).
    """

    def __init__(self, sensor_id):
        """Initializes the MockPRNU instance."""
        self.sensor_id = sensor_id

        # SECURITY PATCH: Fail if running in PRODUCTION mode
        if os.environ.get("VTR_ENV") == "PRODUCTION":
            raise RuntimeError(
                "CRITICAL SECURITY VIOLATION: MockPRNU loaded in PRODUCTION environment. "
                "This module is for testing only. Use RealPRNU interface."
            )

        # Mock GPS Block used for location hashing.
        # Check env var for deterministic override: VTR_TEST_GPS
        self.gps_salt = os.environ.get("VTR_TEST_GPS", "34.0522,118.2437")

        # Performance Optimization: Pre-calculate and cache static values
        # SECURITY FIX: Use PBKDF2-HMAC-SHA256 for robust key derivation instead of simple hashing.
        # Fixed domain-specific salt to ensure deterministic output for the same sensor/GPS while preventing rainbow tables.
        kdf_salt = b"vtr_kdf_salt_2025_canonical"
        iterations = 100000

        self._cached_public_key = hashlib.pbkdf2_hmac(
            "sha256",
            self.sensor_id.encode(),
            kdf_salt,
            iterations
        ).hex()

        self._cached_location_block_hash = hashlib.pbkdf2_hmac(
            "sha256",
            self.gps_salt.encode(),
            kdf_salt,
            iterations
        ).hex()

    def get_public_key(self):
        """Derives a simulated Public Verification Key from the sensor ID."""
        return self._cached_public_key

    def _hash_video_content(self, video_path):
        """Calculates the Merkle Root of the video file content."""
        return MockPRNU._static_hash_video_content(video_path)

    def generate_zk_proof(self, video_path, timestamp, liveness_flag, location_block_hash, nonce, previous_signature=None, video_hash=None):
        """Simulates generating a Zero-Knowledge Proof (ZKP) for V2.0.

        Binds the Verification Key, Merkle Root, Timestamp, Liveness, Location,
        Nonce (Replay Protection), and optional Chain-of-Custody link.

        Args:
            video_path (str): Path to the video file (used if video_hash is None).
            timestamp (float): The timestamp of capture.
            liveness_flag (bool): The liveness status.
            location_block_hash (str): The hash of the location block.
            nonce (str): The replay protection nonce.
            previous_signature (Optional[str]): The proof of the previous link.
            video_hash (Optional[str]): Pre-calculated Merkle Root. If provided, video_path is ignored for hashing.

        Returns:
            str: The simulated zk_proof string.
        """
        # 1. Calculate Hash of the actual Video Content (Merkle Root)
        if video_hash is None:
            video_hash = self._hash_video_content(video_path)

        # 2. Derive the Public Verification Key
        verification_key = self.get_public_key()

        # 3. Create the Proof
        return self.calculate_expected_proof(
            public_key=verification_key,
            video_hash=video_hash,
            timestamp=timestamp,
            liveness_flag=liveness_flag,
            location_block_hash=location_block_hash,
            nonce=nonce,
            previous_signature=previous_signature
        )

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
        return self._cached_location_block_hash

    @staticmethod
    def _static_hash_video_content(video_path):
        """Static helper to hash video content using Merkle Tree."""
        return MerkleTree(video_path).get_root()

    @staticmethod
    def calculate_expected_proof(public_key: str, video_hash: str, timestamp: float, liveness_flag: bool, location_block_hash: str, nonce: str, previous_signature: Optional[str] = None) -> str:
        """Calculates the expected zk_proof string based on the provided inputs.

        Args:
            public_key (str): The public verification key.
            video_hash (str): The Merkle Root of the video content.
            timestamp (float): The timestamp of capture.
            liveness_flag (bool): The liveness status.
            location_block_hash (str): The hash of the location block.
            nonce (str): The replay protection nonce.
            previous_signature (Optional[str]): The proof of the previous link.

        Returns:
            str: The expected zk_proof string.
        """
        # Optimization: Use "|".join() for faster concatenation.
        # We cast liveness_flag (bool) to lowercase string for consistent hashing.
        data_to_sign = "|".join([
            public_key,
            str(timestamp),
            video_hash,
            "true" if liveness_flag else "false",
            location_block_hash,
            nonce,
            previous_signature or ""
        ])

        proof_hash = hashlib.sha256(data_to_sign.encode()).hexdigest()
        return f"zk_snark_{proof_hash[:16]}"

    @staticmethod
    def verify_zk_proof(public_key, video_path, timestamp, zk_proof, liveness_flag, location_block_hash, nonce, previous_signature=None, video_hash=None):
        """Verifies a simulated Zero-Knowledge Proof.

        Now requires liveness_flag, location_block_hash, and nonce to reconstruct the hash.

        Args:
            public_key (str): The public verification key.
            video_path (str): Path to the video file (used if video_hash is None).
            timestamp (float): The timestamp of capture.
            zk_proof (str): The proof string to verify.
            liveness_flag (bool): The liveness status.
            location_block_hash (str): The hash of the location block.
            nonce (str): The replay protection nonce.
            previous_signature (Optional[str]): The proof of the previous link.
            video_hash (Optional[str]): Pre-calculated Merkle Root. If provided, video_path is ignored for hashing.

        Returns:
            bool: True if the proof is valid, False otherwise.
        """
        if video_hash is None:
            video_hash = MockPRNU._static_hash_video_content(video_path)

        expected_proof = MockPRNU.calculate_expected_proof(
            public_key=public_key,
            video_hash=video_hash,
            timestamp=timestamp,
            liveness_flag=liveness_flag,
            location_block_hash=location_block_hash,
            nonce=nonce,
            previous_signature=previous_signature
        )

        return hmac.compare_digest(expected_proof, zk_proof)
