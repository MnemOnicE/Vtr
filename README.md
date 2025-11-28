# The Video Truth Record (.vtr) Project

**Status:** Proposal / Draft
**Codename:** Witness

## Overview

As generative AI approaches photorealism, the "Signal-to-Noise" ratio of the internet approaches zero. Current verification methods (watermarking, ID verification) are either fragile or dystopian.

The **Video Truth Record (.vtr)** is an open standard for **Hardware-Signed Media Attribution**. It binds video content to a specific hardware sensor (PRNU) at the moment of capture, ensuring the authenticity of "Human-Generated Data" without requiring user identity disclosure.

**Core Principles:**
1.  **Hardware is Truth:** We trust the physics of the sensor, not the logic of the OS.
2.  **Blind Notary:** Verify the "What" (Humanity), protect the "Who" (Identity).
3.  **Innocent Until Proven Wealthy:** Works on budget hardware ("Potato Phones") via high-noise sensors.

## Features

*   **Hardware Root of Trust:** Uses Photo Response Non-Uniformity (PRNU) to uniquely identify camera sensors.
*   **Zero-Knowledge Proofs (ZKP):** Validates authenticity without revealing the raw unique sensor ID.
*   **Liveness Detection:** Simulates checks for 3D parallax and other patterns to prevent "replay" attacks or recording screens.
*   **Legal Assertions:** Embeds meta-tags regarding AI training consent (e.g., DMCA Sec 1202).

## Repository Structure

The repository is organized as follows:

*   `/vtr-standard`: The main project directory containing the standard definitions and reference implementation.
    *   `/whitepaper`: The full "Seth Protocol" master plan and economic model.
    *   `/specs`: The technical Request For Comments (RFC) documents defining the standard.
    *   `/poc`: Python proof-of-concept for the metadata container and verification logic (Reference Implementation).
    *   `/docs`: Documentation files.
*   `/poc`: A standalone Proof of Concept implementation (simplified).

## Installation & Setup

### Prerequisites

*   Python 3.6 or higher.

### Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/vtr-project.git
cd vtr-project
```

No external dependencies are required for the Proof of Concept (POC) as it uses the Python standard library.

## Usage Guide

You can run the Proof of Concept using either the standalone script or the package within `vtr-standard`.

### Running the Standalone POC

To run the simplified proof-of-concept script:

```bash
python3 -m poc.vtr_container
```

### Running the Standard Reference POC

To run the reference implementation in `vtr-standard`:

```bash
python3 -m vtr-standard.poc.vtr_container
```

### Output

The script will generate a `.vtr.json` sidecar file (e.g., `protest_footage.mp4.vtr.json`) in the same directory. This file contains:

*   **vtr_version**: The version of the VTR standard used.
*   **hardware_signature**:
    *   `zk_proof`: A simulated Zero-Knowledge Proof hash.
    *   `liveness_flag`: Result of the liveness check.
    *   `timestamp`: Time of capture.
*   **legal_assertions**:
    *   `x_vtr_ai_training`: Boolean flag for AI training consent.
    *   `note`: Legal note regarding data usage.

## API Documentation

### `poc.vtr_container`

Main module for handling VTR containers.

*   `VTRContainer`: Class to manage video and sensor association.
    *   `create_sidecar(allow_ai_training=False)`: Generates the JSON sidecar.

### `poc.mock_prnu`

Module for simulating hardware sensor logic.

*   `MockPRNU`: Class simulating the hardware root of trust.
    *   `generate_zk_proof(video_path, timestamp)`: Creates a simulated cryptographic proof.
    *   `check_liveness()`: Simulates liveness checks (e.g., 3D depth).

## Contributing

This is an open standard. We welcome contributions from engineers, cryptographers, and privacy advocates.

*See `CONTRIBUTING.md` for the "Poison Pill" anti-forking rules.*

## License

This project uses a custom 'Hardware-GPL' license. Please refer to the license file for details.
