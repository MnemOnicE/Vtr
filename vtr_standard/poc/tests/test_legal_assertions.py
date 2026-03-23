# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
import os
import sys
import json
from unittest.mock import MagicMock

# VTR-STANDUP: Fallback Mock for restricted environments where pydantic is missing.
# Sentinel: "Trust nothing, but verify the logic even if the infra is brittle."
try:
    import pydantic
except ImportError:
    class MockBaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
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
    sys.modules["pydantic"] = mock_pydantic

from vtr_standard.poc.vtr_container import VTRContainer

class TestLegalAssertions(unittest.TestCase):
    """
    Tests the legal assertions block in VTRContainer, specifically the x_vtr_ai_training flag.
    """

    def setUp(self):
        self.video_path = "test_ai_training.mp4"
        self.sidecar_path = f"{self.video_path}.vtr.json"

        # Create a tiny dummy video file
        with open(self.video_path, "wb") as f:
            f.write(b"dummy video content")

        # Set environment variables for deterministic output
        os.environ["VTR_TEST_LIVENESS"] = "true"
        os.environ["VTR_TEST_GPS"] = "locked"

        self.container = VTRContainer(self.video_path, "TEST_SENSOR_AI")

    def tearDown(self):
        # Clean up files
        if os.path.exists(self.video_path):
            os.remove(self.video_path)
        if os.path.exists(self.sidecar_path):
            os.remove(self.sidecar_path)

        # Clean up environment variables
        os.environ.pop("VTR_TEST_LIVENESS", None)
        os.environ.pop("VTR_TEST_GPS", None)

    def test_ai_training_flag_true(self):
        """
        Verify that allow_ai_training=True results in x_vtr_ai_training=True in the sidecar JSON.
        """
        self.container.create_sidecar(allow_ai_training=True)

        # Ensure file exists
        self.assertTrue(os.path.exists(self.sidecar_path))

        # Read and parse JSON
        with open(self.sidecar_path, 'r') as f:
            sidecar_data = json.load(f)

        # Assert the value
        self.assertTrue(sidecar_data["legal_assertions"]["x_vtr_ai_training"])

    def test_ai_training_flag_false(self):
        """
        Verify that allow_ai_training=False results in x_vtr_ai_training=False in the sidecar JSON.
        """
        self.container.create_sidecar(allow_ai_training=False)

        # Ensure file exists
        self.assertTrue(os.path.exists(self.sidecar_path))

        # Read and parse JSON
        with open(self.sidecar_path, 'r') as f:
            sidecar_data = json.load(f)

        # Assert the value
        self.assertFalse(sidecar_data["legal_assertions"]["x_vtr_ai_training"])

if __name__ == "__main__":
    unittest.main()
