# Project Roadmap

## 🚀 Active Features
- [ ] (None)

## 📅 Planned

### 1. Advancing the Core Technology (From PoC to Production)
- [ ] **High-Performance Implementation (Rust or C++)**: Port the core cryptographic and PRNU extraction logic to Rust or C++ for better performance and memory safety, while maintaining the Python API using bindings (e.g., PyO3 for Rust).
- [ ] **Zero-Knowledge Proofs (ZKPs) for Privacy**: Integrate ZK-SNARKs or ZK-STARKs to allow mathematical proof that an image matches a sensor's fingerprint without revealing the actual PRNU data, preventing spoofing attacks.

### 2. Decentralization & Ledger Integration
- [ ] **Data Availability & Anchoring**: Anchor Merkle roots of VTR containers to a high-throughput blockchain (e.g., Solana), Layer-2 rollup, or a dedicated Data Availability (DA) layer (e.g., Celestia) for immutable timestamping.
- [ ] **Decentralized Storage**: Formalize support for storing large VTR container payloads (bundled media and proofs) on decentralized networks like IPFS or Arweave, storing only hashes/URIs in the VTR standard (Future RFC).

### 3. Ecosystem & Standardization
- [ ] **Conformance Test Suite**: Create a language-agnostic "Conformance Test Vector" repository with pre-calculated dummy images, PRNU signatures, and valid/invalid containers for developers building VTR clients in Go, TypeScript, Swift, etc.
- [ ] **Hardware Enclave (TEE) Support**: Draft RFC-003 to include specifications for extracting and signing data directly within a device's Trusted Execution Environment (e.g., Apple Secure Enclave, ARM TrustZone) to provide hardware-signed attestation combined with PRNU matches.

## ✅ Completed
- [x] Operation Hard Truth (Security Hardening: Decouple Economics)
- [x] Standard Wallet Integration (Replacing 'Invisible Wallet')
