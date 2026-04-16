import unittest
from vtr_standard.poc.mock_prnu import MockPRNU
import os

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

if __name__ == "__main__":
    unittest.main()
