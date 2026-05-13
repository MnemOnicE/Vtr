# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
import os
from unittest.mock import patch
from vtr_standard.poc.config import VTRConfig

class TestVTRConfig(unittest.TestCase):
    """Tests for the VTRConfig class."""

    def test_from_env_success(self):
        """Test successful creation of VTRConfig from environment variables."""
        env_vars = {
            "VTR_KDF_SALT": "test_salt",
            "VTR_KDF_ITERATIONS": "50000",
            "VTR_TEST_LIVENESS": "true",
            "VTR_TEST_GPS": "1.0,2.0",
            "VTR_ENV": "TESTING"
        }
        with patch.dict(os.environ, env_vars, clear=True):
            config = VTRConfig.from_env()
            self.assertEqual(config.kdf_salt, b"test_salt")
            self.assertEqual(config.kdf_iterations, 50000)
            self.assertEqual(config.test_liveness, "true")
            self.assertEqual(config.test_gps, "1.0,2.0")
            self.assertEqual(config.env, "TESTING")

    def test_from_env_missing_salt(self):
        """Test that ValueError is raised when VTR_KDF_SALT is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "VTR_KDF_SALT environment variable is missing"):
                VTRConfig.from_env()

    def test_from_env_empty_salt(self):
        """Test that ValueError is raised when VTR_KDF_SALT is empty."""
        with patch.dict(os.environ, {"VTR_KDF_SALT": ""}, clear=True):
            with self.assertRaisesRegex(ValueError, "^CRITICAL SECURITY REQUIREMENT: VTR_KDF_SALT environment variable is missing"):
                VTRConfig.from_env()

    def test_from_env_default_iterations(self):
        """Test default iterations when VTR_KDF_ITERATIONS is not set."""
        with patch.dict(os.environ, {"VTR_KDF_SALT": "test_salt"}, clear=True):
            config = VTRConfig.from_env()
            self.assertEqual(config.kdf_iterations, 100000)

    def test_from_env_invalid_iterations(self):
        """Test fallback to default when VTR_KDF_ITERATIONS is not a valid integer."""
        with patch.dict(os.environ, {"VTR_KDF_SALT": "test_salt", "VTR_KDF_ITERATIONS": "invalid"}, clear=True):
            config = VTRConfig.from_env()
            self.assertEqual(config.kdf_iterations, 100000)

    def test_from_env_custom_iterations(self):
        """Test that custom iterations are correctly parsed."""
        with patch.dict(os.environ, {"VTR_KDF_SALT": "test_salt", "VTR_KDF_ITERATIONS": "200000"}, clear=True):
            config = VTRConfig.from_env()
            self.assertEqual(config.kdf_iterations, 200000)

    def test_from_env_iteration_clamping(self):
        """Test that iterations are clamped to a minimum of 1."""
        for val in ["-100", "0"]:
            with patch.dict(os.environ, {"VTR_KDF_SALT": "test_salt", "VTR_KDF_ITERATIONS": val}, clear=True):
                config = VTRConfig.from_env()
                self.assertEqual(config.kdf_iterations, 1)

    def test_from_env_defaults(self):
        """Test default values for optional environment variables."""
        with patch.dict(os.environ, {"VTR_KDF_SALT": "test_salt"}, clear=True):
            config = VTRConfig.from_env()
            self.assertIsNone(config.test_liveness)
            self.assertIsNone(config.test_gps)
            self.assertEqual(config.env, "DEVELOPMENT")

if __name__ == "__main__":
    unittest.main()
