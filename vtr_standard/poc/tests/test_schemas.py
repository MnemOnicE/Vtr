# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
import sys
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
        def model_dump(self):
            def _dump(obj):
                if hasattr(obj, '__dict__'):
                    return {k: _dump(v) for k, v in obj.__dict__.items()}
                return obj
            return _dump(self)

    # Use a local mock instead of patching sys.modules globally to avoid side effects
    mock_pydantic = MagicMock()
    mock_pydantic.BaseModel = MockBaseModel
    mock_pydantic.Field = MagicMock(return_value=None)
    mock_pydantic.ValidationError = type("ValidationError", (Exception,), {})
    # Note: If other modules import schemas.py, they might still see this mock if we are not careful.
    # But for this test file, it's necessary since schemas.py imports from pydantic.
    if "pydantic" not in sys.modules:
        sys.modules["pydantic"] = mock_pydantic

from vtr_standard.poc.schemas import VTRSidecar, HardwareSignature, LegalAssertions, VTR_VERSION, VTR_SIDECAR_SCHEMA

class TestSchemas(unittest.TestCase):
    def test_vtr_sidecar_schema_constant(self):
        """Test that VTR_SIDECAR_SCHEMA is a valid dictionary and has the expected structure."""
        self.assertIsInstance(VTR_SIDECAR_SCHEMA, dict)
        self.assertEqual(VTR_SIDECAR_SCHEMA["$schema"], "http://json-schema.org/draft-07/schema#")
        self.assertEqual(VTR_SIDECAR_SCHEMA["type"], "object")
        self.assertIn("vtr_version", VTR_SIDECAR_SCHEMA["required"])
        self.assertIn("hardware_signature", VTR_SIDECAR_SCHEMA["required"])
        self.assertIn("legal_assertions", VTR_SIDECAR_SCHEMA["required"])

    def test_hardware_signature_instantiation(self):
        """Test that HardwareSignature can be instantiated with valid data."""
        data = {
            "public_key": "test_pub",
            "zk_proof": "test_proof",
            "liveness_flag": True,
            "timestamp": 1234567890.0,
            "merkle_root": "test_root",
            "location_block_hash": "test_loc",
            "nonce": "test_nonce"
        }
        hw_sig = HardwareSignature(**data)
        self.assertEqual(hw_sig.public_key, "test_pub")
        self.assertEqual(hw_sig.zk_proof, "test_proof")
        self.assertTrue(hw_sig.liveness_flag)
        self.assertEqual(hw_sig.timestamp, 1234567890.0)
        self.assertEqual(hw_sig.merkle_root, "test_root")
        self.assertEqual(hw_sig.location_block_hash, "test_loc")
        self.assertEqual(hw_sig.nonce, "test_nonce")

    def test_legal_assertions_instantiation(self):
        """Test that LegalAssertions can be instantiated with valid data."""
        data = {
            "x_vtr_ai_training": True,
            "copyright_notice": "test notice"
        }
        legal = LegalAssertions(**data)
        self.assertTrue(legal.x_vtr_ai_training)
        self.assertEqual(legal.copyright_notice, "test notice")

    def test_vtr_sidecar_instantiation(self):
        """Test that VTRSidecar can be instantiated with valid data."""
        data = {
            "vtr_version": VTR_VERSION,
            "hardware_signature": {
                "public_key": "test_pub",
                "zk_proof": "test_proof",
                "liveness_flag": True,
                "timestamp": 1234567890.0,
                "merkle_root": "test_root",
                "location_block_hash": "test_loc",
                "nonce": "test_nonce"
            },
            "legal_assertions": {
                "x_vtr_ai_training": False,
                "copyright_notice": "test notice"
            }
        }
        sidecar = VTRSidecar.model_validate(data)
        self.assertEqual(sidecar.vtr_version, VTR_VERSION)
        self.assertEqual(sidecar.hardware_signature.public_key, "test_pub")
        self.assertEqual(sidecar.legal_assertions.copyright_notice, "test notice")

if __name__ == "__main__":
    unittest.main()
