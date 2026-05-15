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
            # Run multiple times to ensure both outcomes are possible (50% probability each)
            results = {prnu.check_liveness() for _ in range(100)}
            self.assertEqual(results, {True, False})
        finally:
            # Restore environment
            if old_liveness is not None:
                os.environ["VTR_TEST_LIVENESS"] = old_liveness
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
            prnu_salted = MockPRNU(sensor_id)
            hash_salted = prnu_salted.calculate_location_block_hash()
            self.assertNotEqual(hash1, hash_salted, "Hash should change with VTR_KDF_SALT override")

if __name__ == "__main__":
    unittest.main()
