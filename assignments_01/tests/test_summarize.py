import pytest
from weatherkit import DailyAggregator, DailySummary, HourlyReading


@pytest.fixture
def sample_readings():
    """Fixture providing a controlled set of hourly readings spanning two dates."""
    readings = []
    # 24 hours for Day 1
    for hour in range(24):
        readings.append(
            HourlyReading(
                timestamp=f"2026-04-08T{hour:02d}:00",
                temperature_c=10.0 + (hour % 5),
                precipitation_mm=0.0,
            )
        )
    # 24 hours for Day 2
    for hour in range(24):
        readings.append(
            HourlyReading(
                timestamp=f"2026-04-09T{hour:02d}:00",
                temperature_c=15.0 + (hour % 3),
                precipitation_mm=1.0 if hour == 12 else 0.0,
            )
        )
    return readings


def test_grouping_produces_two_summaries(sample_readings):
    """Test 1: Grouping a list spanning two dates produces two summaries."""
    aggregator = DailyAggregator(min_hours=24)
    summaries = aggregator.summarize(sample_readings)
    assert len(summaries) == 2
    assert summaries[0].date == "2026-04-08"
    assert summaries[1].date == "2026-04-09"


def test_temp_max_and_min_are_correct(sample_readings):
    """Test 2: temp_max and temp_min correctly calculated."""
    aggregator = DailyAggregator(min_hours=24)
    summaries = aggregator.summarize(sample_readings)
    # Day 1 temperatures range from 10.0 to 14.0 based on (10.0 + (hour % 5))
    assert summaries[0].temp_min == 10.0
    assert summaries[0].temp_max == 14.0


def test_precipitation_sum_adds_up(sample_readings):
    """Test 3: precipitation_sum adds up correctly using pytest.approx."""
    aggregator = DailyAggregator(min_hours=24)
    summaries = aggregator.summarize(sample_readings)
    # Day 2 has a single 1.0mm hour
    assert summaries[1].precipitation_sum == pytest.approx(1.0)


def test_incomplete_day_is_dropped_and_tracked():
    """Test 4: A day with fewer than min_hours is dropped and appears in incomplete_days()."""
    # Create only 6 hours of data for a single day
    short_readings = [
        HourlyReading(
            timestamp=f"2026-04-10T{h:02d}:00",
            temperature_c=12.0,
            precipitation_mm=0.0,
        )
        for h in range(6)
    ]
    aggregator = DailyAggregator(min_hours=24)
    summaries = aggregator.summarize(short_readings)
    dropped = aggregator.incomplete_days(short_readings)

    assert len(summaries) == 0
    assert "2026-04-10" in dropped


@pytest.mark.parametrize("threshold", [6, 12, 24])
def test_lowering_min_hours_keeps_day(threshold):
    """Test 5: Lowering min_hours causes a short day to be kept (parametrized)."""
    short_readings = [
        HourlyReading(
            timestamp=f"2026-04-10T{h:02d}:00",
            temperature_c=12.0,
            precipitation_mm=0.0,
        )
        for h in range(12)  # 12 hours total
    ]
    # If min_hours is 12 or 6, it should be kept. If 24, it should be dropped.
    aggregator = DailyAggregator(min_hours=threshold)
    summaries = aggregator.summarize(short_readings)

    if threshold <= 12:
        assert len(summaries) == 1
    else:
        assert len(summaries) == 0