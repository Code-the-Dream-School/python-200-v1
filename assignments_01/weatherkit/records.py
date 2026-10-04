"""Internal weather records."""

from dataclasses import dataclass
from .schemas import WeatherResponse


@dataclass
class HourlyReading:
    """One timestamp with temperature in Celsius and precipitation in mm."""

    timestamp: str
    temperature_c: float
    precipitation_mm: float


# WeatherResponse checks outside data. These records use that checked input.
def to_readings(response: WeatherResponse) -> list[HourlyReading]:
    """Convert parallel columns into ordered records.

    Args:
        response: A validated weather response.

    Returns:
        One reading per timestamp, in input order.
    """
    hourly = response.hourly
    return [
        HourlyReading(timestamp, temperature, precipitation)
        for timestamp, temperature, precipitation in zip(
            hourly.time, hourly.temperature_2m, hourly.precipitation, strict=True
        )
    ]
