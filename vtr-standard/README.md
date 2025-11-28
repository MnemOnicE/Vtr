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

The Proof of Concept (POC) demonstrates how to generate a VTR sidecar file for a video.

Run the Proof of Concept generator:

```bash
python3 -m vtr-standard.poc.vtr_container
```

This will produce a `.vtr.json` file (e.g., `protest_footage.mp4.vtr.json`) containing the simulated cryptographic proofs.

### API Reference

#### `vtr_standard.poc.vtr_container`

Main module for handling VTR containers.

*   `VTRContainer`: Class to manage video and sensor association.
    *   `create_sidecar(allow_ai_training=False)`: Generates the JSON sidecar.
    *   `_generate_zk_proof()`: (Internal) Simulates ZK proof generation.
    *   `_check_liveness()`: (Internal) Simulates liveness checks.

## License

This project is licensed under the **VTR Public License (VTR-PL)**, a reciprocal license designed to protect the integrity of human-generated media. See `LICENSE.md` for details.

---
*Records, then beer.*
