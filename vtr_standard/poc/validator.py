# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import json
from pathlib import Path
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pydantic import ValidationError
from .mock_prnu import MockPRNU
from .schemas import VTRSidecar
from .config import VTRConfig

# Configure module-level logger
logger = logging.getLogger(__name__)

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

    def __init__(self, config: VTRConfig):
        """Initializes the VTRValidator.

        Args:
            config (VTRConfig): The VTR configuration object.
        """
        self.config = config

    def _read_and_validate_schema(self, sidecar_path: Path) -> tuple:
        """Reads and validates the sidecar schema.

        Returns:
            tuple: (VerificationResult, Optional[VTRSidecar])
        """
        if not sidecar_path.exists():
            return VerificationResult(
                is_valid=False,
                error_code="SIDECAR_NOT_FOUND",
                message=f"Sidecar file not found at: {sidecar_path}"
            ), None

        try:
            with open(sidecar_path, 'r') as f:
                raw_data = json.load(f)
            sidecar = VTRSidecar.model_validate(raw_data)
            return VerificationResult(is_valid=True), sidecar
        except json.JSONDecodeError:
            return VerificationResult(
                is_valid=False,
                error_code="INVALID_JSON",
                message="Sidecar file contains invalid JSON."
            ), None
        except ValidationError as e:
            sanitized_error = " | ".join(str(e).splitlines())
            logger.error(f"VTR Schema Validation Error: {sanitized_error}")
            return VerificationResult(
                is_valid=False,
                error_code="INVALID_SCHEMA",
                message="Sidecar file does not match the required VTR schema.",
                details={"validation_error_count": len(e.errors()) if hasattr(e, 'errors') else 1}
            ), None
        except Exception as e:
            logger.error("VTR Sidecar Read Error", exc_info=True)
            return VerificationResult(
                is_valid=False,
                error_code="READ_ERROR",
                message="An error occurred while reading or parsing the sidecar file.",
                details={}
            ), None

    def _verify_cryptography(self, video_path: str, actual_merkle_root: str, sidecar: VTRSidecar) -> VerificationResult:
        """Verifies the cryptographic signature of the sidecar against the actual merkle root."""
        hw_sig = sidecar.hardware_signature

        is_signature_valid = MockPRNU.verify_zk_proof(
            config=self.config,
            public_key=hw_sig.public_key,
            video_path=video_path,
            timestamp=hw_sig.timestamp,
            zk_proof=hw_sig.zk_proof,
            liveness_flag=hw_sig.liveness_flag,
            location_block_hash=hw_sig.location_block_hash,
            nonce=hw_sig.nonce,
            previous_signature=hw_sig.previous_signature_link,
            video_hash=actual_merkle_root
        )

        if is_signature_valid:
            sidecar_merkle_root = hw_sig.merkle_root

            if sidecar_merkle_root != actual_merkle_root:
                return VerificationResult(
                    is_valid=False,
                    error_code="MERKLE_MISMATCH",
                    message="Sidecar Merkle Root does not match actual video Merkle Root.",
                    details={
                        "sidecar_root": sidecar_merkle_root,
                        "merkle_root_claimed": sidecar_merkle_root,
                    }
                )

            if not hw_sig.liveness_flag:
                 return VerificationResult(
                    is_valid=False,
                    error_code="LIVENESS_FAILURE",
                    message="Hardware liveness check failed. This content is flagged as potentially synthetic.",
                    details={"liveness_flag": False}
                )

            details = {
                    "vtr_version": sidecar.vtr_version,
                    "timestamp": hw_sig.timestamp,
                    "liveness": hw_sig.liveness_flag,
                    "merkle_root": actual_merkle_root,
                    "zk_proof": hw_sig.zk_proof
            }
            if hw_sig.previous_signature_link:
                details["chained_to_previous_proof"] = True
                details["previous_proof_hash"] = hw_sig.previous_signature_link

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
                    "timestamp_claimed": hw_sig.timestamp,
                    "liveness_claimed": hw_sig.liveness_flag,
                    "location_hash_claimed": hw_sig.location_block_hash,
                    "merkle_root_claimed": hw_sig.merkle_root,
                    "nonce": hw_sig.nonce,
                    "public_key": hw_sig.public_key,
                    "previous_signature_link": hw_sig.previous_signature_link,
                    "proof_received": hw_sig.zk_proof,
                }
            )

    def validate_sidecar_only(self, sidecar_path: str) -> VerificationResult:
        """Validates a sidecar cryptographically without needing the raw video file.

        This is used for strict chain of custody verification, ensuring the previous
        sidecar in the chain is fully valid against its claimed Merkle root.
        """
        s_path = Path(sidecar_path).resolve()

        res, sidecar = self._read_and_validate_schema(s_path)
        if not res.is_valid:
            return res

        # For a sidecar-only validation (e.g., chain of custody link), we assume the video
        # is no longer available but we want to verify the sidecar's proof against the
        # Merkle root *it claims* to have. If the signature validates the claimed root,
        # the sidecar itself is mathematically consistent.
        claimed_root = sidecar.hardware_signature.merkle_root

        return self._verify_cryptography(
            video_path="", # Empty because we use the pre-calculated hash
            actual_merkle_root=claimed_root,
            sidecar=sidecar
        )
    def validate_container(self, video_path: str, sidecar_path: Optional[str] = None) -> VerificationResult:
        """Validates a video file against its VTR sidecar.

        Args:
            video_path (str): The path to the raw video file.
            sidecar_path (Optional[str]): The path to the .vtr.json sidecar file.
                If None, it defaults to <video_path>.vtr.json.

        Returns:
            VerificationResult: The outcome of the validation process.
        """
        # Resolve Video Path strictly to prevent path traversal
        v_path = Path(video_path).resolve()

        # 1. Resolve Sidecar Path
        if sidecar_path is None:
            s_path = Path(f"{v_path}.vtr.json")
        else:
            s_path = Path(sidecar_path).resolve()

        # 2. Check File Existence
        if not v_path.exists():
            return VerificationResult(
                is_valid=False,
                error_code="VIDEO_NOT_FOUND",
                message=f"Video file not found at: {video_path}"
            )
        if not v_path.is_file():
            return VerificationResult(
                is_valid=False,
                error_code="VIDEO_NOT_FOUND",
                message=f"Video path is not a file: {video_path}"
            )

        # 3. Load and Parse Sidecar
        schema_result, sidecar = self._read_and_validate_schema(s_path)
        if not schema_result.is_valid:
            return schema_result

        # 4. Cryptographic Verification
        actual_merkle_root = MockPRNU._static_hash_video_content(str(v_path))
        return self._verify_cryptography(str(v_path), actual_merkle_root, sidecar)
