import unittest
from unittest.mock import patch
import os
import random
from vtr_standard.poc.mock_prnu import MockPRNU

class TestMockPRNU(unittest.TestCase):
    def setUp(self):
        os.environ["VTR_KDF_SALT"] = "test_logic_salt"

    def tearDown(self):
        if "VTR_KDF_SALT" in os.environ:
            del os.environ["VTR_KDF_SALT"]

    def test_proof_generation_and_verification(self):
        # Create a dummy video file
        with open("test.mp4", "wb") as f:
            f.write(b"video data")

        try:
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
        finally:
            # Cleanup
            if os.path.exists("test.mp4"):
                os.remove("test.mp4")

    def test_check_liveness_logic(self):
        with patch.dict(os.environ, {"VTR_ENV": "TESTING"}):
            prnu = MockPRNU("sensor_123")

        # 1. Test environment variable overrides (True cases)
        true_values = ["true", "1", "pass", "TRUE", "Pass", "TrUe"]
        for val in true_values:
            with patch.dict(os.environ, {"VTR_TEST_LIVENESS": val}):
                self.assertTrue(
                    prnu.check_liveness(),
                    f"check_liveness should return True for VTR_TEST_LIVENESS='{val}'"
                )

        # 2. Test environment variable overrides (False cases)
        false_values = ["false", "0", "fail", "random", ""]
        for val in false_values:
            with patch.dict(os.environ, {"VTR_TEST_LIVENESS": val}):
                self.assertFalse(
                    prnu.check_liveness(),
                    f"check_liveness should return False for VTR_TEST_LIVENESS='{val}'"
                )

        # 3. Test fallback logic when env var is not set
        # Ensure env var is absent
        with patch.dict(os.environ):
            os.environ.pop("VTR_TEST_LIVENESS", None)
            # We must also ensure other required env vars for MockPRNU init are present if needed,
            # but here we already have the prnu instance.
            # However, check_liveness reads os.environ directly.

            with patch("random.uniform") as mock_uniform:
                # Threshold in mock_prnu.py is 0.9
                # Case A: liveness_score > 0.9
                mock_uniform.return_value = 0.91
                self.assertTrue(prnu.check_liveness())
                self.assertTrue(prnu.check_liveness())
                self.assertEqual(mock_uniform.call_count, 1)
                mock_uniform.assert_called_with(0.8, 1.0)

                # Case B: liveness_score <= 0.9
                mock_uniform.return_value = 0.89
                self.assertFalse(prnu.check_liveness())

                # Case C: Boundary condition
                mock_uniform.return_value = 0.9
                self.assertFalse(prnu.check_liveness())

    def test_random_gps_salt(self):
        """Verify that GPS salt is random when VTR_TEST_GPS is not set."""
        if "VTR_TEST_GPS" in os.environ:
            del os.environ["VTR_TEST_GPS"]

        prnu1 = MockPRNU("sensor_1")
        prnu2 = MockPRNU("sensor_1")

        self.assertNotEqual(prnu1.gps_salt, prnu2.gps_salt)
        self.assertEqual(len(prnu1.gps_salt), 32) # hex of 16 bytes

if __name__ == "__main__":
    unittest.main()
