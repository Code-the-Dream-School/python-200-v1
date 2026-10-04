"""Validate incoming weather data."""

from typing import Self
from pydantic import BaseModel, Field, model_validator


class HourlyBlock(BaseModel):
    """Parallel hourly timestamps, Celsius temperatures, and rain in mm."""

    time: list[str]
    temperature_2m: list[float]
    precipitation: list[float]

    @model_validator(mode="after")
    def check_lengths(self) -> Self:
        """Keep each timestamp paired with its measurements."""
        if not len(self.time) == len(self.temperature_2m) == len(self.precipitation):
            raise ValueError("hourly lists must have the same length")
        return self


class WeatherResponse(BaseModel):
    """Weather metadata and validated hourly observations."""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str
    elevation: float
    hourly: HourlyBlock
