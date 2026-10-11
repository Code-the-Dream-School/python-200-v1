from weatherkit.records import to_readings, HourlyReading
import pytest
from weatherkit.schemas import WeatherResponse
import json
from pathlib import Path

with open(Path(__file__).parent.parent / "weather_raw.json", 'r') as file:
        weather_raw = json.load(file)

test_response = WeatherResponse.model_validate(weather_raw)
hourly_list = to_readings(test_response)

def test_one_reading_check():
    """test that to_readings returns one reading per hour"""
    assert test_response.hourly.time[0] == hourly_list[0].timestamp
    assert test_response.hourly.time[-1] == hourly_list[-1].timestamp


def test_index_match():
    """his test catches the case where readings are paired with the wrong timestamps."""
    i=1
    assert hourly_list[i].timestamp == test_response.hourly.time[i]
    assert hourly_list[i].temperature_c == test_response.hourly.temperature_2m[i]
    assert hourly_list[i].precipitation_mm == test_response.hourly.precipitation[i]
        
def test_equal_data():
     """Two HourlyReading objects with identical fields compare equal."""
     hourlyreading_a = HourlyReading(timestamp='2026-04-13T10:00', temperature_c=13.6, precipitation_mm=0.0)
     hourlyreading_b = HourlyReading(timestamp='2026-04-13T10:00', temperature_c=13.6, precipitation_mm=0.0)
     assert hourlyreading_a == hourlyreading_b