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

    def test_random_gps_salt(self):
        """Verify that GPS salt is random when VTR_TEST_GPS is not set."""
        from unittest.mock import patch
        with patch.dict(os.environ):
            os.environ.pop("VTR_TEST_GPS", None)

            prnu1 = MockPRNU("sensor_1")
            prnu2 = MockPRNU("sensor_1")

            self.assertNotEqual(prnu1.gps_salt, prnu2.gps_salt)
            self.assertEqual(len(prnu1.gps_salt), 32) # hex of 16 bytes

if __name__ == "__main__":
    unittest.main()
