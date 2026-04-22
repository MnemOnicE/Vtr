# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
import sys
from unittest.mock import MagicMock

# VTR-STANDUP: Fallback Mock for restricted environments where pydantic is missing.
from vtr_standard.poc.tests.common import setup_pydantic_mock
setup_pydantic_mock()

from vtr_standard.poc.schemas import VTRSidecar, HardwareSignature, LegalAssertions, VTR_VERSION, VTR_SIDECAR_SCHEMA

class TestSchemas(unittest.TestCase):
    def test_vtr_sidecar_schema_constant(self):
        """Test that VTR_SIDECAR_SCHEMA is a valid dictionary and has the expected structure."""
        self.assertIsInstance(VTR_SIDECAR_SCHEMA, dict)
        # Note: Pydantic v2 model_json_schema might not include $schema by default or might have different titles
        # So we check for the core presence of required fields.
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
