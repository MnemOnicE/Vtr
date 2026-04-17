# VTR Performance Benchmarks

This file tracks the performance improvements and optimizations made to the VTR Standard reference implementation.
Our primary focus is ensuring the system remains high-performance, specifically minimizing memory usage and latency in the core cryptographic paths.

## Merkle Tree Hashing Optimization (V2.2)

### The Problem
During the chunk-based file hashing process (`vtr_standard/poc/merkle.py`), a 4MB chunk was loaded into memory. To ensure cryptographic domain separation, a `b'\x00'` byte was prepended to the chunk before hashing using `hashlib.sha256(b'\x00' + chunk).digest()`. This caused Python to allocate a *new* 4MB byte string in memory for every single chunk, leading to unnecessary memory allocation and garbage collection overhead.

### The Solution
The code was refactored to use the incremental `hashlib.sha256().update()` method, completely eliminating the string allocation overhead.

### Benchmark Results

*Hardware/Environment: Simulated via `tracemalloc` testing core inner loop allocations.*

| Metric | V2.2 Baseline (Concat) | V2.2 Optimized (`.update()`) | Improvement |
| :--- | :--- | :--- | :--- |
| **Peak Memory Allocation per 4MB Chunk** | 4.00 MB | 0.00 MB | **-4.00 MB (100% reduction in allocation overhead)** |

*Note: While wall-clock execution time for hashing a 500MB file remained largely I/O bound (~1.6 seconds in both versions), this optimization drastically reduced peak memory pressure by preventing the redundant 4MB allocation per iteration, ensuring the memory footprint stays flat relative to the chunk size.*
