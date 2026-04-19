
import unittest
import os
import json
import sys
from unittest.mock import MagicMock
try:
    import pydantic
except ImportError:
    class MockBaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    setattr(self, k, MockBaseModel(**v))
                else:
                    setattr(self, k, v)
        @classmethod
        def model_validate(cls, data):
            return cls(**data)
        def model_dump_json(self, **kwargs):
            import json
            def default(obj):
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                return str(obj)
            return json.dumps(self.__dict__, default=default)

    mock_pydantic = MagicMock()
    mock_pydantic.BaseModel = MockBaseModel
    mock_pydantic.Field = MagicMock(return_value=None)
    mock_pydantic.ValidationError = Exception
    sys.modules["pydantic"] = mock_pydantic

import logging
from vtr_standard.poc.vtr_container import VTRContainer
from vtr_standard.poc.config import VTRConfig

# Disable logging for tests
logging.getLogger("vtr_standard.poc.vtr_container").setLevel(logging.CRITICAL)

class TestChainFailure(unittest.TestCase):
    def setUp(self):
        os.environ["VTR_KDF_SALT"] = "test_chain_salt"
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
        if "VTR_KDF_SALT" in os.environ:
            del os.environ["VTR_KDF_SALT"]

    def test_chain_failure_raises_exception(self):
        """Test that linking to an invalid sidecar raises ValueError."""


        container = VTRContainer(self.video_file, "TEST_SENSOR", VTRConfig(kdf_salt=b"test_salt"))

        with self.assertRaises(ValueError) as context:
            container.create_sidecar(previous_sidecar_path=self.bad_sidecar)

        # The bad_sidecar has invalid schema, which gets caught and re-raised as "Chain of Custody Failure: ..."
        self.assertIn("Chain of Custody Failure:", str(context.exception))
        self.assertIn("INVALID_SCHEMA:", str(context.exception))




    def test_missing_sidecar_raises_exception(self):
        """Test that linking to a non-existent sidecar raises FileNotFoundError."""
        container = VTRContainer(self.video_file, "TEST_SENSOR", VTRConfig(kdf_salt=b"test_salt"))
        missing_path = "non_existent.json"

        with self.assertRaises(ValueError) as context:
            container.create_sidecar(previous_sidecar_path=missing_path)

        self.assertIn("SIDECAR_NOT_FOUND:", str(context.exception))


    def test_invalid_json_sidecar_raises_exception(self):
        """Test that linking to a sidecar with invalid JSON raises ValueError."""
        container = VTRContainer(self.video_file, "TEST_SENSOR", VTRConfig(kdf_salt=b"test_salt"))

        # Create an invalid JSON sidecar
        invalid_json_sidecar = "invalid_json.vtr.json"
        with open(invalid_json_sidecar, "w") as f:
            f.write("{ invalid json format ")

        try:
            with self.assertRaises(ValueError) as context:
                container.create_sidecar(previous_sidecar_path=invalid_json_sidecar)

            self.assertIn("INVALID_JSON:", str(context.exception))
        finally:
            if os.path.exists(invalid_json_sidecar):
                os.remove(invalid_json_sidecar)

if __name__ == "__main__":
    unittest.main()
