# The Video Truth Record (.vtr) Project

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-VTR--PL-red?style=flat-square)
![Status](https://img.shields.io/badge/Status-Proposal%20%2F%20Draft-orange?style=flat-square)
![Pydantic](https://img.shields.io/badge/Powered%20by-Pydantic-e92063?style=flat-square&logo=pydantic&logoColor=white)
![Code Style](https://img.shields.io/badge/Code%20Style-Google-blue?style=flat-square)

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

*   `/vtr_standard`: The main project directory containing the standard definitions and reference implementation.
    *   `/whitepaper`: The full "Seth Protocol" master plan and economic model.
    *   `/specs`: The technical Request For Comments (RFC) documents defining the standard.
    *   `/poc`: Python proof-of-concept for the metadata container and verification logic (Reference Implementation).
    *   `/docs`: Documentation files.

## Installation & Setup

### Prerequisites

*   Python 3.8 or higher.

### Installation

Clone the repository and install the package:

```bash
git clone https://github.com/ontologics/vtr-standard.git
cd vtr-standard
pip install .
```

This will install the required dependencies (including `pydantic`).

## Usage Guide

### Running the CLI

The Proof of Concept provides a Command Line Interface (CLI) to sign and verify video files.

> **⚠️ WARNING:** The POC runs in **Mock Sensor Mode**. It uses simulated hardware roots of trust and is for demonstration purposes only.

#### Sign a Video

Generate a VTR sidecar (`.vtr.json`) for a video file:

```bash
python3 -m vtr_standard.poc.cli sign my_video.mp4
```

Options:
*   `--sensor-id <ID>`: Simulate a specific sensor ID (e.g., `DEVICE_123`).
*   `--allow-ai`: Flag to allow your data to be used for AI training.
*   `--link-to <PATH>`: Path to a previous sidecar to create a "Chain of Custody" link.

#### Verify a Video

Verify the integrity and authenticity of a VTR container:

```bash
python3 -m vtr_standard.poc.cli verify my_video.mp4
```

This checks:
1.  **File Integrity:** Merkle Tree hashing of the video content.
2.  **Signature Validity:** Cryptographic verification of the ZK proof.
3.  **Schema Compliance:** Ensures the sidecar matches V2.0 specs.

## API Documentation

### `vtr_standard.poc.vtr_container`

Main module for handling VTR containers.

*   `VTRContainer`: Class to manage video and sensor association.
    *   `create_sidecar(allow_ai_training=False)`: Generates the JSON sidecar.

### `vtr_standard.poc.mock_prnu`

Module for simulating hardware sensor logic.

*   `MockPRNU`: Class simulating the hardware root of trust.
    *   `generate_zk_proof(video_path, timestamp)`: Creates a simulated cryptographic proof.
    *   `check_liveness()`: Simulates liveness checks (e.g., 3D depth).

## Contributing

This is an open standard. We welcome contributions from engineers, cryptographers, and privacy advocates.

*See `CONTRIBUTING.md` for the "Poison Pill" anti-forking rules.*

## License

This project is licensed under the **VTR Public License (VTR-PL)**, a reciprocal license designed to protect the integrity of human-generated media. See `LICENSE` for details.
