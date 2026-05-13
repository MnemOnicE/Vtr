# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
import os
from vtr_standard.poc.vtr_container import VTRContainer

class TestVTRContainerOverwrite(unittest.TestCase):
    """
    Tests the overwrite protection logic in VTRContainer.
    """

    def setUp(self):
        self.video_path = "test_overwrite.mp4"
        self.sidecar_path = f"{self.video_path}.vtr.json"
        # Create a dummy video file
        with open(self.video_path, "wb") as f:
            f.write(b"dummy video content")

        self.container = VTRContainer(self.video_path, "TEST_SENSOR")

    def tearDown(self):
        if os.path.exists(self.video_path):
            os.remove(self.video_path)
        if os.path.exists(self.sidecar_path):
            os.remove(self.sidecar_path)

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

if __name__ == "__main__":
    unittest.main()
