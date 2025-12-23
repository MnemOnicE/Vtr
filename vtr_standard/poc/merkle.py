# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import hashlib
from typing import List

class MerkleTree:
    """
    A simple implementation of a Merkle Tree for video file integrity.
    """

    def __init__(self, file_path: str, chunk_size: int = 1024 * 1024):
        """
        Initialize the Merkle Tree by reading the file and computing the root.
        """
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.leaves = self._compute_leaves()
        self.root = self._compute_root(self.leaves)

    def _compute_leaves(self) -> List[str]:
        """Reads the file in chunks and computes SHA256 hash for each chunk."""
        hashes = []
        with open(self.file_path, 'rb') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                hashes.append(hashlib.sha256(chunk).hexdigest())

        if not hashes:
            return [hashlib.sha256(b"").hexdigest()]

        return hashes

    def _compute_root(self, leaves: List[str]) -> str:
        """Iteratively computes the Merkle Root from a list of hashes."""
        current_level = leaves
        if not current_level:
            return ""

        while len(current_level) > 1:
            parents = []
            for i in range(0, len(current_level), 2):
                node1 = current_level[i]
                node2 = current_level[i+1] if i + 1 < len(current_level) else node1
                combined = node1 + node2
                parents.append(hashlib.sha256(combined.encode()).hexdigest())
            current_level = parents

        return current_level[0]

    def get_root(self) -> str:
        """Returns the hexadecimal Merkle Root."""
        return self.root
