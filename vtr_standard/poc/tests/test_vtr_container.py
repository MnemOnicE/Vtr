# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
import os
import tempfile
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

class TestVTRContainer(unittest.TestCase):
    """
    Tests for VTRContainer utility methods.
    """

    def setUp(self):
        # Create a temporary directory to avoid leaving files on disk
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_filename = os.path.join(self.temp_dir.name, "test_dummy_video.mp4")

    def tearDown(self):
        # Cleanup temporary directory and all its contents
        self.temp_dir.cleanup()

    def test_ensure_dummy_video_creates_file(self):
        """
        Verify that ensure_dummy_video creates a 1MB file when it doesn't exist.
        """
        self.assertFalse(os.path.exists(self.test_filename))

        VTRContainer.ensure_dummy_video(self.test_filename)

        self.assertTrue(os.path.exists(self.test_filename))
        self.assertEqual(os.path.getsize(self.test_filename), 1024 * 1024)

    def test_ensure_dummy_video_no_overwrite(self):
        """
        Verify that ensure_dummy_video does not overwrite an existing file.
        """
        # Pre-create a small file
        with open(self.test_filename, "wb") as f:
            f.write(b"existing data")

        initial_size = os.path.getsize(self.test_filename)
        self.assertEqual(initial_size, 13)

        # Call the method
        VTRContainer.ensure_dummy_video(self.test_filename)

        # Verify the file was not overwritten (size is still 13, not 1MB)
        self.assertTrue(os.path.exists(self.test_filename))
        self.assertEqual(os.path.getsize(self.test_filename), initial_size)

if __name__ == "__main__":
    unittest.main()
