# ---------- Classes ---------
# Q1

class Thermometer:
    def __init__(self, location: str, readings : list[float] | None = None) -> None:
        self.location = location
        if readings is None:
            self.readings = []
        else:
            self.readings = list(readings)

    def add(self, reading: float) -> None:
        self.readings.append(reading)

    def average(self) -> float | None:
        if not self.readings:
            return None
        return sum(self.readings)/len(self.readings)

    def hottest(self) -> float | None:
        if not self.readings:
            return None
        return max(self.readings)

      
my_thermometer = Thermometer("Philly")
my_thermometer.add(62.5)
my_thermometer.add(72.0)
my_thermometer.add(80.0)
my_thermometer.add(68.5)

# Print the average and the hottest
print(f"Average temperature in {my_thermometer.location}: {my_thermometer.average()}")
print(f"Hottest temperature in {my_thermometer.location}: {my_thermometer.hottest()}")

# average() must handle the empty case to prevent any errors 
# when dividing, such as ZeroDivisionError


# Q2
class Thermometer:
    def __init__(self, location: str, readings : list[float] | None = None) -> None:
        self.location = location
        if readings is None:
            self.readings = []
        else:
            self.readings = list(readings)

    def add(self, reading: float) -> None:
        self.readings.append(reading)

    def average(self) -> float | None:
        if not self.readings:
            return None
        return sum(self.readings)/len(self.readings)

    def hottest(self) -> float | None:
        if not self.readings:
            return None
        return max(self.readings)

    def __repr__(self):
            return f"Thermometer(location='{self.location}', n_readings={len(self.readings)}, average= {self.average()})"

my_thermometer = Thermometer("Philly")
my_thermometer.add(62.5)
my_thermometer.add(72.0)
my_thermometer.add(80.0)
my_thermometer.add(68.5)

print(my_thermometer)

# When our class does not have __repr__ it shows default memory references 
# such as <__main__.Thermometer object at 0x109b95d30>. It is not helpful for
# debugging due to the lack of the object's actual attributes.


# Q3
class TemperatureAlert:
    def __init__(self, threshold: float = 30.0) -> None:
        self.threshold = threshold

    def breaches(self, thermometer: Thermometer) -> list[float]:
        breached = []
        for r in thermometer.readings:
            if r > self.threshold:
                breached.append(r)
        return breached


philly_thermometer = Thermometer("Philly", [25.0, 32.0, 28.5, 35.0])
alert = TemperatureAlert(threshold=30.0)

results = alert.breaches(philly_thermometer)
print(results)  # Prints: [32.0, 35.0]

# Storing threshold on TemperatureAlert configures the alert object with a fixed boundary rule. 
# The advantage when checking twenty thermometers is that you set the threshold once when 
# If the threshold ever needs to change, you only update it in one place instead of changing twenty function calls.



# ---------- Dataclass ---------
# Q1
from dataclasses import dataclass

@dataclass
class Station:
    station_id: str
    name: str
    latitude: float
    longitude:float
    elevation: float


station_a = Station("CE306", "Amtrak", 45.22, -89.44, 14.0)
station_b = Station("CE306", "Amtrak", 45.22, -89.44, 14.0)

print(station_a == station_b)

# The @dataclass decorator automatically generates an __eq__ (equality) method behind 
# the scenes. This method compares two objects field-by-field (station_id, name, latitude, 
# longitude, and elevation). Since both objects hold identical data in every field, 
# Python considers them equal and returns True.

# What the result would have been with the original hand-written class:
# With the original hand-written class, station_a == station_b would evaluate to False. 
# Without a custom __eq__ method, plain Python classes use default identity comparison 
# (comparing memory addresses). Because station_a and station_b are two distinct objects 
# created separately in memory, Python sees them as unequal even if their attributes match.




# Q2
from dataclasses import dataclass, FrozenInstanceError

@dataclass(frozen=True)
class Station:
    station_id: str
    name: str
    latitude: float
    longitude: float
    elevation: float


station_a = Station("CE306", "Amtrak", 45.22, -89.44, 14.0)
station_b = Station("CE306", "Amtrak", 45.22, -89.44, 14.0)
station_c = Station("BF405", "Acela", 36.75, -57.92, 12.0)

try:
    station_b.name = "Northeast Regional"
except FrozenInstanceError as e:
    print("Cannot modify:", e)


stations = {
    Station("CE306", "Amtrak", 45.22, -89.44, 14.0),
    Station("CE306", "Amtrak", 45.22, -89.44, 14.0),
    Station("BF405", "Acela", 36.75, -57.92, 12.0),
}
print(len(stations))

# besides immutability, frozen=True gives us an advatage to put our objects 
# inside curl braces to create a set without getting a UNhashableTypeError




# Q3
from dataclasses import dataclass, field

@dataclass
class StationBatch:
    """Represents a collection of weather stations within a specific region."""
    region : str
    stations : list[Station] = field(default_factory=list)

    def add(self, station: Station) -> None:
        """Adds a Station instance to the batch list."""
        self.stations.append(station)

    def highest(self) -> Station | None:
        """Returns the Station with the highest elevation, or None if empty."""
        if not self.stations:
            return None
        return max(self.stations, key=lambda s: s.elevation)

# error : raise ValueError(f'mutable default {type(f.default)} for field 'f'{f.name} is not allowed: use default_factory')
# Python dataclasses disallow mutable default values like list [] or dict {} in field definitions.
# If [] were allowed, every instance of StationBatch created without explicit stations would share 
# the exact same list object in memory, leading to shared-state bugs.


# ---------- Pydantic --------- 

# Q1
from pydantic import BaseModel, Field

class Reading(BaseModel):
    station_id: str = Field(min_length=3)
    timestamp: str
    temperature_c: float = Field(ge=-90.0, le=60.0)
    humidity: float = Field(ge=0, le=100)

# One valid reading
reading = Reading(
    station_id="amtrak21", 
    timestamp="2026-10-05", 
    temperature_c=57.48, 
    humidity=50.33
)

print(reading)


# Q2
from pydantic import ValidationError

print("\n")
# Failure 1 (A missing require field)
try:
    f1 = valid = Reading(
        station_id="amtrak21", 
        temperature_c=57.48, 
        humidity=50.33
    )
    print(f1)
except ValidationError as e:
    print(e)

print("\n")
# Failure 2 (A temperature_c of 150.0)
try:
    f2 = valid = Reading(
        station_id="amtrak21", 
        timestamp="2027-12-11",
        temperature_c=150.0, 
        humidity=50.33
    )
    print(f2)
except ValidationError as e:
    print(e)

print("\n")
# Failure 3 (A humidity of "very humid")
try:
    f3 = valid = Reading(
        station_id="amtrak21", 
        timestamp="2027-12-11",
        temperature_c=150.0, 
        humidity="very humid"
    )
    print(f3)
except ValidationError as e:
    print(e)


# Construct a new Reading

new_reading = Reading(
    station_id="amtrak21", 
    timestamp="2026-10-05", 
    temperature_c="21.5", 
    humidity=40
)

print("\n")
print(new_reading)
print(type(new_reading.temperature_c))
print(type(new_reading.humidity))


# Q3
print("\n")
try:
    all_error = Reading(
        station_id="a", 
        temperature_c="very hot", 
        humidity=50.33
    )
    print(all_error)
except ValidationError as e:
    for err in e.errors():
        print("Location:", err["loc"])
        print("Message:", err["msg"])




# ---------- Pytest ---------
import pytest

# Q1

def celcius_to_fahrenheit(celsius: float) -> float:
    """Converts a temperature from Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32

def test_celsius_to_fahrenheit():
    assert celcius_to_fahrenheit(0) == 32.0
    assert celcius_to_fahrenheit(100) == 212.0
    assert celcius_to_fahrenheit(37) == pytest.approx(98.6)
# It is important to use approximate because when the numbers are 
# calculated, it will come out with a lot of number behind the comma.


from pydantic import ValidationError

# Q2
def mean(values: list[float]) -> float:
    """Calculates the average of a list of numbers. Raises ValueError if list is empty."""
    if not values:
        raise ValueError("Cannot calculate mean of an empty list")
    return sum(values) / len(values)


def test_mean_of_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        mean([])


# Q3
@pytest.mark.parametrize("numbers, expected_mean", [
    ([10.0, 20.0, 30.0], 20.0),      
    ([42.0], 42.0),                   
    ([-10.0, -20.0, -30.0], -20.0),   
    ([0.0, 100.0], 50.0),           
])
def test_mean_values(numbers, expected_mean):
    assert mean(numbers) == expected_mean

# Q4

def celsius_to_fahrenheit(celsius: float) -> float:
    """Converts a temperature from Celsius to Fahrenheit."""
    return (celsius * 9 / 4) + 32  

"""
FAILED warmup_01.py::test_celsius_to_fahrenheit - assert 257.0 == 212.0
 +  where 257.0 = celsius_to_fahrenheit(100)
 E  AssertionError: assert 257.0 == 212.0
 E   +  where 257.0 = celsius_to_fahrenheit(100)
"""

def celsius_to_fahrenheit(celsius: float) -> float:
    """Converts a temperature from Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32
