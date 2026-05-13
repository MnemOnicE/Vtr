# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class VTRConfig:
    """Configuration object for VTR components."""
    kdf_salt: bytes
    kdf_iterations: int = 100000
    test_liveness: Optional[str] = None
    test_gps: Optional[str] = None
    env: str = "DEVELOPMENT"

    @classmethod
    def from_env(cls) -> "VTRConfig":
        """Creates a VTRConfig from environment variables.

        Raises:
            ValueError: If VTR_KDF_SALT is missing or empty.
        """
        env_salt = os.environ.get("VTR_KDF_SALT")
        if not env_salt:
            raise ValueError(
                "CRITICAL SECURITY REQUIREMENT: VTR_KDF_SALT environment variable is missing. "
                "For security, a unique, non-hardcoded salt must be provided for key derivation. "
                "In development/testing, you can set this to a dummy value (e.g., export VTR_KDF_SALT='mock_salt')."
            )

        kdf_salt = env_salt.encode()

        try:
            iterations = max(1, int(os.environ.get("VTR_KDF_ITERATIONS", 100000)))
        except ValueError:
            iterations = 100000

        test_liveness = (os.environ.get("VTR_TEST_LIVENESS") or "").strip() or None
        test_gps = (os.environ.get("VTR_TEST_GPS") or "").strip() or None

        return cls(
            kdf_salt=kdf_salt,
            kdf_iterations=iterations,
            test_liveness=test_liveness,
            test_gps=test_gps,
            env=os.environ.get("VTR_ENV", "DEVELOPMENT").strip().upper()
        )
