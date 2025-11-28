# RFC-001: Core VTR Container Specification

**Status:** Draft
**Version:** 0.1

## Abstract

This document defines the structure and encoding of the Video Truth Record (VTR) sidecar file. The VTR sidecar is a JSON-formatted file containing cryptographic signatures, metadata, and legal assertions that bind a video file to the hardware sensor that captured it.

## File Format

The sidecar file MUST use the `.vtr.json` extension. It MUST be encoded in UTF-8.

## Schema

```json
{
  "vtr_version": "2.0",
  "hardware_signature": {
    "zk_proof": "<string>",
    "liveness_flag": <boolean>,
    "timestamp": <float>,
    "location_block_hash": "<string>"
  },
  "legal_assertions": {
    "x_vtr_ai_training": <boolean>,
    "copyright_notice": "<string>"
  },
  "economic_data": {
    "semantic_score": <float>,
    "device_tier": "<string>"
  }
}
```

## Fields

*   `vtr_version`: The version of the VTR standard.
*   `hardware_signature`: Contains the cryptographic proofs.
    *   `zk_proof`: A Zero-Knowledge Proof verifying the sensor signature.
    *   `liveness_flag`: Indicates if passive liveness checks passed.
    *   `timestamp`: The Unix timestamp of capture.
    *   `location_block_hash`: A hash of the location data (salted).
*   `legal_assertions`:
    *   `x_vtr_ai_training`: Usage flag for AI training.
    *   `copyright_notice`: Legal text.
*   `economic_data`:
    *   `semantic_score`: Assessment of data value.
    *   `device_tier`: Classification of the capture device.
