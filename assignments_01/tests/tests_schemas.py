import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from weatherkit import WeatherResponse


def test_valid_response_loads_168_entries():
    """Test 1: Valid response validates and has 168 hourly entries.

    Using Path(__file__) is reliable because a plain relative path ("weather_raw.json")
    fails if pytest is run from a different directory than the file location.
    """
    json_path = Path(__file__).parent.parent / "weather_raw.json"
    with open(json_path, "r") as f:
        raw_data = json.load(f)

    weather = WeatherResponse.model_validate(raw_data)
    assert weather.latitude == 35.216976
    assert len(weather.hourly.time) == 168


def test_invalid_latitude_raises_validation_error():
    """Test 2: A latitude of 200.0 raises a ValidationError."""
    invalid_data = {
        "latitude": 200.0,  
        "longitude": -80.0,
        "timezone": "GMT",
        "elevation": 100.0,
        "hourly": {
            "time": ["2026-04-08T00:00"],
            "temperature_2m": [15.0],
            "precipitation": [0.0],
        },
    }
    with pytest.raises(ValidationError):
        WeatherResponse.model_validate(invalid_data)


def test_mismatched_list_lengths_raises_validation_error():
    """Test 3: Mismatched list lengths in HourlyBlock raise a ValidationError."""
    mismatched_data = {
        "latitude": 35.0,
        "longitude": -80.0,
        "timezone": "GMT",
        "elevation": 100.0,
        "hourly": {
            "time": ["2026-04-08T00:00", "2026-04-08T01:00"],
            "temperature_2m": [15.0],  
            "precipitation": [0.0, 0.0],
        },
    }
    with pytest.raises(ValidationError):
        WeatherResponse.model_validate(mismatched_data)


def test_null_temperature_raises_validation_error():
    """Test 4: A null inside temperature_2m raises a ValidationError."""
    null_data = {
        "latitude": 35.0,
        "longitude": -80.0,
        "timezone": "GMT",
        "elevation": 100.0,
        "hourly": {
            "time": ["2026-04-08T00:00"],
            "temperature_2m": [None], 
            "precipitation": [0.0],
        },
    }
    with pytest.raises(ValidationError):
        WeatherResponse.model_validate(null_data)