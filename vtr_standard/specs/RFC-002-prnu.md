# RFC-002: Hardware Root of Trust Logic (PRNU)

**Status:** Draft
**Version:** 0.1

## Abstract

This document describes the mechanism for using Photo Response Non-Uniformity (PRNU) as a hardware root of trust for the Video Truth Record (VTR) protocol.

## PRNU Extraction

Every camera sensor has a unique noise fingerprint due to manufacturing imperfections. This fingerprint, or PRNU, is extracted inside the Trusted Execution Environment (TEE).

## Signing Process

1.  **Capture:** The sensor captures raw video data.
2.  **Extraction:** The TEE extracts the PRNU pattern.
3.  **Key Derivation:** A signing key is derived from the PRNU.
4.  **Signing:** The video hash is signed using this key.
5.  **Zero-Knowledge Proof:** A proof is generated to attest that the signature is valid and corresponds to a known, valid sensor, without revealing the sensor's unique ID.

## Security Considerations

*   **Physical Access:** The security relies on the assumption that the PRNU cannot be cloned without physical access to the sensor.
*   **TEE Integrity:** The extraction and signing must happen within a secure enclave to prevent software-based spoofing.
