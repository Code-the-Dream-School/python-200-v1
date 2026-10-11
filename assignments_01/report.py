import json
from pathlib import Path
from weatherkit import DailyAggregator, WeatherResponse, to_readings


def main():
    """Main execution pipeline for weatherkit reporting."""
    # 1. Load weather_raw.json using a reliable path
    json_path = Path(__file__).parent / "weather_raw.json"
    with open(json_path, "r") as f:
        raw_data = json.load(f)

    # 2. Validate into WeatherResponse
    weather = WeatherResponse.model_validate(raw_data)

    # 3. Convert to HourlyReading objects
    readings = to_readings(weather)

    # 4. Aggregate to DailySummary objects
    aggregator = DailyAggregator(min_hours=24)
    summaries = aggregator.summarize(readings)
    dropped_days = aggregator.incomplete_days(readings)

    # 5. Print a readable table
    print(
        f"{'Date':<12} | {'High (°C)':<10} | {'Low (°C)':<10} | {'Precip (mm)':<12} | {'Range (°C)':<10}"
    )
    print("-" * 65)
    for summary in summaries:
        print(
            f"{summary.date:<12} | {summary.temp_max:<10.1f} | {summary.temp_min:<10.1f} | {summary.precipitation_sum:<12.1f} | {summary.temp_range():<10.1f}"
        )

    # 6. Print a warning line listing incomplete days that were dropped
    if dropped_days:
        print(f"\n⚠️ Warning: The following incomplete days were dropped: {', '.join(dropped_days)}")


# If we omitted the if __name__ == "__main__": guard, anyone who imported
# report.py into another script (e.g., to reuse a helper function) would inadvertently
# trigger this entire main() execution script as soon as the module is imported.
if __name__ == "__main__":
    main()



# TASL 7
# 1. Rejecting vs. Tolerating Nulls:
#    - Rejecting the whole file is ideal for safety-critical pipelines (like aviation 
#      or severe storm warnings) where missing sensor data could cause dangerous 
#      miscalculations. Conversely, you would tolerate gaps in climate research or 
#      long-term trend analysis where dropping a single hour is negligible compared 
#      to losing an entire week of data. To tolerate nulls in Pydantic, you could 
#      change the type annotation to `Optional[float] = None` and filter them out 
#      during conversion or aggregation.
#
# 2. Aggregating at Noon:
#    - If a pipeline runs at noon, today's data is only half complete (e.g., 12 hours 
#      instead of 24). With min_hours=24, today would fail validation and be silently 
#      dropped or missing. `incomplete_days()` helps by explicitly auditing and revealing 
#      *why* it was dropped, ensuring nothing disappears without a trace so you know 
#      it's just an incomplete day rather than a missing database record.
#
# 3. Benefits of Packaging in Week 10:
#    - Writing weatherkit as a package makes it modular and reusable. In Week 10, when 
#      building a larger application or pipeline, you can simply write 
#      `from weatherkit import DailyAggregator` anywhere in your project workspace 
#      without duplicating code, maintaining clean separation of concerns and 
#      centralized test coverage.