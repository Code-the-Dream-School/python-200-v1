"""Week 1 practice: records, validation, and tests."""

from dataclasses import FrozenInstanceError, dataclass, field
from typing import Self
import pytest
from pydantic import BaseModel, Field, ValidationError, model_validator


# --- Classes ---
# Q1
class Thermometer:
    """Celsius readings from one location."""

    def __init__(self, location: str, readings: list[float] | None = None) -> None:
        self.location = location
        self.readings = list(readings) if readings is not None else []

    def add(self, reading: float) -> None:
        """Save one reading."""
        self.readings.append(reading)

    def average(self) -> float | None:
        """Return the mean, or None when empty."""
        # Without this check, an empty list would cause division by zero.
        return sum(self.readings) / len(self.readings) if self.readings else None

    def hottest(self) -> float | None:
        """Return the highest reading, or None when empty."""
        return max(self.readings) if self.readings else None

    # Q2
    def __repr__(self) -> str:
        return (f"Thermometer(location={self.location!r}, "
                f"n_readings={len(self.readings)}, average={self.average()!r})")


# The default repr shows a type and address, not the readings we need to debug.
# Q3
class TemperatureAlert:
    """A reusable Celsius threshold."""

    def __init__(self, threshold: float = 30.0) -> None:
        self.threshold = threshold

    def breaches(self, thermometer: Thermometer) -> list[float]:
        """Return readings strictly above the threshold."""
        return [value for value in thermometer.readings if value > self.threshold]


# Store the threshold once, then reuse the same alert for twenty thermometers.
# --- Dataclasses, Type Hints, and Docstrings ---
# Q1 and Q2
@dataclass(frozen=True)
class Station:
    """A station's identifier, coordinates in degrees, and elevation in meters."""

    station_id: str
    name: str
    latitude: float
    longitude: float
    elevation: float


# Dataclass equality compares fields. The original class compared identity.
# Frozen fields cannot be reassigned. These hashable fields also allow sets.
# Q3
@dataclass
class StationBatch:
    """Stations grouped by region."""

    region: str
    stations: list[Station] = field(default_factory=list)

    def add(self, station: Station) -> None:
        """Add one station."""
        self.stations.append(station)

    def highest(self) -> Station | None:
        """Return the highest station, or None when empty."""
        return max(self.stations, key=lambda station: station.elevation, default=None)


# A default factory gives each batch its own list instead of sharing one.
# --- Pydantic ---
# Q1
class Reading(BaseModel):
    """One station reading in Celsius and percent humidity."""

    station_id: str = Field(min_length=3)
    timestamp: str
    temperature_c: float = Field(ge=-90, le=60)
    humidity: float = Field(ge=0, le=100)

    # Q4
    @model_validator(mode="after")
    def check_sensor(self) -> Self:
        """Reject the specified sensor-failure combination."""
        if self.humidity == 0.0 and self.temperature_c < -40:
            raise ValueError("sensor failure: dry reading below -40 C")
        return self


# Field checks individual values; this rule compares two fields together.
# Q2: Numeric strings can be parsed as floats; descriptive words cannot.
# Q3: Three errors together let us fix the whole input in one pass.
# --- pytest ---
# Q1
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32


def test_celsius_to_fahrenheit():
    assert celsius_to_fahrenheit(0) == 32
    assert celsius_to_fahrenheit(100) == 212
    assert celsius_to_fahrenheit(37) == pytest.approx(98.6)


# approx allows tiny floating-point rounding differences.
# Q2
def mean(values: list[float]) -> float:
    """Return the mean; reject an empty list."""
    if not values:
        raise ValueError("cannot average an empty list")
    return sum(values) / len(values)


def test_mean_of_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        mean([])


# match checks the reason too, so an unrelated ValueError won't pass.
# Q3
@pytest.mark.parametrize("values,expected", [([8], 8), ([2, 4], 3), ([-6, -2], -4), ([-3, 0, 3], 0)])
def test_mean_values(values, expected):
    assert mean(values) == pytest.approx(expected)


# One test body keeps the cases consistent and easier to extend.
# Q4: Actual failure output and the final summary are recorded below.


def test_empty_thermometer():
    thermometer = Thermometer("Porch")
    assert thermometer.average() is None
    assert thermometer.hottest() is None


def test_readings_are_not_shared():
    first = Thermometer("Porch")
    second = Thermometer("Garden")
    first.add(12)
    assert second.readings == []
    source = [10.0]
    third = Thermometer("Kitchen", source)
    third.add(20)
    assert source == [10.0]


def test_alert_excludes_threshold():
    thermometer = Thermometer("Porch", [29, 30, 31])
    assert TemperatureAlert().breaches(thermometer) == [31]


def test_batches_are_separate_and_find_highest():
    first = StationBatch("East")
    second = StationBatch("West")
    assert first.highest() is None
    low = Station("LOW", "Valley", 35, -80, 100)
    high = Station("HIGH", "Hill", 36, -81, 400)
    first.add(low)
    first.add(high)
    assert first.highest() == high
    assert second.stations == []


@pytest.mark.parametrize("temperature,humidity,valid", [(-41, 0, False), (-40, 0, True), (-41, 1, True)])
def test_sensor_rule(temperature, humidity, valid):
    values = dict(station_id="ABC", timestamp="2026-05-01T00:00", temperature_c=temperature, humidity=humidity)
    if valid:
        assert Reading(**values).temperature_c == temperature
    else:
        with pytest.raises(ValidationError, match="sensor failure"):
            Reading(**values)


def main() -> None:
    """Show each practice example."""
    print("--- Classes ---")
    thermometer = Thermometer("Porch")
    for value in [18.0, 25.0, 31.0, 34.0]:
        thermometer.add(value)
    print("Average:", thermometer.average(), "Hottest:", thermometer.hottest())
    print(thermometer)
    print([thermometer, Thermometer("Garden", [16.0, 19.0])])
    print("Above 30:", TemperatureAlert().breaches(thermometer))
    print("Above 33:", TemperatureAlert(33).breaches(thermometer))

    print("--- Dataclasses ---")
    station_a = Station("ABC", "Porch", 35.0, -80.0, 250.0)
    station_b = Station("ABC", "Porch", 35.0, -80.0, 250.0)
    station_c = Station("XYZ", "Hill", 36.0, -81.0, 500.0)
    print("Equal fields:", station_a == station_b)
    try:
        station_a.elevation = 300.0
    except FrozenInstanceError as error:
        print(error)
    print("Unique stations:", len({station_a, station_b, station_c}))
    try:
        @dataclass
        class BadBatch:
            stations: list[Station] = []
    except ValueError as error:
        print("Mutable default:", error)
    batch = StationBatch("East")
    print("Empty highest:", batch.highest())
    batch.add(station_a)
    batch.add(station_c)
    print("Highest:", batch.highest())

    print("--- Pydantic ---")
    values = dict(station_id="ABC", timestamp="2026-05-01T00:00", temperature_c=21.5, humidity=40)
    print(Reading(**values))
    missing = {key: value for key, value in values.items() if key != "timestamp"}
    for bad in [missing, values | {"temperature_c": 150}, values | {"humidity": "very humid"}]:
        try:
            Reading(**bad)
        except ValidationError as error:
            print(error)
    converted = Reading(**(values | {"temperature_c": "21.5"}))
    print(converted)
    print(type(converted.temperature_c), type(converted.humidity))
    try:
        Reading(station_id="A", temperature_c="warm", humidity=40)
    except ValidationError as error:
        print("Errors:", error.error_count())
        for problem in error.errors():
            print(problem["loc"], problem["msg"])
    print("Valid sensor:", Reading(**values))
    try:
        Reading(**(values | {"temperature_c": -45, "humidity": 0}))
    except ValidationError as error:
        print(error)


if __name__ == "__main__":
    main()

# Dataclass Q3, captured while running the bad default:
# mutable default <class 'list'> for field stations is not allowed: use default_factory
# pytest Q3, actual run summary: 13 passed in 0.19s
# pytest Q4, captured with 9 / 4, before restoring 9 / 5:
# > assert celsius_to_fahrenheit(100) == 212
# E assert 257.0 == 212
# E + where 257.0 = celsius_to_fahrenheit(100)
# FAILED warmup_01.py::test_celsius_to_fahrenheit - assert 257.0 == 212
# 1 failed in 0.21s
# Showing 257 instead of 212 points straight to the conversion calculation.
