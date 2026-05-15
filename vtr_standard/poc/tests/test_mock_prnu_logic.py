import unittest
from vtr_standard.poc.mock_prnu import MockPRNU
import os

class TestMockPRNU(unittest.TestCase):
    def test_proof_generation_and_verification(self):
        # Create a dummy video file
        with open("test.mp4", "wb") as f:
            f.write(b"video data")

        prnu = MockPRNU("sensor_123")
        ts = 1234567890.0
        lf = True
        lbh = "lbh_hash"
        n = "nonce_123"
        ps = "prev_sig"

        proof = prnu.generate_zk_proof("test.mp4", ts, lf, lbh, n, ps)
        self.assertTrue(proof.startswith("zk_snark_"))

        pk = prnu.get_public_key()
        is_valid = MockPRNU.verify_zk_proof(pk, "test.mp4", ts, proof, lf, lbh, n, ps)
        self.assertTrue(is_valid)

        # Cleanup
        os.remove("test.mp4")

    def test_check_liveness_random(self):
        """Verifies that check_liveness returns a boolean when env var is unset."""
        # Ensure VTR_TEST_LIVENESS is not in environment
        old_liveness = os.environ.pop("VTR_TEST_LIVENESS", None)
        try:
            prnu = MockPRNU("sensor_123")
            result = prnu.check_liveness()
            self.assertIsInstance(result, bool)
            # Run multiple times to ensure both outcomes are possible (50% probability each)
            results = {prnu.check_liveness() for _ in range(100)}
            self.assertEqual(results, {True, False})
        finally:
            # Restore environment
            if old_liveness is not None:
                os.environ["VTR_TEST_LIVENESS"] = old_liveness

    def test_static_hash_video_content(self):
        """Verifies _static_hash_video_content returns a valid 64-char hex string."""
        import tempfile
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".mp4", delete=False) as tmp:
            tmp.write(b"dummy video data for hashing test")
            test_file = tmp.name
        try:
            hash_result = MockPRNU._static_hash_video_content(test_file)

            self.assertIsInstance(hash_result, str)
            self.assertEqual(len(hash_result), 64)
            # Verify it's a valid hex string
            int(hash_result, 16)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
    def test_check_liveness_env_var(self):
        """Verifies check_liveness respects VTR_TEST_LIVENESS env var explicitly."""
        from unittest.mock import patch

        prnu = MockPRNU("sensor_123")

        # Truthy cases (case-insensitive)
        truthy_values = ["true", "1", "pass", "TRUE", "Pass", " true ", " pass\n"]
        for val in truthy_values:
            with patch.dict(os.environ, {"VTR_TEST_LIVENESS": val}):
                self.assertTrue(prnu.check_liveness(), f"Expected True for '{val}'")

        # Falsy and edge cases
        falsy_values = ["false", "0", "fail", "random", "", " false "]
        for val in falsy_values:
            with patch.dict(os.environ, {"VTR_TEST_LIVENESS": val}):
                self.assertFalse(prnu.check_liveness(), f"Expected False for '{val}'")

    def test_location_block_hash_logic(self):
        """Tests that location block hash is deterministic and configurable."""
        from unittest.mock import patch

        sensor_id = "sensor_123"

        # 1. Test Default Stability
        prnu1 = MockPRNU(sensor_id)
        hash1 = prnu1.calculate_location_block_hash()
        self.assertEqual(len(hash1), 64, "Hash should be 64-char hex string (SHA256)")

        prnu2 = MockPRNU(sensor_id)
        self.assertEqual(hash1, prnu2.calculate_location_block_hash(), "Hash should be deterministic")

        # 2. Test VTR_TEST_GPS override
        custom_gps = "40.7128,-74.0060" # NYC
        with patch.dict(os.environ, {"VTR_TEST_GPS": custom_gps}):
            prnu_nyc = MockPRNU(sensor_id)
            hash_nyc = prnu_nyc.calculate_location_block_hash()
            self.assertNotEqual(hash1, hash_nyc, "Hash should change with VTR_TEST_GPS override")

            # Verify consistency for same override
            prnu_nyc_2 = MockPRNU(sensor_id)
            self.assertEqual(hash_nyc, prnu_nyc_2.calculate_location_block_hash())

        # 3. Test KDF Binding (VTR_KDF_SALT)
        # The location hash is derived using the same KDF salt as the public key.
        with patch.dict(os.environ, {"VTR_KDF_SALT": "new_security_salt_2025"}):
            MockPRNU._get_kdf_params.cache_clear()
        MockPRNU._get_kdf_params.cache_clear()
        MockPRNU._derive_pbkdf2.cache_clear()
        with patch.dict(os.environ, {"VTR_KDF_SALT": "new_security_salt_2025"}, clear=True):
            prnu_salted = MockPRNU(sensor_id)
            hash_salted = prnu_salted.calculate_location_block_hash()
            self.assertNotEqual(hash1, hash_salted, "Hash should change with VTR_KDF_SALT override")
        MockPRNU._get_kdf_params.cache_clear()

if __name__ == "__main__":
    unittest.main()
