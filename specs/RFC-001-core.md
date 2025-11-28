# RFC 001: The VTR Sidecar Standard

## Abstract
Defines the JSON structure for the `.vtr` sidecar file, which carries the cryptographic proofs and legal assertions for a media file.

## Metadata Structure
The `trth` box (ISO-BMFF) or sidecar JSON must adhere to:

```json
{
  "vtr_version": "2.0",
  "hardware_signature": {
    "zk_proof": "0x...",           // Zero-Knowledge Proof of PRNU match
    "liveness_flag": true,         // Optical Flow / Moiré check passed
    "timestamp_hash": "GPS_Atomic" // Salted Time Block
  },
  "legal_assertions": {
    "x_vtr_ai_training": false,    // COPYRIGHT TRAP: If false, scraping is a violation
    "royalty_target": "null"       // If true, Smart Contract address here
  },
  "entropy_score": {
    "semantic_score": 88.4,        // Object recognition score (0-100)
    "source_device_tier": "AOSP_Budget"
  }
}
```

## Security Considerations

  * **Rotational Hashing:** The `device_id` MUST be salted with a Time+Location block to prevent tracking users across sessions.
  * **Direct Link:** Implementers SHOULD use Direct CSI-2 links to the TEE to prevent kernel-level injection attacks.
