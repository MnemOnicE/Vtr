# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
import os
import sys
import io
import json
from unittest.mock import patch, MagicMock

from vtr_standard.poc.vtr_container import VTRContainer
from vtr_standard.poc.cli import cmd_verify

class TestCLI(unittest.TestCase):
    """
    Integration tests for the VTR CLI commands.
    """

    def setUp(self):
        # Setup environment variables for deterministic mock behavior
        os.environ["VTR_TEST_LIVENESS"] = "true"
        os.environ["VTR_TEST_GPS"] = "34.0522,-118.2437"

        # Use patch.dict instead of setting os.environ directly to avoid state leakage
        self.env_patcher = patch.dict(os.environ, {
            "VTR_TEST_LIVENESS": "true",
            "VTR_TEST_GPS": "34.0522,-118.2437",
            "VTR_KDF_SALT": "test_salt_cli_123"
        })
        self.env_patcher.start()

        # Clear LRU caches that depend on environment variables
        from vtr_standard.poc.mock_prnu import MockPRNU
        MockPRNU._get_kdf_params.cache_clear()

        self.video_path = "test_cli_video.mp4"
        self.sidecar_path = f"{self.video_path}.vtr.json"

        # Create a dummy video file
        with open(self.video_path, "wb") as f:
            f.write(b"dummy video content for cli tests")

        self.sensor_id = "TEST_SENSOR_CLI"

    def tearDown(self):
        # Cleanup
        try:
            if os.path.exists(self.video_path):
                os.remove(self.video_path)
            if os.path.exists(self.sidecar_path):
                os.remove(self.sidecar_path)
        finally:
            self.env_patcher.stop()
            from vtr_standard.poc.mock_prnu import MockPRNU
            MockPRNU._get_kdf_params.cache_clear()

    def test_setup_teardown(self):
        """Sanity check that the file is created and cleaned up"""
        self.assertTrue(os.path.exists(self.video_path))

    @patch("vtr_standard.poc.cli.logger")
    def test_cmd_verify_success(self, mock_logger):
        """
        Verify that cmd_verify succeeds on a valid container and sidecar.
        """
        # Generate a valid sidecar
        container = VTRContainer(self.video_path, self.sensor_id)
        container.create_sidecar(overwrite=True)

        # Create mock arguments for the CLI command
        args = MagicMock()
        args.video_path = self.video_path
        args.sidecar = self.sidecar_path
        args.json = False

        # Should run without raising SystemExit
        try:
            cmd_verify(args)
        except SystemExit as e:
            self.fail(f"cmd_verify raised SystemExit unexpectedly: {e}")

        # Check logger calls to verify success output
        mock_logger.info.assert_any_call("\n✅  VERIFICATION SUCCESSFUL")

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_cmd_verify_success_json(self, mock_stdout):
        """
        Verify that cmd_verify outputs correct JSON on success when --json is passed.
        """
        # Generate a valid sidecar
        container = VTRContainer(self.video_path, self.sensor_id)
        container.create_sidecar(overwrite=True)

        # Create mock arguments for the CLI command
        args = MagicMock()
        args.video_path = self.video_path
        args.sidecar = self.sidecar_path
        args.json = True

        # Should run without raising SystemExit
        try:
            cmd_verify(args)
        except SystemExit as e:
            self.fail(f"cmd_verify raised SystemExit unexpectedly: {e}")

        # Verify JSON output
        output = mock_stdout.getvalue()
        try:
            result_json = json.loads(output)
            self.assertTrue(result_json.get("is_valid"))
            self.assertIsNone(result_json.get("error_code"))
        except json.JSONDecodeError:
            self.fail("Output was not valid JSON")

    @patch("vtr_standard.poc.cli.logger")
    def test_cmd_verify_failure(self, mock_logger):
        """
        Verify that cmd_verify fails gracefully when the sidecar doesn't match the video.
        """
        # Generate a valid sidecar
        container = VTRContainer(self.video_path, self.sensor_id)
        container.create_sidecar(overwrite=True)

        # Tamper with the video to invalidate the signature
        with open(self.video_path, "ab") as f:
            f.write(b"tampered")

        # Create mock arguments for the CLI command
        args = MagicMock()
        args.video_path = self.video_path
        args.sidecar = self.sidecar_path
        args.json = False

        # Should raise SystemExit(1)
        with self.assertRaises(SystemExit) as cm:
            cmd_verify(args)

        self.assertEqual(cm.exception.code, 1)

        # Check logger calls to verify failure output
        mock_logger.error.assert_any_call("\n❌  VERIFICATION FAILED")

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_cmd_verify_failure_json(self, mock_stdout):
        """
        Verify that cmd_verify outputs JSON with failure details when --json is passed and validation fails.
        """
        # Generate a valid sidecar
        container = VTRContainer(self.video_path, self.sensor_id)
        container.create_sidecar(overwrite=True)

        # Tamper with the video to invalidate the signature
        with open(self.video_path, "ab") as f:
            f.write(b"tampered")

        # Create mock arguments for the CLI command
        args = MagicMock()
        args.video_path = self.video_path
        args.sidecar = self.sidecar_path
        args.json = True

        # Should raise SystemExit(1)
        with self.assertRaises(SystemExit) as cm:
            cmd_verify(args)

        self.assertEqual(cm.exception.code, 1)

        # Verify JSON output
        output = mock_stdout.getvalue()
        try:
            result_json = json.loads(output)
            self.assertFalse(result_json.get("is_valid"))
            self.assertIsNotNone(result_json.get("error_code"))
        except json.JSONDecodeError:
            self.fail("Output was not valid JSON")

if __name__ == "__main__":
    unittest.main()
