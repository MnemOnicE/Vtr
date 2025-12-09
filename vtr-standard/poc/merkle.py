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
        try:
            with open(self.file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    hashes.append(hashlib.sha256(chunk).hexdigest())
        except FileNotFoundError:
            return [hashlib.sha256(b"MISSING_FILE").hexdigest()]

        if not hashes:
            return [hashlib.sha256(b"").hexdigest()]

        return hashes

    def _compute_root(self, leaves: List[str]) -> str:
        """Recursively computes the Merkle Root from a list of hashes."""
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

        return self._compute_root(parents)

    def get_root(self) -> str:
        """Returns the hexadecimal Merkle Root."""
        return self.root
