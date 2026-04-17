# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

"""
Tests for ingest_manager.py
"""

import unittest
from unittest.mock import patch, MagicMock, call
import subprocess
import os
import sys

# Ensure the scripts directory is in the path so we can import ingest_manager
import sys
# Assuming the project structure allows importing from the root or a standard package path
from scripts import ingest_manager

import ingest_manager

class TestGetCommitCount(unittest.TestCase):
    """Tests for get_commit_count function."""

    @patch('ingest_manager.subprocess.run')
    def test_get_commit_count_success(self, mock_run):
        """Test successful retrieval of commit count."""
        mock_result = MagicMock()
        mock_result.stdout = "42\n"
        mock_run.return_value = mock_result

        count = ingest_manager.get_commit_count()

        self.assertEqual(count, 42)
        mock_run.assert_called_once_with(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )

    @patch('ingest_manager.subprocess.run')
    def test_get_commit_count_called_process_error(self, mock_run):
        """Test handling of CalledProcessError from git."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git"])

        with self.assertRaises(SystemExit) as cm:
            ingest_manager.get_commit_count()

        self.assertEqual(cm.exception.code, 1)

    @patch('ingest_manager.subprocess.run')
    def test_get_commit_count_value_error(self, mock_run):
        """Test handling of unexpected output from git."""
        mock_result = MagicMock()
        mock_result.stdout = "not_a_number\n"
        mock_run.return_value = mock_result

        with self.assertRaises(SystemExit) as cm:
            ingest_manager.get_commit_count()

        self.assertEqual(cm.exception.code, 1)

class TestRunGitingest(unittest.TestCase):
    """Tests for run_gitingest function."""

    @patch('ingest_manager.os.makedirs')
    @patch('ingest_manager.os.path.exists')
    @patch('ingest_manager.datetime')
    @patch('ingest_manager.subprocess.run')
    @patch('ingest_manager.os.rename')
    def test_run_gitingest_success(self, mock_rename, mock_run, mock_datetime, mock_exists, mock_makedirs):
        """Test happy path for run_gitingest."""
        # Side effect for os.path.exists:
        # 1. Check INGEST_DIR exists -> False
        # 2. Check digest.txt exists -> True
        mock_exists.side_effect = [False, True]

        mock_now = MagicMock()
        mock_now.strftime.return_value = "20250101_120000"
        mock_datetime.now.return_value = mock_now

        ingest_manager.run_gitingest()

        mock_makedirs.assert_called_once_with("ingests")
        mock_run.assert_called_once_with(["gitingest", "."], check=True)
        expected_filepath = os.path.join("ingests", "digest_20250101_120000.txt")
        mock_rename.assert_called_once_with("digest.txt", expected_filepath)

    @patch('ingest_manager.os.path.exists')
    @patch('ingest_manager.datetime')
    @patch('ingest_manager.subprocess.run')
    def test_run_gitingest_missing_digest(self, mock_run, mock_datetime, mock_exists):
        """Test failure when gitingest doesn't produce digest.txt."""
        # Mock INGEST_DIR exists, but digest.txt doesn't
        mock_exists.side_effect = [True, False]

        mock_now = MagicMock()
        mock_now.strftime.return_value = "20250101_120000"
        mock_datetime.now.return_value = mock_now

        with self.assertRaises(SystemExit) as cm:
            ingest_manager.run_gitingest()

        self.assertEqual(cm.exception.code, 1)

    @patch('ingest_manager.os.path.exists')
    @patch('ingest_manager.subprocess.run')
    def test_run_gitingest_subprocess_error(self, mock_run, mock_exists):
        """Test failure when gitingest subprocess fails."""
        mock_exists.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, ["gitingest"])

        with self.assertRaises(SystemExit) as cm:
            ingest_manager.run_gitingest()

        self.assertEqual(cm.exception.code, 1)

class TestRotateIngests(unittest.TestCase):
    """Tests for rotate_ingests function."""

    @patch('ingest_manager.glob.glob')
    @patch('ingest_manager.os.path.getmtime')
    @patch('ingest_manager.os.remove')
    def test_rotate_ingests_multiple_files(self, mock_remove, mock_getmtime, mock_glob):
        """Test rotation when there are more than MAX_INGESTS files."""
        # 5 mock files
        mock_files = [f"ingests/digest_{i}.txt" for i in range(5)]
        mock_glob.return_value = mock_files

        # Mock mtimes to be in order 0 to 4 (0 is oldest)
        mock_getmtime.side_effect = lambda x: int(x.split('_')[1].split('.')[0])

        ingest_manager.rotate_ingests()

        # Should delete the 2 oldest files (0 and 1)
        self.assertEqual(mock_remove.call_count, 2)
        mock_remove.assert_has_calls([
            call("ingests/digest_0.txt"),
            call("ingests/digest_1.txt")
        ], any_order=True)

    @patch('ingest_manager.glob.glob')
    @patch('ingest_manager.os.path.getmtime')
    @patch('ingest_manager.os.remove')
    def test_rotate_ingests_no_rotation_needed(self, mock_remove, mock_getmtime, mock_glob):
        """Test that no files are deleted if count <= MAX_INGESTS."""
        # 2 mock files
        mock_files = ["ingests/digest_1.txt", "ingests/digest_2.txt"]
        mock_glob.return_value = mock_files
        # Return same mtime for both
        mock_getmtime.return_value = 1000

        ingest_manager.rotate_ingests()

        mock_remove.assert_not_called()

class TestMain(unittest.TestCase):
    """Tests for main function orchestration logic."""

    @patch('ingest_manager.argparse.ArgumentParser.parse_args')
    @patch('ingest_manager.get_commit_count')
    @patch('ingest_manager.run_gitingest')
    @patch('ingest_manager.rotate_ingests')
    def test_main_force(self, mock_rotate, mock_run, mock_get_count, mock_args):
        """Test main when --force is used."""
        mock_args.return_value = MagicMock(force=True)
        # Count is 4 (not multiple of 5)
        mock_get_count.return_value = 4

        ingest_manager.main()

        mock_run.assert_called_once()
        mock_rotate.assert_called_once()

    @patch('ingest_manager.argparse.ArgumentParser.parse_args')
    @patch('ingest_manager.get_commit_count')
    @patch('ingest_manager.run_gitingest')
    @patch('ingest_manager.rotate_ingests')
    def test_main_modulo_trigger(self, mock_rotate, mock_run, mock_get_count, mock_args):
        """Test main when commit count is a multiple of 5."""
        mock_args.return_value = MagicMock(force=False)
        # Count is 10 (multiple of 5)
        mock_get_count.return_value = 10

        ingest_manager.main()

        mock_run.assert_called_once()
        mock_rotate.assert_called_once()

    @patch('ingest_manager.argparse.ArgumentParser.parse_args')
    @patch('ingest_manager.get_commit_count')
    @patch('ingest_manager.run_gitingest')
    @patch('ingest_manager.rotate_ingests')
    def test_main_skip(self, mock_rotate, mock_run, mock_get_count, mock_args):
        """Test main skips when no conditions met."""
        mock_args.return_value = MagicMock(force=False)
        # Count is 3 (not multiple of 5)
        mock_get_count.return_value = 3

        ingest_manager.main()

        mock_run.assert_not_called()
        mock_rotate.assert_not_called()

if __name__ == "__main__":
    unittest.main()
