# OntoLogics - The Logic of Reality

**Manifesto**

We are entering the "Post-Truth Era," where generative AI makes visual evidence indistinguishable from fabrication. Current solutions (watermarking) are fragile; current regulatory attempts (moderation) are expensive failures.

OntoLogics provides the infrastructure for reality.

## The Video Truth Record (.vtr)

The Video Truth Record is a new open standard that inverts the model. Instead of detecting fakes, we cryptographically authenticate reality at the point of capture. By leveraging the physical entropy of camera sensors (Silicon DNA) and a decentralized settlement layer, we create a "Chain of Custody" that protects truth, preserves privacy, and monetizes human-generated data.

### Mission

*   **Hardware is Truth:** Software can lie; physics cannot. We trust the sensor's imperfections.
*   **Privacy by Design:** Proof of Humanity must not require Proof of Identity.
*   **Innocent Until Proven Wealthy:** Security for budget devices ("Potato Phone") as well as flagships.
*   **Data is Labor:** Users deserve a dividend for high-quality training data.

## Repository Structure

*   `whitepaper/`: The Master Plan and detailed technical specifications.
*   `specs/`: RFCs defining the core container and PRNU logic.
*   `poc/`: Proof of Concept Python code for generating hardware-signed sidecars.
*   `docs/`: Economic models and legal frameworks.

## Installation & Setup

### Prerequisites

*   Python 3.6 or higher.

### Installation

No external dependencies are required for the Proof of Concept (POC) as it uses the Python standard library.

## Usage

The Proof of Concept (POC) provides a Command Line Interface (CLI) to sign and verify video files.

> **⚠️ WARNING:** The POC runs in **Mock Sensor Mode**. It uses simulated hardware roots of trust and is for demonstration purposes only.

### Sign a Video

Generate a VTR sidecar (`.vtr.json`) for a video file:

```bash
python3 -m vtr_standard.poc.cli sign my_video.mp4
```

Options:
*   `--sensor-id <ID>`: Simulate a specific sensor ID (e.g., `DEVICE_123`).
*   `--allow-ai`: Flag to allow your data to be used for AI training.
*   `--link-to <PATH>`: Path to a previous sidecar to create a "Chain of Custody" link.

### Verify a Video

Verify the integrity and authenticity of a VTR container:

```bash
python3 -m vtr_standard.poc.cli verify my_video.mp4
```

This checks:
1.  **File Integrity:** Merkle Tree hashing of the video content.
2.  **Signature Validity:** Cryptographic verification of the ZK proof.
3.  **Schema Compliance:** Ensures the sidecar matches V2.0 specs.

### Legacy Demo

To run the automated internal demo script:

```bash
python3 -m vtr_standard.poc.vtr_container
```

## License

This project is licensed under the **VTR Public License (VTR-PL)**, a reciprocal license designed to protect the integrity of human-generated media. See `LICENSE.md` for details.

---
*Records, then beer.*
