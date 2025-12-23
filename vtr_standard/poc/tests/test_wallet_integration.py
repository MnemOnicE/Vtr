import unittest
import os
import json
from vtr_standard.poc.vtr_container import VTRContainer

class TestWalletIntegration(unittest.TestCase):
    def setUp(self):
        # Create a dummy video file
        self.test_video = "test_wallet_video.mp4"
        with open(self.test_video, "wb") as f:
            f.write(b"dummy content")

        # Set environment variables for deterministic MockPRNU
        os.environ["VTR_TEST_LIVENESS"] = "true"
        os.environ["VTR_TEST_GPS"] = "locked"

    def tearDown(self):
        # Clean up files
        if os.path.exists(self.test_video):
            os.remove(self.test_video)

        sidecar_path = f"{self.test_video}.vtr.json"
        if os.path.exists(sidecar_path):
            os.remove(sidecar_path)

        # Unset env vars
        os.environ.pop("VTR_TEST_LIVENESS", None)
        os.environ.pop("VTR_TEST_GPS", None)

    def test_wallet_address_inclusion(self):
        """Test that wallet address is correctly included in economic_data."""
        container = VTRContainer(self.test_video, "SENSOR_TEST")
        wallet = "0x1234567890abcdef"
        container.create_sidecar(wallet_address=wallet)

        sidecar_path = f"{self.test_video}.vtr.json"
        self.assertTrue(os.path.exists(sidecar_path))

        with open(sidecar_path, 'r') as f:
            data = json.load(f)

        self.assertIn("economic_data", data)
        self.assertIsNotNone(data["economic_data"])
        self.assertEqual(data["economic_data"].get("payment_address"), wallet)

    def test_no_wallet_address(self):
        """Test that economic_data is None when no wallet address is provided."""
        container = VTRContainer(self.test_video, "SENSOR_TEST")
        container.create_sidecar()

        sidecar_path = f"{self.test_video}.vtr.json"
        self.assertTrue(os.path.exists(sidecar_path))

        with open(sidecar_path, 'r') as f:
            data = json.load(f)

        self.assertIsNone(data.get("economic_data"))

if __name__ == '__main__':
    unittest.main()
