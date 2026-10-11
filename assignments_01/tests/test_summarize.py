from weatherkit.summarize import DailySummary, DailyAggregator
from weatherkit.records import to_readings, HourlyReading
import pytest
#tests/test_summarize.py -- at least five tests. Use a @pytest.fixture for shared input.
#1.Grouping works: a hand-built list spanning two dates produces two summaries.
#2.temp_max and temp_min are correct for a known small input.
#3.precipitation_sum adds up correctly. Use pytest.approx.
#4,A day with fewer than min_hours readings is dropped, and its date appears in incomplete_days().
#5.Lowering min_hours causes that same day to be kept -- proving the parameter is actually consulted rather than ignored.
#At least one test must use @pytest.mark.parametrize.
@pytest.fixture
def sample_readings():
    """sample readings for testing"""
    return [
        HourlyReading(timestamp='2026-04-08T02:00', temperature_c=13.4, precipitation_mm=5.7),
        HourlyReading(timestamp='2026-04-08T03:00', temperature_c=12.1, precipitation_mm=1.201),
        HourlyReading(timestamp='2026-04-08T04:00', temperature_c=12.0, precipitation_mm=4.0),
        HourlyReading(timestamp='2026-04-09T10:00', temperature_c=4.2, precipitation_mm=0.0),
        HourlyReading(timestamp='2026-04-09T11:00', temperature_c=3.7, precipitation_mm=0.0)
    ]
# 1
def test_list_to_summaries(sample_readings):
    """test a number of entries produce the same number of summaries"""
    daily_agg = DailyAggregator(min_hours=2)
    test_summary = daily_agg.summarize(sample_readings)
    assert len(test_summary) == 2

# 2
@pytest.mark.parametrize(
        "index, max_temp, min_temp",
        [
            (0, 13.4, 12.0),
            (1, 4.2, 3.7)
        ]
)     
def test_temp_values(sample_readings,index,max_temp,min_temp):
    """test the values for temp_max and temp_min are correct"""
    daily_agg = DailyAggregator(min_hours=2)
    test_summary = daily_agg.summarize(sample_readings)
    assert test_summary[index].temp_max == max_temp
    assert test_summary[index].temp_min == min_temp

# 3
def test_precipitation_sum_value(sample_readings):
    """test if the precipitation sum value is correct"""
    daily_agg = DailyAggregator(min_hours=2)
    test_summary = daily_agg.summarize(sample_readings)
    assert test_summary[0].precipitation_sum == pytest.approx(10.901)

# 4 
def test_incomplete_days(sample_readings):
    """test the program drop the incomplete days and return them in a list"""
    daily_agg = DailyAggregator(min_hours=3)
    test_summary = daily_agg.summarize(sample_readings)
    incomplete_days_list = daily_agg.incomplete_days(sample_readings)
    assert test_summary[0].date == '2026-04-08'
    assert incomplete_days_list[0] == '2026-04-09'

# 5

def test_min_hours_effectiveness(sample_readings):
    """test the parameter is working in class DailyAggregator"""
    daily_agg = DailyAggregator(min_hours=2)
    test_result = daily_agg.incomplete_days(sample_readings)
    assert len(test_result) == 0

# broke the DailyAggregator.incomplete_days function by changing the < to a > in the min_days comparison.
# two tests caught this, 4 and 5