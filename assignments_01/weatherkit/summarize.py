from dataclasses import dataclass
from collections import defaultdict
from .records import HourlyReading


@dataclass
class DailySummary:
    date: str
    temp_max: float
    temp_min: float
    precipitation_sum: float
    hours_observed: int

    def temp_range(self) -> float:
        return self.temp_max - self.temp_min


class DailyAggregator:
    def __init__(self, min_hours: int = 24):
        self.min_hours = min_hours

    def _group_by_date(
        self, readings: list[HourlyReading]
    ) -> dict[str, list[HourlyReading]]:
        """Helper method to group hourly readings by their YYYY-MM-DD date key."""
        grouped = defaultdict(list)
        for reading in readings:
            date_key = reading.timestamp[:10]
            grouped[date_key].append(reading)
        return grouped

    def summarize(self, readings: list[HourlyReading]) -> list[DailySummary]:
        """Groups hourly readings by date and returns summaries for complete days.

        Days with fewer than min_hours observations are dropped.
        """
        grouped = self._group_by_date(readings)
        summaries = []

        # Sort dates to ensure chronological order
        for date_key in sorted(grouped.keys()):
            day_readings = grouped[date_key]
            hours = len(day_readings)

            # Drop days that don't meet the min_hours threshold
            if hours < self.min_hours:
                continue

            temps = [r.temperature_c for r in day_readings]
            precip = sum(r.precipitation_mm for r in day_readings)

            summaries.append(
                DailySummary(
                    date=date_key,
                    temp_max=max(temps),
                    temp_min=min(temps),
                    precipitation_sum=precip,
                    hours_observed=hours,
                )
            )

        return summaries

    def incomplete_days(self, readings: list[HourlyReading]) -> list[str]:
        """Returns a list of date strings for days that had fewer than min_hours observations."""
        grouped = self._group_by_date(readings)
        dropped_dates = []

        for date_key in sorted(grouped.keys()):
            if len(grouped[date_key]) < self.min_hours:
                dropped_dates.append(date_key)

        return dropped_dates