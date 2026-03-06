# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
import os
import sys
from unittest.mock import MagicMock

# VTR-STANDUP: Fallback Mock for restricted environments where pydantic is missing.
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
    mock_pydantic.ValidationError = type("ValidationError", (Exception,), {})
    sys.modules["pydantic"] = mock_pydantic

from vtr_standard.poc.validator import VTRValidator

class TestValidator(unittest.TestCase):
    def setUp(self):
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

    def test_invalid_json_sidecar(self):
        """Test that validating a sidecar with invalid JSON returns the correct error."""
        # Create a sidecar file with invalid JSON
        with open(self.sidecar_file, "w") as f:
            f.write("{ invalid json ]")

        validator = VTRValidator()
        result = validator.validate_container(self.video_file)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "INVALID_JSON")
        self.assertEqual(result.message, "Sidecar file contains invalid JSON.")

if __name__ == "__main__":
    unittest.main()
