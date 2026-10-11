import json
from pathlib import Path
from weatherkit import HourlyReading, WeatherResponse, to_readings


def test_to_readings_preserves_order_and_count():
    """Test 1: to_readings returns one reading per hour in correct order."""
    json_path = Path(__file__).parent.parent / "weather_raw.json"
    with open(json_path, "r") as f:
        weather = WeatherResponse.model_validate(json.load(f))

    readings = to_readings(weather)
    assert len(readings) == 168
    assert readings[0].timestamp == weather.hourly.time[0]
    assert readings[-1].timestamp == weather.hourly.time[-1]


def test_reading_indices_match_precisely():
    """Test 2: Ensure reading fields match index i of input lists (no shifting)."""
    json_path = Path(__file__).parent.parent / "weather_raw.json"
    with open(json_path, "r") as f:
        weather = WeatherResponse.model_validate(json.load(f))

    readings = to_readings(weather)
    for i, r in enumerate(readings):
        assert r.timestamp == weather.hourly.time[i]
        assert r.temperature_c == weather.hourly.temperature_2m[i]
        assert r.precipitation_mm == weather.hourly.precipitation[i]


def test_hourly_reading_equality():
    """Test 3: Two HourlyReading objects with identical fields compare equal."""
    r1 = HourlyReading(
        timestamp="2026-04-08T00:00", temperature_c=12.5, precipitation_mm=0.0
    )
    r2 = HourlyReading(
        timestamp="2026-04-08T00:00", temperature_c=12.5, precipitation_mm=0.0
    )
    assert r1 == r2