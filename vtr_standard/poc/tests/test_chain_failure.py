# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
import os
import json
import sys
import logging
from unittest.mock import MagicMock

# VTR-STANDUP: Fallback Mock for restricted environments where pydantic is missing.
from vtr_standard.poc.tests.common import setup_pydantic_mock
setup_pydantic_mock()

from vtr_standard.poc.vtr_container import VTRContainer
from vtr_standard.poc.config import VTRConfig
from vtr_standard.poc.validator import VTRSidecar, ValidationError

# Disable logging for tests
logging.getLogger("vtr_standard.poc.vtr_container").setLevel(logging.CRITICAL)

class TestChainFailure(unittest.TestCase):
    def setUp(self):
        os.environ["VTR_KDF_SALT"] = "test_chain_salt"
        self.video_file = "test_chain_failure_video.mp4"
        with open(self.video_file, "wb") as f:
            f.write(os.urandom(1024))

        self.bad_sidecar = "bad_sidecar.vtr.json"
        with open(self.bad_sidecar, "w") as f:
            json.dump({"broken": "schema"}, f)

    def tearDown(self):
        if os.path.exists(self.video_file):
            os.remove(self.video_file)
        if os.path.exists(self.bad_sidecar):
            os.remove(self.bad_sidecar)
        if os.path.exists(f"{self.video_file}.vtr.json"):
            os.remove(f"{self.video_file}.vtr.json")
        if "VTR_KDF_SALT" in os.environ:
            del os.environ["VTR_KDF_SALT"]

    def test_chain_failure_raises_exception(self):
        """Test that linking to an invalid sidecar raises ValueError."""
        container = VTRContainer(self.video_file, "TEST_SENSOR", VTRConfig(kdf_salt=b"test_salt"))

        # The bad_sidecar has invalid schema.
        # With our improved MockBaseModel, model_validate should raise Exception/ValidationError naturally.
        with self.assertRaises(ValueError) as context:
            container.create_sidecar(previous_sidecar_path=self.bad_sidecar)

        # The bad_sidecar has invalid schema, which gets caught and re-raised as "Chain of Custody Failure: ..."
        self.assertIn("Chain of Custody Failure:", str(context.exception))
        self.assertIn("INVALID_SCHEMA:", str(context.exception))

    def test_missing_sidecar_raises_exception(self):
        """Test that linking to a non-existent sidecar raises FileNotFoundError."""
        container = VTRContainer(self.video_file, "TEST_SENSOR", VTRConfig(kdf_salt=b"test_salt"))
        missing_path = "non_existent.json"

        with self.assertRaises(ValueError) as context:
            container.create_sidecar(previous_sidecar_path=missing_path)

        self.assertIn("SIDECAR_NOT_FOUND:", str(context.exception))


    def test_invalid_json_sidecar_raises_exception(self):
        """Test that linking to a sidecar with invalid JSON raises ValueError."""
        container = VTRContainer(self.video_file, "TEST_SENSOR", VTRConfig(kdf_salt=b"test_salt"))

        # Create an invalid JSON sidecar
        invalid_json_sidecar = "invalid_json.vtr.json"
        with open(invalid_json_sidecar, "w") as f:
            f.write("{ invalid json format ")

        try:
            with self.assertRaises(ValueError) as context:
                container.create_sidecar(previous_sidecar_path=invalid_json_sidecar)

            self.assertIn("INVALID_JSON:", str(context.exception))
        finally:
            if os.path.exists(invalid_json_sidecar):
                os.remove(invalid_json_sidecar)

if __name__ == "__main__":
    unittest.main()
