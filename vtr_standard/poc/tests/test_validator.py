# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import os
import sys
import unittest
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

    def test_video_not_found(self):
        """Test that validating a non-existent video file returns the correct error."""
        non_existent_video = "non_existent_video.mp4"
        # Ensure it doesn't exist
        if os.path.exists(non_existent_video):
            os.remove(non_existent_video)

        validator = VTRValidator()
        result = validator.validate_container(non_existent_video)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "VIDEO_NOT_FOUND")
        self.assertEqual(result.message, f"Video file not found at: {non_existent_video}")

    def test_video_path_is_directory(self):
        """Test that validating a directory as a video file returns the correct error."""
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = VTRValidator()
            result = validator.validate_container(temp_dir)

            self.assertFalse(result.is_valid)
            self.assertEqual(result.error_code, "VIDEO_NOT_FOUND")
            self.assertEqual(result.message, f"Video path is not a file: {temp_dir}")

if __name__ == "__main__":
    unittest.main()
