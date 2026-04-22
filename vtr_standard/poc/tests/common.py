# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0 (the "License").
# A copy of the License is available in the root/vtr_standard/poc/LICENSE file.
# This code is distributed WITHOUT ANY WARRANTY.

import sys
from unittest.mock import MagicMock

def setup_pydantic_mock():
    """Sets up a robust, shared mock for Pydantic if it's not installed."""
    try:
        import pydantic
        return pydantic
    except ImportError:
        pass

    # If already mocked, return it
    if "pydantic" in sys.modules and not isinstance(sys.modules["pydantic"], MagicMock):
        # This shouldn't happen if we only use this helper, but being safe
        return sys.modules["pydantic"]

    class MockBaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    setattr(self, k, MockBaseModel(**v))
                else:
                    setattr(self, k, v)

        @classmethod
        def model_validate(cls, data):
            # Simulation of required field validation using __annotations__ if present
            # Accessing from the mock_pydantic which will have been populated by the subclasses in schemas.py
            if hasattr(cls, "__annotations__"):
                for field_name in cls.__annotations__:
                    if field_name not in data and not hasattr(cls, field_name):
                        # Pydantic v2 raises ValidationError
                        # We use the MockValidationError class defined below
                        raise mock_pydantic.ValidationError(f"Mock Validation Error: {field_name} is required")
            return cls(**data)

        def model_dump(self):
            def _dump(obj):
                if hasattr(obj, "__dict__"):
                    return {k: _dump(v) for k, v in obj.__dict__.items()}
                return obj
            return _dump(self)

        def model_dump_json(self, **kwargs):
            import json
            return json.dumps(self.model_dump(), **kwargs)

        @classmethod
        def model_json_schema(cls):
            # Minimal mock for model_json_schema
            schema = {
                "title": cls.__name__,
                "type": "object",
                "properties": {},
                "required": []
            }
            if hasattr(cls, "__annotations__"):
                for field_name in cls.__annotations__:
                    schema["properties"][field_name] = {"type": "string"} # Crude
                    if not hasattr(cls, field_name):
                        schema["required"].append(field_name)
            return schema

    # ValidationError mock
    class MockValidationError(Exception):
        @classmethod
        def from_exception_data(cls, title, input_data):
            return cls(f"{title}: {input_data}")
        def errors(self):
            return [{"msg": str(self)}]

    mock_pydantic = MagicMock()
    mock_pydantic.BaseModel = MockBaseModel
    mock_pydantic.ValidationError = MockValidationError

    # Simple Field mock
    def mock_field(*args, **kwargs):
        return None
    mock_pydantic.Field = mock_field

    sys.modules["pydantic"] = mock_pydantic
    return mock_pydantic
