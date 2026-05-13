# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
import os
import sys
import tempfile
from unittest.mock import MagicMock

# VTR-STANDUP: Fallback Mock for restricted environments where pydantic is missing.
# Sentinel: "Trust nothing, but verify the logic even if the infra is brittle."
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
from vtr_standard.poc.config import VTRConfig

class TestVTRContainerOverwrite(unittest.TestCase):
    """
    Tests the overwrite protection logic in VTRContainer.
    """

    def setUp(self):
        os.environ["VTR_KDF_SALT"] = "test_overwrite_salt"
        self.video_path = "test_overwrite.mp4"
        self.sidecar_path = f"{self.video_path}.vtr.json"
        # Create a dummy video file
        with open(self.video_path, "wb") as f:
            f.write(b"dummy video content")

        self.container = VTRContainer(self.video_path, "TEST_SENSOR", VTRConfig(kdf_salt=b"test_salt"))
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_filename = os.path.join(self.temp_dir.name, "test_dummy_video.mp4")

    def tearDown(self):
        if os.path.exists(self.video_path):
            os.remove(self.video_path)
        if os.path.exists(self.sidecar_path):
            os.remove(self.sidecar_path)
        if "VTR_KDF_SALT" in os.environ:
            del os.environ["VTR_KDF_SALT"]
        self.temp_dir.cleanup()

    def test_create_sidecar_raises_if_exists_and_no_overwrite(self):
        """
        Verify that FileExistsError is raised when sidecar exists and overwrite=False.
        """
        # 1. Create the sidecar for the first time
        self.container.create_sidecar(overwrite=False)
        self.assertTrue(os.path.exists(self.sidecar_path))

        # 2. Attempt to create it again without overwrite=True
        with self.assertRaises(FileExistsError) as cm:
            self.container.create_sidecar(overwrite=False)

        self.assertIn("Sidecar file already exists", str(cm.exception))

    def test_create_sidecar_succeeds_if_exists_and_overwrite_true(self):
        """
        Verify that sidecar is overwritten when overwrite=True.
        """
        # 1. Create the sidecar for the first time
        self.container.create_sidecar(overwrite=False)

        # 2. Create it again with overwrite=True
        # This should succeed without raising FileExistsError
        self.container.create_sidecar(overwrite=True)
        self.assertTrue(os.path.exists(self.sidecar_path))

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

        # Additional assert as per PR feedback
        with open(self.test_filename, "rb") as f:
            content = f.read()
        self.assertEqual(content, b"existing data")

if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
