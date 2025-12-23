# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import unittest
import hashlib
import os
import tempfile
from typing import List
from vtr_standard.poc.merkle import MerkleTree

class TestMerkleCompatibility(unittest.TestCase):
    """
    Tests ensuring the new iterative Merkle Tree implementation produces
    identical results to the legacy recursive logic.
    """

    def _recursive_compute_root(self, leaves: List[str]) -> str:
        """
        The legacy recursive implementation for comparison.
        """
        if not leaves:
            return ""
        if len(leaves) == 1:
            return leaves[0]

        parents = []
        for i in range(0, len(leaves), 2):
            node1 = leaves[i]
            if i + 1 < len(leaves):
                node2 = leaves[i+1]
                combined = node1 + node2
            else:
                combined = node1 + node1

            parents.append(hashlib.sha256(combined.encode()).hexdigest())

        return self._recursive_compute_root(parents)

    def test_merkle_logic_parity(self):
        """
        Generates random leaves and verifies that the new iterative class
        matches the old recursive helper.
        """
        # Create a dummy file to satisfy MerkleTree init
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"dummy_content")
            temp_path = f.name

        try:
            merkle_instance = MerkleTree(temp_path)

            # Test cases with varying number of leaves
            test_cases = [
                [], # Empty
                ["a"], # Single
                ["a", "b"], # Even
                ["a", "b", "c"], # Odd
                [str(i) for i in range(10)], # Larger Even
                [str(i) for i in range(11)], # Larger Odd
                [str(i) for i in range(100)], # Big Even
                [str(i) for i in range(101)], # Big Odd
            ]

            for leaves in test_cases:
                # Calculate using old recursive logic
                expected_root = self._recursive_compute_root(leaves)

                # Calculate using new iterative logic (by injecting leaves directly)
                # We bypass _compute_leaves by calling _compute_root directly
                actual_root = merkle_instance._compute_root(leaves)

                self.assertEqual(
                    actual_root,
                    expected_root,
                    f"Mismatch for leaves: {leaves}"
                )

        finally:
            os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()
