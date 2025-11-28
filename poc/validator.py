import json
import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from .mock_prnu import MockPRNU

@dataclass
class VerificationResult:
    """Encapsulates the result of a VTR validation attempt.

    Attributes:
        is_valid (bool): True if the container is valid, False otherwise.
        error_code (Optional[str]): A short string identifying the error type (e.g., "INVALID_PROOF").
        message (Optional[str]): A human-readable description of the result.
        details (Dict[str, Any]): Additional context or metadata about the validation.
    """
    is_valid: bool
    error_code: Optional[str] = None
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class VTRValidator:
    """Validates Video Truth Record (VTR) containers and sidecar files.

    This class performs integrity checks, schema validation, and cryptographic
    verification of the hardware signature against the video content.
    """

    def validate_container(self, video_path: str, sidecar_path: Optional[str] = None) -> VerificationResult:
        """Validates a video file against its VTR sidecar.

        Args:
            video_path (str): The path to the raw video file.
            sidecar_path (Optional[str]): The path to the .vtr.json sidecar file.
                If None, it defaults to <video_path>.vtr.json.

        Returns:
            VerificationResult: The outcome of the validation process.
        """
        # 1. Resolve Sidecar Path
        if sidecar_path is None:
            sidecar_path = f"{video_path}.vtr.json"

        # 2. Check File Existence
        if not os.path.exists(video_path):
            return VerificationResult(
                is_valid=False,
                error_code="VIDEO_NOT_FOUND",
                message=f"Video file not found at: {video_path}"
            )
        if not os.path.isfile(video_path):
            return VerificationResult(
                is_valid=False,
                error_code="VIDEO_NOT_FOUND",
                message=f"Video path is not a file: {video_path}"
            )
        if not os.path.exists(sidecar_path):
            return VerificationResult(
                is_valid=False,
                error_code="SIDECAR_NOT_FOUND",
                message=f"Sidecar file not found at: {sidecar_path}"
            )

        # 3. Load and Parse Sidecar
        try:
            with open(sidecar_path, 'r') as f:
                sidecar_data = json.load(f)
        except json.JSONDecodeError:
            return VerificationResult(
                is_valid=False,
                error_code="INVALID_JSON",
                message="Sidecar file contains invalid JSON."
            )
        except Exception as e:
            return VerificationResult(
                is_valid=False,
                error_code="READ_ERROR",
                message=f"Could not read sidecar: {str(e)}"
            )

        # 4. Schema Check (Basic)
        required_keys = ["vtr_version", "hardware_signature", "legal_assertions"]
        if not all(key in sidecar_data for key in required_keys):
             return VerificationResult(
                is_valid=False,
                error_code="INVALID_SCHEMA",
                message="Sidecar missing top-level keys."
            )

        hw_sig = sidecar_data.get("hardware_signature", {})
        required_sig_keys = ["public_key", "zk_proof", "timestamp", "liveness_flag"]
        if not all(key in hw_sig for key in required_sig_keys):
             return VerificationResult(
                is_valid=False,
                error_code="INVALID_SCHEMA",
                message="Hardware signature block missing required keys."
            )

        # 5. Cryptographic Verification
        # Extract data
        public_key = hw_sig["public_key"]
        zk_proof = hw_sig["zk_proof"]
        timestamp = hw_sig["timestamp"]
        # Extract optional Chain of Custody link
        previous_signature = hw_sig.get("previous_signature_link")

        # Verify using MockPRNU static method
        # This re-hashes the video content (via Merkle Tree) and checks if it matches the proof signed by the public key
        # We pass previous_signature to include it in the hash reconstruction if present
        is_signature_valid = MockPRNU.verify_zk_proof(
            public_key=public_key,
            video_path=video_path,
            timestamp=timestamp,
            zk_proof=zk_proof,
            previous_signature=previous_signature
        )

        if is_signature_valid:
            # Additional check: Verify the Merkle Root matches the one in sidecar if present
            # This is a secondary integrity check, although cryptographic signature is the primary one.
            sidecar_merkle_root = hw_sig.get("merkle_root")
            actual_merkle_root = MockPRNU._static_hash_video_content(video_path)

            if sidecar_merkle_root and sidecar_merkle_root != actual_merkle_root:
                return VerificationResult(
                    is_valid=False,
                    error_code="MERKLE_MISMATCH",
                    message="Sidecar Merkle Root does not match actual video Merkle Root.",
                    details={
                        "sidecar_root": sidecar_merkle_root,
                        "actual_root": actual_merkle_root
                    }
                )

            details = {
                    "vtr_version": sidecar_data["vtr_version"],
                    "timestamp": timestamp,
                    "liveness": hw_sig["liveness_flag"],
                    "merkle_root": actual_merkle_root
            }
            if previous_signature:
                details["chained_to_previous_proof"] = True
                details["previous_proof_hash"] = previous_signature

            return VerificationResult(
                is_valid=True,
                message="VTR container is valid.",
                details=details
            )
        else:
            return VerificationResult(
                is_valid=False,
                error_code="INVALID_SIGNATURE",
                message="Cryptographic proof verification failed. The content may have been modified or the sidecar does not match the video.",
                details={
                    "timestamp_claimed": timestamp
                }
            )
