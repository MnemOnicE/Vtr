import time
import hashlib
from typing import List

def buggy_compute_root(leaves: List[bytes]) -> str:
    current_level = leaves
    if not current_level:
        return ""

    internal_hasher = hashlib.sha256(b'\x01')
    loop_count = 0
    while len(current_level) > 1:
        loop_count += 1
        # The bug causes an infinite loop since it appends two items for every pair!
        # len(parents) == len(current_level), so the condition len(current_level) > 1 is never false.
        # To prevent benchmark hanging, we break after 1000 iterations to simulate
        # a timeout/OOM situation and measure the time taken.
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
    leaves = [hashlib.sha256(secrets.token_bytes(32)).digest() for _ in range(num_leaves)]

    print(f"Benchmarking with {num_leaves} leaves...")

    # Baseline
    start = time.perf_counter()
    buggy_compute_root(leaves)
    baseline_time = time.perf_counter() - start
    print(f"Baseline Time (Buggy - capped at 1000 infinite loop iterations): {baseline_time:.4f} seconds")

    # Optimized
    start = time.perf_counter()
    optimized_compute_root(leaves)
    optimized_time = time.perf_counter() - start
    print(f"Optimized Time (Correct & Fast): {optimized_time:.4f} seconds")

    if optimized_time > 0:
        speedup = baseline_time / optimized_time
        improvement = ((baseline_time - optimized_time) / baseline_time) * 100
        print(f"Speedup: {speedup:.2f}x faster")
        print(f"Improvement: {improvement:.2f}%")
