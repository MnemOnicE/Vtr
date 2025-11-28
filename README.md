# The Video Truth Record (.vtr) Project

**Status:** Proposal / Draft
**Codename:** Witness

## 1. The Problem
As generative AI approaches photorealism, the "Signal-to-Noise" ratio of the internet approaches zero. Current verification methods (watermarking, ID verification) are either fragile or dystopian.

## 2. The Solution
The **Video Truth Record (.vtr)** is an open standard for **Hardware-Signed Media Attribution**.
It binds video content to a specific hardware sensor (PRNU) at the moment of capture, ensuring the authenticity of "Human-Generated Data" without requiring user identity disclosure.

**Core Principles:**
1.  **Hardware is Truth:** We trust the physics of the sensor, not the logic of the OS.
2.  **Blind Notary:** Verify the "What" (Humanity), protect the "Who" (Identity).
3.  **Innocent Until Proven Wealthy:** Works on budget hardware ("Potato Phones") via high-noise sensors.

## 3. Repository Structure
* `/whitepaper`: The full "Seth Protocol" master plan and economic model.
* `/specs`: The technical Request For Comments (RFC) documents defining the standard.
* `/poc`: Python proof-of-concept for the metadata container and verification logic.

### Quick Start (POC)
To run the proof-of-concept script and generate a sample `.vtr.json` sidecar:

```bash
python3 -m poc.vtr_container
```

## 4. Contributing
This is an open standard. We welcome contributions from engineers, cryptographers, and privacy advocates.
*See `CONTRIBUTING.md` for the "Poison Pill" anti-forking rules.*
