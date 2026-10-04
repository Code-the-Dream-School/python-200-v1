"""Group hourly observations into daily summaries."""

from dataclasses import dataclass
from .records import HourlyReading


@dataclass
class DailySummary:
    """Daily temperatures in Celsius, rain in mm, and observation count."""

    date: str
    temp_max: float
    temp_min: float
    precipitation_sum: float
    hours_observed: int

    def temp_range(self) -> float:
        """Return high minus low in Celsius."""
        return self.temp_max - self.temp_min


class DailyAggregator:
    """Report days meeting a minimum observation count."""

    def __init__(self, min_hours: int = 24) -> None:
        """Set the minimum readings needed to keep a day."""
        if min_hours < 1:
            raise ValueError("min_hours must be positive")
        self.min_hours = min_hours

    @staticmethod
    def _group(readings: list[HourlyReading]) -> dict[str, list[HourlyReading]]:
        """Group by the date shown in each timestamp."""
        groups: dict[str, list[HourlyReading]] = {}
        for reading in readings:
            groups.setdefault(reading.timestamp[:10], []).append(reading)
        return groups

    def summarize(self, readings: list[HourlyReading]) -> list[DailySummary]:
        """Return complete daily summaries sorted by date."""
        summaries = []
        for date, hours in sorted(self._group(readings).items()):
            if len(hours) < self.min_hours:
                continue
            summaries.append(DailySummary(
                date=date,
                temp_max=max(hour.temperature_c for hour in hours),
                temp_min=min(hour.temperature_c for hour in hours),
                precipitation_sum=sum(hour.precipitation_mm for hour in hours),
                hours_observed=len(hours),
            ))
        return summaries

    def incomplete_days(self, readings: list[HourlyReading]) -> list[str]:
        """Return sorted dates with too few observations."""
        return [
            date for date, hours in sorted(self._group(readings).items())
            if len(hours) < self.min_hours
        ]
