"""Check the data boundary."""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from weatherkit import HourlyBlock, WeatherResponse


@pytest.fixture
def payload():
    """A small response with distinct measurements."""
    return {
        "latitude": 35.0, "longitude": -80.0, "timezone": "GMT", "elevation": 250,
        "hourly": {
            "time": ["2026-05-01T00:00", "2026-05-01T01:00", "2026-05-01T02:00"],
            "temperature_2m": [12.0, 15.0, 9.0],
            "precipitation": [0.1, 0.2, 0.0],
        },
    }


def test_real_response_validates():
    # A plain relative path depends on where the command was started.
    path = Path(__file__).parent.parent / "weather_raw.json"
    response = WeatherResponse.model_validate(json.loads(path.read_text()))
    assert len(response.hourly.time) == 168


@pytest.mark.parametrize("field,value", [("latitude", 200.0), ("longitude", -181.0)])
def test_bad_coordinates_raise(payload, field, value):
    payload[field] = value
    with pytest.raises(ValidationError, match=field):
        WeatherResponse.model_validate(payload)


def test_mismatched_lists_raise(payload):
    payload["hourly"]["precipitation"].pop()
    with pytest.raises(ValidationError, match="same length"):
        WeatherResponse.model_validate(payload)


def test_null_temperature_raises(payload):
    payload["hourly"]["temperature_2m"][1] = None
    with pytest.raises(ValidationError) as error:
        WeatherResponse.model_validate(payload)
    assert error.value.errors()[0]["loc"] == ("hourly", "temperature_2m", 1)


def test_empty_columns_validate():
    block = HourlyBlock(time=[], temperature_2m=[], precipitation=[])
    assert block.time == []
