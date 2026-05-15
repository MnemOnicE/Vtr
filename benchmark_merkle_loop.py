"""
Benchmark suite for Merkle tree inner loop optimizations.

This module provides focused micro-benchmarks to compare the execution
time of the baseline (buggy) Merkle root computation against the optimized
O(N) version. It simulates an input of cryptographic hashes to observe
the exponential growth bug in isolation without requiring actual file I/O.
"""

import time
import hashlib
from typing import List


def buggy_compute_root(leaves: List[bytes]) -> str:
    """
    Computes a Merkle root simulating the original buggy implementation.

    This function intentionally includes a logical bug where it appends
    two nodes per iteration, creating an exponential growth of elements
    that causes an infinite loop. It serves strictly as a performance
    baseline.

    Args:
        leaves: A list of byte arrays representing the leaf hashes.

    Returns:
        The computed root hash as a hex string.
    """
    current_level = leaves
    if not current_level:
        return ""

    internal_hasher = hashlib.sha256(b'\x01')
    loop_count = 0
    while len(current_level) > 1:
        loop_count += 1
        # The bug causes an infinite loop since it appends two
        # items for every pair. We cap at 1000 loop counts.
        if loop_count > 1000:
            break

        parents = []
        for i in range(0, len(current_level), 2):
            node1 = current_level[i]
            node2 = current_level[i+1] if i + 1 < len(current_level) else node1

            h = internal_hasher.copy()
            h.update(node1)
            h.update(node2)
            parents.append(h.digest())
            combined = node1 + node2
            parents.append(hashlib.sha256(b'\x01' + combined).digest())
        current_level = parents

    return current_level[0].hex()


def optimized_compute_root(leaves: List[bytes]) -> str:
    """
    Computes the Merkle root using the optimized O(N) spatial mapping.

    This function iteratively processes leaf nodes in pairs to compute
    the root hash correctly by dropping redundant appends and byte
    concatenations found in the baseline implementation.

    Args:
        leaves: A list of byte arrays representing the leaf hashes.

    Returns:
        The computed root hash as a hex string.
    """
    current_level = leaves
    if not current_level:
        return ""

    internal_hasher = hashlib.sha256(b'\x01')
    while len(current_level) > 1:
        parents = []
        for i in range(0, len(current_level), 2):
            node1 = current_level[i]
            node2 = current_level[i+1] if i + 1 < len(current_level) else node1

            h = internal_hasher.copy()
            h.update(node1)
            h.update(node2)
            parents.append(h.digest())
        current_level = parents
    return current_level[0].hex()


if __name__ == "__main__":
    import secrets

    num_leaves = 1000
    leaves = [
        hashlib.sha256(secrets.token_bytes(32)).digest()
        for _ in range(num_leaves)
    ]

    print(f"Benchmarking with {num_leaves} leaves...")

    # Baseline
    start = time.perf_counter()
    buggy_compute_root(leaves)
    baseline_time = time.perf_counter() - start
    print(
        f"Baseline Time (Buggy, capped at 1000 iterations): "
        f"{baseline_time:.4f}s"
    )

    # Optimized
    start = time.perf_counter()
    optimized_compute_root(leaves)
    optimized_time = time.perf_counter() - start
    print(f"Optimized Time (Correct & Fast): {optimized_time:.4f}s")

    if optimized_time > 0:
        speedup = baseline_time / optimized_time
        improvement = ((baseline_time - optimized_time) / baseline_time) * 100
        print(f"Speedup: {speedup:.2f}x faster")
        print(f"Improvement: {improvement:.2f}%")
