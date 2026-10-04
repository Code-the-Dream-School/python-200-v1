"""Print daily summaries from the supplied local weather file."""

import json
from pathlib import Path
from weatherkit import DailyAggregator, WeatherResponse, to_readings


def main() -> None:
    """Load, validate, summarize, and display observations."""
    path = Path(__file__).parent / "weather_raw.json"
    response = WeatherResponse.model_validate(json.loads(path.read_text()))
    readings = to_readings(response)
    aggregator = DailyAggregator()
    print(f"Latitude: {response.latitude} | Timezone: {response.timezone}")
    print(f"Hourly observations: {len(readings)}")
    print("Date          High C   Low C   Rain mm   Range C   Hours")
    for day in aggregator.summarize(readings):
        print(
            f"{day.date}  {day.temp_max:8.1f} {day.temp_min:7.1f} "
            f"{day.precipitation_sum:9.1f} {day.temp_range():9.1f} "
            f"{day.hours_observed:7d}"
        )
    dropped = aggregator.incomplete_days(readings)
    if dropped:
        print(f"Warning: incomplete days dropped: {', '.join(dropped)}")


# Without this guard, importing report would load data and print the table.
if __name__ == "__main__":
    main()

# Reflection draft: review these choices before submitting.
# Reject nulls when a model needs every measurement. A monitoring dashboard
# could keep gaps instead: use list[float | None], then handle missing values
# in conversion and aggregation without treating them as zero.
# At noon, today's data has fewer than 24 hours, so today is dropped.
# incomplete_days() makes the missing date visible instead of hiding it.
# A later pipeline can import to_readings and DailyAggregator directly.
