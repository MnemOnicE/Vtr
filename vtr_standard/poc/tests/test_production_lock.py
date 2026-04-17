# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
import os
from unittest.mock import patch
from vtr_standard.poc.mock_prnu import MockPRNU

class TestProductionLock(unittest.TestCase):
    """
    Tests the Security Hardening: Production Safeguards for MockPRNU.
    """

    def setUp(self):
        # We need a salt even for production lock tests that reach the KDF block
        os.environ["VTR_KDF_SALT"] = "lock_test_salt"

    def tearDown(self):
        if "VTR_KDF_SALT" in os.environ:
            del os.environ["VTR_KDF_SALT"]

    def test_production_lock_active(self):
        """
        Verifies that MockPRNU raises RuntimeError when VTR_ENV is PRODUCTION.
        """
        with patch.dict(os.environ, {"VTR_ENV": "PRODUCTION"}):
            with self.assertRaises(RuntimeError) as cm:
                MockPRNU("sensor_123")

            self.assertIn("CRITICAL SECURITY VIOLATION", str(cm.exception))
            self.assertIn("PRODUCTION environment", str(cm.exception))

    def test_production_lock_inactive(self):
        """
        Verifies that MockPRNU initializes normally when VTR_ENV is not PRODUCTION.
        """
        # Test default (None)
        # Note: patch.dict(os.environ, {}, clear=True) will clear the setUp salt too.
        # So we must re-add it or use a less aggressive patch.
        with patch.dict(os.environ, {"VTR_KDF_SALT": "lock_test_salt"}, clear=True):
             try:
                MockPRNU("sensor_123")
             except RuntimeError:
                self.fail("MockPRNU raised RuntimeError unexpectedly without VTR_ENV set")

        # Test other values
        with patch.dict(os.environ, {"VTR_ENV": "DEVELOPMENT", "VTR_KDF_SALT": "lock_test_salt"}):
             try:
                MockPRNU("sensor_123")
             except RuntimeError:
                self.fail("MockPRNU raised RuntimeError unexpectedly in DEVELOPMENT")

if __name__ == '__main__':
    unittest.main()
