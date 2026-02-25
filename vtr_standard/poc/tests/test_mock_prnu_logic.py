import unittest
import os
import tempfile
from vtr_standard.poc.mock_prnu import MockPRNU

class TestMockPRNU(unittest.TestCase):
    def test_proof_generation_and_verification(self):
        # Use a temporary file to avoid polluting the filesystem and ensure cleanup.
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".mp4") as f:
            test_file_path = f.name
            f.write(b"video data")

        try:
            prnu = MockPRNU("sensor_123")
            timestamp = 1234567890.0
            liveness_flag = True
            location_block_hash = "lbh_hash"
            nonce = "nonce_123"
            previous_signature = "prev_sig"

            proof = prnu.generate_zk_proof(
                video_path=test_file_path,
                timestamp=timestamp,
                liveness_flag=liveness_flag,
                location_block_hash=location_block_hash,
                nonce=nonce,
                previous_signature=previous_signature
            )
            self.assertTrue(proof.startswith("zk_snark_"))

            public_key = prnu.get_public_key()
            is_valid = MockPRNU.verify_zk_proof(
                public_key=public_key,
                video_path=test_file_path,
                timestamp=timestamp,
                zk_proof=proof,
                liveness_flag=liveness_flag,
                location_block_hash=location_block_hash,
                nonce=nonce,
                previous_signature=previous_signature
            )
            self.assertTrue(is_valid)
        finally:
            os.remove(test_file_path)

if __name__ == "__main__":
    unittest.main()
