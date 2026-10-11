from dataclasses import dataclass
from .schemas import WeatherResponse

@dataclass
class HourlyReading:
    """Represents a single hour's weather reading, including timestamp, temperature, and precipitation."""
    timestamp: str
    temperature_c: float
    precipitation_mm: float

def to_readings(response: WeatherResponse) -> list[HourlyReading]:
    """Converting columnar hourly into a list HourlyReading per hour."""
    readings = []
    total_hours = len(response.hourly.time)

    for i in range(total_hours):
        reading = HourlyReading(
        timestamp=response.hourly.time[i],
        temperature_c=response.hourly.temperature_2m[i],
        precipitation_mm=response.hourly.precipitation[i],
    )
        readings.append(reading)

    return readings
