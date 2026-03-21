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

    def test_log_injection_prevention(self):
        """Test that ValidationError with newlines is sanitized in logs."""
        # We need to mock the validation to raise a ValidationError with newlines
        # since we can't easily rely on pydantic in this environment.
        from vtr_standard.poc.validator import VTRValidator, ValidationError

        validator = VTRValidator()

        # Mock VTRSidecar.model_validate to raise a ValidationError
        # We must keep the patch active during the validate_container call
        with unittest.mock.patch('vtr_standard.poc.validator.VTRSidecar.model_validate') as mock_validate:
            mock_error = ValidationError.from_exception_data('Test Error\r\nLine 1\nLine 2\rLine 3', []) if hasattr(ValidationError, 'from_exception_data') else Exception('Test Error\r\nLine 1\nLine 2\rLine 3')
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

if __name__ == "__main__":
    unittest.main()
