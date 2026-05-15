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

if __name__ == "__main__":
    unittest.main()
