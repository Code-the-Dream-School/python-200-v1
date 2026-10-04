"""Check column-to-record pairing."""

import pytest
from weatherkit import HourlyReading, WeatherResponse, to_readings


@pytest.fixture
def response():
    return WeatherResponse(
        latitude=35, longitude=-80, timezone="GMT", elevation=250,
        hourly={
            "time": ["2026-05-01T00:00", "2026-05-01T01:00", "2026-05-01T02:00"],
            "temperature_2m": [12, 15, 9], "precipitation": [0.1, 0.2, 0],
        },
    )


def test_count_and_order(response):
    readings = to_readings(response)
    assert len(readings) == 3
    assert readings[0].timestamp == response.hourly.time[0]
    assert readings[-1].timestamp == response.hourly.time[-1]


def test_values_keep_their_index(response):
    for index, reading in enumerate(to_readings(response)):
        assert reading.timestamp == response.hourly.time[index]
        assert reading.temperature_c == response.hourly.temperature_2m[index]
        assert reading.precipitation_mm == response.hourly.precipitation[index]


def test_equal_records_compare_equal():
    assert HourlyReading("2026-05-01T00:00", 12, 0) == HourlyReading("2026-05-01T00:00", 12, 0)


def test_empty_response_has_no_readings(response):
    response.hourly.time.clear()
    response.hourly.temperature_2m.clear()
    response.hourly.precipitation.clear()
    assert to_readings(response) == []
