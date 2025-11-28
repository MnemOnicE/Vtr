# RFC 002: The Hardware Root of Trust (PRNU)

## Abstract
This document defines the specification for extracting and utilizing Photo Response Non-Uniformity (PRNU) as a hardware root of trust within the Video Truth Record (.vtr) protocol.

## 1. Introduction
Photo Response Non-Uniformity (PRNU) is a unique pattern of noise present in every digital image sensor due to manufacturing imperfections. This pattern acts as a "silicon fingerprint" or "Silicon DNA" that cannot be cloned or forged without physical possession of the sensor.

## 2. PRNU Extraction Mechanism
Implementations MUST extract the PRNU fingerprint within a Trusted Execution Environment (TEE).

### 2.1. Extraction Process
1.  **Raw Capture:** The sensor captures a series of flat-field frames (uniform illumination).
2.  **Noise Isolation:** The TEE isolates the fixed pattern noise from the random shot noise and dark current.
3.  **Fingerprint Generation:** A high-frequency noise map is generated and stored securely within the TEE's secure storage.

### 2.2. Security Requirements
*   **Direct CSI-2 Link:** The image data MUST flow directly from the Camera Serial Interface (CSI-2) to the TEE, bypassing the main Operating System (OS) memory to prevent interception or injection (e.g., "Rooted Android" attacks).
*   **Secure Storage:** The extracted PRNU fingerprint MUST never leave the TEE in plaintext.

## 3. Signing Protocol
When a video is recorded, the device must generate a cryptographic signature binding the content to the hardware.

### 3.1. Key Derivation
A private signing key is derived from the PRNU fingerprint. This ensures that the key is intrinsic to the hardware.

### 3.2. Signature Generation
1.  **Hash Generation:** A cryptographic hash of the video stream is calculated.
2.  **Signing:** The TEE signs the video hash using the PRNU-derived private key.
3.  **Output:** The resulting signature is embedded in the `.vtr` sidecar or `trth` box.

## 4. Verification
Verification relies on matching the noise pattern in the media file against the known PRNU fingerprint (or a ZK-Proof of it) of the claiming device.

### 4.1. Security Model
*   **Unclonability:** Because the private key is derived from physical defects, it cannot be exported or copied to another device.
*   **Physical Possession:** To forge a signature, an attacker must physically possess the specific sensor.

## 5. Budget Hardware Considerations
Low-cost sensors often exhibit higher magnitudes of PRNU ("louder" noise). This standard leverages this characteristic, making budget devices ("Potato Phones") potentially more secure and easier to verify than high-end devices with aggressive noise reduction algorithms.
