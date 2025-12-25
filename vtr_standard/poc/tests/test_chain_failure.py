
import unittest
import os
import json
import logging
from vtr_standard.poc.vtr_container import VTRContainer
from vtr_standard.poc.schemas import VTRSidecar

# Disable logging for tests
logging.getLogger("vtr_standard.poc.vtr_container").setLevel(logging.CRITICAL)

class TestChainFailure(unittest.TestCase):
    def setUp(self):
        self.video_file = "test_chain_failure_video.mp4"
        with open(self.video_file, "wb") as f:
            f.write(os.urandom(1024))

        self.bad_sidecar = "bad_sidecar.vtr.json"
        with open(self.bad_sidecar, "w") as f:
            json.dump({"broken": "schema"}, f)

    def tearDown(self):
        if os.path.exists(self.video_file):
            os.remove(self.video_file)
        if os.path.exists(self.bad_sidecar):
            os.remove(self.bad_sidecar)
        if os.path.exists(f"{self.video_file}.vtr.json"):
            os.remove(f"{self.video_file}.vtr.json")

    def test_chain_failure_raises_exception(self):
        """Test that linking to an invalid sidecar raises ValueError."""
        container = VTRContainer(self.video_file, "TEST_SENSOR")

        with self.assertRaises(ValueError) as context:
            container.create_sidecar(previous_sidecar_path=self.bad_sidecar)

        self.assertIn("Chain of Custody", str(context.exception) + str(context.exception.__cause__))

    def test_missing_sidecar_raises_exception(self):
        """Test that linking to a non-existent sidecar raises FileNotFoundError."""
        container = VTRContainer(self.video_file, "TEST_SENSOR")

        with self.assertRaises(FileNotFoundError):
            container.create_sidecar(previous_sidecar_path="non_existent.json")

if __name__ == "__main__":
    unittest.main()
