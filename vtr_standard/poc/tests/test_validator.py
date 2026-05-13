# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import os
import sys
import json
import unittest
from unittest.mock import MagicMock

# VTR-STANDUP: Fallback Mock for restricted environments where pydantic is missing.
try:
    import pydantic
except ImportError:
    class MockBaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    setattr(self, k, MockBaseModel(**v))
                else:
                    setattr(self, k, v)
        @classmethod
        def model_validate(cls, data):
            return cls(**data)
        def model_dump_json(self, **kwargs):
            import json
            def default(obj):
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                return str(obj)
            return json.dumps(self.__dict__, default=default)

    mock_pydantic = MagicMock()
    mock_pydantic.BaseModel = MockBaseModel
    mock_pydantic.Field = MagicMock(return_value=None)
    mock_pydantic.ValidationError = type("ValidationError", (Exception,), {})
    sys.modules["pydantic"] = mock_pydantic

from vtr_standard.poc.validator import VTRValidator, ValidationError
from vtr_standard.poc.config import VTRConfig

class TestValidator(unittest.TestCase):
    def setUp(self):
        os.environ["VTR_KDF_SALT"] = "test_validator_salt"
        self.video_file = "test_invalid_json_video.mp4"
        self.sidecar_file = f"{self.video_file}.vtr.json"

        # Create a dummy video file
        with open(self.video_file, "wb") as f:
            f.write(b"dummy video content")

    def tearDown(self):
        if os.path.exists(self.video_file):
            os.remove(self.video_file)
        if os.path.exists(self.sidecar_file):
            os.remove(self.sidecar_file)
        if "VTR_KDF_SALT" in os.environ:
            del os.environ["VTR_KDF_SALT"]

    def test_invalid_json_sidecar(self):
        """Test that validating a sidecar with invalid JSON returns the correct error."""
        # Create a sidecar file with invalid JSON
        with open(self.sidecar_file, "w") as f:
            f.write("{ invalid json ]")

        validator = VTRValidator(VTRConfig(kdf_salt=b"test_salt"))
        result = validator.validate_container(self.video_file)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "INVALID_JSON")
        self.assertEqual(result.message, "Sidecar file contains invalid JSON.")

    def test_log_injection_prevention(self):
        """Test that ValidationError with newlines is sanitized in logs."""
        # We need to mock the validation to raise a ValidationError with newlines
        # since we can't easily rely on pydantic in this environment.
        from vtr_standard.poc.validator import VTRValidator, ValidationError

        validator = VTRValidator(VTRConfig(kdf_salt=b"test_salt"))

        # Mock VTRSidecar.model_validate to raise a ValidationError
        # We must keep the patch active during the validate_container call
        with unittest.mock.patch('vtr_standard.poc.validator.VTRSidecar.model_validate') as mock_validate:
            mock_error = ValidationError.from_exception_data('Test Error\r\nLine 1\nLine 2\rLine 3', []) if hasattr(ValidationError, 'from_exception_data') else ValidationError('Test Error\r\nLine 1\nLine 2\rLine 3')
            mock_validate.side_effect = mock_error

            # Create a dummy sidecar file so it passes the existence check
            with open(self.sidecar_file, "w") as f:
                f.write('{"dummy": "data"}')

            # We expect a ValidationError to be raised internally and caught/logged
            with self.assertLogs('vtr_standard.poc.validator', level='ERROR') as cm:
                result = validator.validate_container(self.video_file)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "INVALID_SCHEMA")

        # Verify the log message exists and contains no raw newlines within the error part
        log_output = cm.output[0]
        self.assertIn("VTR Schema Validation Error:", log_output)

        # The specific error part should have replaced \n with " | "
        # Pydantic errors usually have many newlines.
        # We check that the log entry itself (excluding the logger prefix) doesn't have internal newlines.
        # assertLogs captures each log record. cm.output is a list of formatted log strings.

        # Check that there are no actual newlines in the captured log message
        # (excluding the one at the end if the formatter adds it, but cm.output usually doesn't include it)
        internal_newlines = log_output.count('\n')
        self.assertEqual(internal_newlines, 0, f"Log message contains raw newlines: {repr(log_output)}")
        self.assertIn(" | ", log_output)

    def test_video_not_found(self):
        """Test that validating a non-existent video returns VIDEO_NOT_FOUND."""
        validator = VTRValidator(VTRConfig(kdf_salt=b"test_salt"))
        result = validator.validate_container("non_existent_video.mp4")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "VIDEO_NOT_FOUND")
        self.assertIn("Video file not found at", result.message)

    def test_video_is_directory(self):
        """Test that validating a directory path as video returns VIDEO_NOT_FOUND."""
        dir_path = "test_dir"
        os.makedirs(dir_path, exist_ok=True)
        try:
            validator = VTRValidator(VTRConfig(kdf_salt=b"test_salt"))
            result = validator.validate_container(dir_path)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.error_code, "VIDEO_NOT_FOUND")
            self.assertIn("Video path is not a file", result.message)
        finally:
            os.rmdir(dir_path)

    def test_sidecar_not_found(self):
        """Test that validating a video with missing sidecar returns SIDECAR_NOT_FOUND."""
        # video_file is created in setUp, but sidecar is not
        validator = VTRValidator(VTRConfig(kdf_salt=b"test_salt"))
        result = validator.validate_container(self.video_file)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "SIDECAR_NOT_FOUND")
        self.assertIn("Sidecar file not found at", result.message)

    def test_sidecar_read_error(self):
        """Test that a generic read failure returns READ_ERROR."""
        # Create a sidecar file so it passes the existence check
        with open(self.sidecar_file, "w") as f:
            f.write('{"dummy": "data"}')

        validator = VTRValidator(VTRConfig(kdf_salt=b"test_salt"))
        with unittest.mock.patch("vtr_standard.poc.validator.open", side_effect=OSError("Disk error")):
            with self.assertLogs("vtr_standard.poc.validator", level="ERROR") as cm:
                result = validator.validate_container(self.video_file)

        self.assertFalse(result.is_valid)
        self.assertIn(result.error_code, ["READ_ERROR", "INVALID_SCHEMA"])
        self.assertIn(result.message, ["An error occurred while reading or parsing the sidecar file.", "Sidecar file does not match the required VTR schema."])
        self.assertTrue(any("VTR Sidecar Read Error" in log or "VTR Schema Validation Error" in log for log in cm.output))

    def _create_valid_sidecar_dict(self, merkle_root="correct_root", liveness=True):
        return {
            "vtr_version": "2.2",
            "hardware_signature": {
                "public_key": "test_pubkey",
                "zk_proof": "test_proof",
                "liveness_flag": liveness,
                "timestamp": 1234567890.0,
                "merkle_root": merkle_root,
                "location_block_hash": "test_loc",
                "nonce": "test_nonce",
                "previous_signature_link": None
            },
            "legal_assertions": {
                "x_vtr_ai_training": False,
                "copyright_notice": "test notice"
            }
        }

    def test_merkle_mismatch(self):
        """Test that a mismatched Merkle root returns MERKLE_MISMATCH."""
        sidecar_data = self._create_valid_sidecar_dict(merkle_root="mismatched_root")
        with open(self.sidecar_file, "w") as f:
            json.dump(sidecar_data, f)

        validator = VTRValidator(VTRConfig(kdf_salt=b"test_salt"))
        with unittest.mock.patch("vtr_standard.poc.validator.MockPRNU._static_hash_video_content", return_value="actual_root"):
            with unittest.mock.patch("vtr_standard.poc.validator.MockPRNU.verify_zk_proof", return_value=True):
                result = validator.validate_container(self.video_file)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "MERKLE_MISMATCH")
        self.assertIn("Sidecar Merkle Root does not match actual video Merkle Root", result.message)
        self.assertNotIn("actual_root", result.details)

    def test_liveness_failure(self):
        """Test that a failed liveness check returns LIVENESS_FAILURE."""
        sidecar_data = self._create_valid_sidecar_dict(liveness=False)
        # Ensure merkle root matches to get past that check
        sidecar_data["hardware_signature"]["merkle_root"] = "actual_root"
        with open(self.sidecar_file, "w") as f:
            json.dump(sidecar_data, f)

        validator = VTRValidator(VTRConfig(kdf_salt=b"test_salt"))
        with unittest.mock.patch("vtr_standard.poc.validator.MockPRNU._static_hash_video_content", return_value="actual_root"):
            with unittest.mock.patch("vtr_standard.poc.validator.MockPRNU.verify_zk_proof", return_value=True):
                result = validator.validate_container(self.video_file)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "LIVENESS_FAILURE")
        self.assertIn("Hardware liveness check failed", result.message)

    def test_invalid_signature(self):
        """Test that an invalid ZK proof returns INVALID_SIGNATURE."""
        sidecar_data = self._create_valid_sidecar_dict()
        with open(self.sidecar_file, "w") as f:
            json.dump(sidecar_data, f)

        validator = VTRValidator(VTRConfig(kdf_salt=b"test_salt"))
        # Mock verify_zk_proof to return False
        with unittest.mock.patch("vtr_standard.poc.validator.MockPRNU.verify_zk_proof", return_value=False):
            result = validator.validate_container(self.video_file)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "INVALID_SIGNATURE")
        self.assertIn("Cryptographic proof verification failed", result.message)
        self.assertNotIn("proof_expected", result.details)
        self.assertNotIn("actual_merkle_root_calculated", result.details)

    def test_validate_container_success(self):
        """Test the happy path: successful validation."""
        sidecar_data = self._create_valid_sidecar_dict(merkle_root="actual_root")
        with open(self.sidecar_file, "w") as f:
            json.dump(sidecar_data, f)

        validator = VTRValidator(VTRConfig(kdf_salt=b"test_salt"))
        with unittest.mock.patch("vtr_standard.poc.validator.MockPRNU._static_hash_video_content", return_value="actual_root"):
            with unittest.mock.patch("vtr_standard.poc.validator.MockPRNU.verify_zk_proof", return_value=True):
                result = validator.validate_container(self.video_file)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.message, "VTR container is valid.")
        self.assertEqual(result.details["merkle_root"], "actual_root")
        self.assertTrue(result.details["liveness"])

if __name__ == "__main__":
    unittest.main()
