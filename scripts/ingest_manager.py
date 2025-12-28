#!/usr/bin/env python3
"""
Ingest Manager Script
---------------------
Manages the generation and rotation of 'gitingest' snapshots of the codebase.

Usage:
    python3 scripts/ingest_manager.py [--force]

Logic:
    1. Checks the total commit count of the current branch.
    2. If count % 5 == 0 OR --force is used:
       a. Creates 'ingests/' directory if it doesn't exist.
       b. Runs 'gitingest .' and saves output to 'ingests/digest_YYYYMMDD_HHMMSS.txt'.
       c. Retains only the 3 most recent digest files, deleting older ones.
    3. Otherwise, prints a message and exits without action.
"""

import os
import sys
import subprocess
import glob
from datetime import datetime
import argparse

INGEST_DIR = "ingests"
MAX_INGESTS = 3
MODULO_TRIGGER = 5

def get_commit_count():
    """Returns the total number of commits in the current branch."""
    try:
        # git rev-list --count HEAD
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return int(result.stdout.strip())
    except subprocess.CalledProcessError:
        print("Error: Could not determine commit count. Is this a git repository?")
        sys.exit(1)
    except ValueError:
        print("Error: Unexpected output from git.")
        sys.exit(1)

def run_gitingest():
    """Runs gitingest and saves the output."""
    if not os.path.exists(INGEST_DIR):
        os.makedirs(INGEST_DIR)
        print(f"Created directory: {INGEST_DIR}/")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"digest_{timestamp}.txt"
    filepath = os.path.join(INGEST_DIR, filename)

    print(f"Generating codebase digest: {filepath} ...")

    # Run gitingest (outputs to digest.txt by default)
    try:
        subprocess.run(["gitingest", "."], check=True)

        # Move digest.txt to destination
        if os.path.exists("digest.txt"):
            os.rename("digest.txt", filepath)
            print("Digest generation complete.")
        else:
            print("Error: gitingest did not produce digest.txt")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"Error running gitingest: {e}")
        sys.exit(1)

def rotate_ingests():
    """Keeps only the MAX_INGESTS most recent files."""
    files = glob.glob(os.path.join(INGEST_DIR, "digest_*.txt"))
    # Sort files by modification time (newest last)
    files.sort(key=os.path.getmtime)

    if len(files) > MAX_INGESTS:
        files_to_delete = files[:-MAX_INGESTS]
        print(f"Rotating ingests. Deleting {len(files_to_delete)} old file(s)...")
        for f in files_to_delete:
            os.remove(f)
            print(f"Deleted: {f}")
    else:
        print("No rotation needed.")

def main():
    parser = argparse.ArgumentParser(description="Manage codebase ingests.")
    parser.add_argument("--force", action="store_true", help="Force generation regardless of commit count.")
    args = parser.parse_args()

    commit_count = get_commit_count()

    should_run = args.force or (commit_count % MODULO_TRIGGER == 0)

    if should_run:
        trigger_reason = "Force flag set" if args.force else f"Commit #{commit_count} is a multiple of {MODULO_TRIGGER}"
        print(f"Triggering ingest: {trigger_reason}")
        run_gitingest()
        rotate_ingests()
    else:
        print(f"Skipping ingest. Commit #{commit_count} is not a multiple of {MODULO_TRIGGER} (and --force not set).")

if __name__ == "__main__":
    main()
