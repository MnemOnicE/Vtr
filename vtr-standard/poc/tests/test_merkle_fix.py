import unittest
import os
import shutil
import subprocess
import sys
from unittest.mock import patch

# Adjust path to allow imports from poc directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from poc.merkle import MerkleTree

class TestMerkleFix(unittest.TestCase):

    def test_merkle_raises_file_not_found(self):
        """Test that MerkleTree raises FileNotFoundError for non-existent files."""
        # This test ensures the fix is working. Before the fix, this would fail (no exception raised).
        with self.assertRaises(FileNotFoundError):
            MerkleTree("non_existent_file_for_test.mp4")

    def test_vtr_container_with_missing_file_fails(self):
        """Test that running VTRContainer as a script fails if video files are missing."""
        # Ensure files do not exist
        if os.path.exists("first_video.mp4"): os.remove("first_video.mp4")
        if os.path.exists("second_video.mp4"): os.remove("second_video.mp4")

        # Run the module
        result = subprocess.run(
            [sys.executable, "-m", "vtr-standard.poc.vtr_container"],
            capture_output=True,
            text=True,
            cwd=os.getcwd() # Run from root
        )

        # Before fix: returncode was 0. After fix: returncode should be non-zero (due to crash).
        self.assertNotEqual(result.returncode, 0, "VTRContainer should fail when video files are missing")
        self.assertIn("FileNotFoundError", result.stderr, "Stderr should contain FileNotFoundError traceback")

    def test_normal_operation(self):
        """Test that VTRContainer works correctly when video files exist."""
        # Create dummy files
        with open("first_video.mp4", "wb") as f:
            f.write(b"dummy content 1")
        with open("second_video.mp4", "wb") as f:
            f.write(b"dummy content 2")

        try:
            # Run the module
            result = subprocess.run(
                [sys.executable, "-m", "vtr-standard.poc.vtr_container"],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )

            self.assertEqual(result.returncode, 0, f"VTRContainer failed with valid files. Stderr: {result.stderr}")
            self.assertIn("VTR Sidecar created", result.stdout)

            # Check for sidecars
            self.assertTrue(os.path.exists("first_video.mp4.vtr.json"))
            self.assertTrue(os.path.exists("second_video.mp4.vtr.json"))

        finally:
            # Cleanup
            files = ["first_video.mp4", "second_video.mp4", "first_video.mp4.vtr.json", "second_video.mp4.vtr.json"]
            for f in files:
                if os.path.exists(f):
                    os.remove(f)

if __name__ == "__main__":
    unittest.main()
