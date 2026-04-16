# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
from unittest.mock import patch, MagicMock
import subprocess
import sys
import os

# Add scripts directory to path to import ingest_manager
sys.path.append(os.path.join(os.path.dirname(__file__)))
from ingest_manager import get_commit_count

class TestIngestManager(unittest.TestCase):

    @patch("subprocess.run")
    def test_get_commit_count_success(self, mock_run):
        """Test get_commit_count returns an integer on success."""
        mock_result = MagicMock()
        mock_result.stdout = "10\n"
        mock_run.return_value = mock_result

        count = get_commit_count()

        self.assertEqual(count, 10)
        mock_run.assert_called_once_with(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )

    @patch("subprocess.run")
    @patch("sys.exit")
    @patch("builtins.print")
    def test_get_commit_count_git_failure(self, mock_print, mock_exit, mock_run):
        """Test get_commit_count exits on git failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        get_commit_count()

        mock_print.assert_called_once_with("Error: Could not determine commit count. Is this a git repository?")
        mock_exit.assert_called_once_with(1)

    @patch("subprocess.run")
    @patch("sys.exit")
    @patch("builtins.print")
    def test_get_commit_count_invalid_output(self, mock_print, mock_exit, mock_run):
        """Test get_commit_count exits on invalid output."""
        mock_result = MagicMock()
        mock_result.stdout = "not-a-number\n"
        mock_run.return_value = mock_result

        get_commit_count()

        mock_print.assert_called_once_with("Error: Unexpected output from git.")
        mock_exit.assert_called_once_with(1)

if __name__ == "__main__":
    unittest.main()
