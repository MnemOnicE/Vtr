import unittest
import os
import shutil
from poc.validator import VTRValidator

class TestValidatorCrash(unittest.TestCase):
    def setUp(self):
        self.validator = VTRValidator()
        self.test_dir = "test_dir_video"
        os.makedirs(self.test_dir, exist_ok=True)
        self.sidecar_path = "test_dir_video.vtr.json"
        with open(self.sidecar_path, "w") as f:
            f.write('{"vtr_version": "2.0", "hardware_signature": {"public_key": "x", "zk_proof": "y", "timestamp": 123, "liveness_flag": true}, "legal_assertions": {}}')

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.sidecar_path):
            os.remove(self.sidecar_path)

    def test_directory_as_video_should_not_crash(self):
        """Test validation when video path is a directory."""
        # This test fails if it raises an exception
        result = self.validator.validate_container(self.test_dir, self.sidecar_path)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "VIDEO_NOT_FOUND")

if __name__ == '__main__':
    unittest.main()
