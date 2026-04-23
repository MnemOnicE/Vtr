# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import os
import unittest
from unittest import mock

from vtr_standard.poc.config import VTRConfig

class TestVTRConfig(unittest.TestCase):

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_from_env_missing_salt(self):
        """Test ValueError is raised when VTR_KDF_SALT is missing."""
        with self.assertRaises(ValueError) as context:
            VTRConfig.from_env()
        self.assertIn("VTR_KDF_SALT environment variable is missing", str(context.exception))

    @mock.patch.dict(os.environ, {"VTR_KDF_SALT": ""}, clear=True)
    def test_from_env_empty_salt(self):
        """Test ValueError is raised when VTR_KDF_SALT is empty."""
        with self.assertRaises(ValueError) as context:
            VTRConfig.from_env()
        self.assertIn("VTR_KDF_SALT environment variable is missing", str(context.exception))

    @mock.patch.dict(os.environ, {"VTR_KDF_SALT": "my_test_salt"}, clear=True)
    def test_from_env_defaults(self):
        """Test defaults are applied when only VTR_KDF_SALT is provided."""
        config = VTRConfig.from_env()
        self.assertEqual(config.kdf_salt, b"my_test_salt")
        self.assertEqual(config.kdf_iterations, 100000)
        self.assertIsNone(config.test_liveness)
        self.assertIsNone(config.test_gps)
        self.assertEqual(config.env, "DEVELOPMENT")

    @mock.patch.dict(os.environ, {
        "VTR_KDF_SALT": "salt",
        "VTR_KDF_ITERATIONS": "50000",
        "VTR_TEST_LIVENESS": "1",
        "VTR_TEST_GPS": "gps_val",
        "VTR_ENV": "PRODUCTION"
    }, clear=True)
    def test_from_env_all_vars(self):
        """Test all optional environment variables are parsed correctly."""
        config = VTRConfig.from_env()
        self.assertEqual(config.kdf_salt, b"salt")
        self.assertEqual(config.kdf_iterations, 50000)
        self.assertEqual(config.test_liveness, "1")
        self.assertEqual(config.test_gps, "gps_val")
        self.assertEqual(config.env, "PRODUCTION")

    @mock.patch.dict(os.environ, {"VTR_KDF_SALT": "salt", "VTR_KDF_ITERATIONS": "invalid"}, clear=True)
    def test_from_env_invalid_iterations(self):
        """Test fallback to default iterations when VTR_KDF_ITERATIONS is not an integer."""
        config = VTRConfig.from_env()
        self.assertEqual(config.kdf_salt, b"salt")
        self.assertEqual(config.kdf_iterations, 100000)

    @mock.patch.dict(os.environ, {"VTR_KDF_SALT": "salt", "VTR_KDF_ITERATIONS": "-5"}, clear=True)
    def test_from_env_negative_iterations(self):
        """Test iterations fall back to 1 if parsed value is less than 1."""
        config = VTRConfig.from_env()
        self.assertEqual(config.kdf_salt, b"salt")
        self.assertEqual(config.kdf_iterations, 1)

if __name__ == '__main__':
    unittest.main()
