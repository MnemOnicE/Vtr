import unittest
import hashlib
import os
from vtr_standard.poc.mock_prnu import MockPRNU

class TestKDFStrength(unittest.TestCase):
    def test_public_key_is_not_simple_hash(self):
        sensor_id = "test_sensor_123"
        simple_hash = hashlib.sha256(sensor_id.encode()).hexdigest()

        prnu = MockPRNU(sensor_id)
        derived_pk = prnu.get_public_key()

        self.assertNotEqual(derived_pk, simple_hash, "Public key should not be a simple SHA256 hash of the sensor ID")
        self.assertEqual(len(derived_pk), 64, "Public key should be a 64-character hex string (SHA256)")

    def test_location_hash_is_not_simple_hash(self):
        gps_salt = "34.0522,118.2437"
        os.environ["VTR_TEST_GPS"] = gps_salt
        try:
            simple_hash = hashlib.sha256(gps_salt.encode()).hexdigest()

            prnu = MockPRNU("test_sensor")
            derived_lh = prnu.calculate_location_block_hash()

            self.assertNotEqual(derived_lh, simple_hash, "Location hash should not be a simple SHA256 hash of the GPS salt")
            self.assertEqual(len(derived_lh), 64, "Location hash should be a 64-character hex string (SHA256)")
        finally:
            del os.environ["VTR_TEST_GPS"]

    def test_kdf_is_deterministic(self):
        sensor_id = "deterministic_sensor"
        prnu1 = MockPRNU(sensor_id)
        prnu2 = MockPRNU(sensor_id)

        self.assertEqual(prnu1.get_public_key(), prnu2.get_public_key(), "KDF must be deterministic for the same sensor ID")

    def test_kdf_config_via_env_vars(self):
        sensor_id = "config_sensor"

        # Original keys
        prnu_default = MockPRNU(sensor_id)
        pk_default = prnu_default.get_public_key()

        # Keys with custom salt
        os.environ["VTR_KDF_SALT"] = "custom_salt"
        prnu_custom_salt = MockPRNU(sensor_id)
        pk_custom_salt = prnu_custom_salt.get_public_key()
        self.assertNotEqual(pk_default, pk_custom_salt)

        # Keys with custom iterations
        os.environ["VTR_KDF_ITERATIONS"] = "1000"
        prnu_custom_iter = MockPRNU(sensor_id)
        pk_custom_iter = prnu_custom_iter.get_public_key()
        self.assertNotEqual(pk_custom_salt, pk_custom_iter)

        # Cleanup
        del os.environ["VTR_KDF_SALT"]
        del os.environ["VTR_KDF_ITERATIONS"]

if __name__ == "__main__":
    unittest.main()
