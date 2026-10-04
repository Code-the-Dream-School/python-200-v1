"""Check daily results and incomplete-day handling."""

import json
from pathlib import Path
import pytest
from weatherkit import DailyAggregator, HourlyReading, WeatherResponse, to_readings


@pytest.fixture
def readings():
    # Unsorted input makes ordering bugs visible.
    return [
        HourlyReading("2026-05-02T00:00", 20, 0.4),
        HourlyReading("2026-05-01T01:00", 15, 0.2),
        HourlyReading("2026-05-01T00:00", 9, 0.1),
    ]


def test_grouping_and_sorting(readings):
    days = DailyAggregator(min_hours=1).summarize(readings)
    assert [day.date for day in days] == ["2026-05-01", "2026-05-02"]
    assert [day.hours_observed for day in days] == [2, 1]


def test_high_and_low(readings):
    day = DailyAggregator(min_hours=1).summarize(readings)[0]
    assert day.temp_max == 15
    assert day.temp_min == 9
    assert day.temp_range() == pytest.approx(6)


def test_precipitation_total(readings):
    day = DailyAggregator(min_hours=1).summarize(readings)[0]
    assert day.precipitation_sum == pytest.approx(0.3)


def test_short_day_is_reported_as_dropped(readings):
    aggregator = DailyAggregator(min_hours=2)
    assert [day.date for day in aggregator.summarize(readings)] == ["2026-05-01"]
    assert aggregator.incomplete_days(readings) == ["2026-05-02"]


@pytest.mark.parametrize("minimum,expected_count", [(1, 2), (2, 1), (3, 0), (24, 0)])
def test_minimum_is_used(readings, minimum, expected_count):
    assert len(DailyAggregator(minimum).summarize(readings)) == expected_count


def test_lowering_minimum_keeps_short_day(readings):
    aggregator = DailyAggregator(min_hours=1)
    assert len(aggregator.summarize(readings)) == 2
    assert aggregator.incomplete_days(readings) == []


def test_empty_input():
    aggregator = DailyAggregator()
    assert aggregator.summarize([]) == []
    assert aggregator.incomplete_days([]) == []


@pytest.mark.parametrize("minimum", [0, -1])
def test_invalid_minimum_raises(minimum):
    with pytest.raises(ValueError, match="min_hours must be positive"):
        DailyAggregator(minimum)


def test_supplied_data_self_check():
    path = Path(__file__).parent.parent / "weather_raw.json"
    response = WeatherResponse.model_validate(json.loads(path.read_text()))
    days = DailyAggregator().summarize(to_readings(response))
    assert len(days) == 7
    assert [(day.date, day.temp_max, day.temp_min, day.precipitation_sum, day.hours_observed)
            for day in days[:2]] == [
        ("2026-04-08", 16.8, 7.8, 0.0, 24),
        ("2026-04-09", 19.3, 3.7, 0.0, 24),
    ]

# Addition in temp_range made test_high_and_low fail: 24 vs 6.
# Restored subtraction after checking the failure.
