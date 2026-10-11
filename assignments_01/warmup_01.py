# --- Classes ---
# Q1

class Thermometer:
    def __init__(self, location, readings=None):
        self.location = location
        if readings is None:
            self.readings = []
        else:
            self.readings = list(readings)
            
        self.readings = readings
        

    def add(self, reading):
        self.readings.append(reading)

    def average(self):
        if len(self.readings) < 1:
            return None
        else:
            return sum(self.readings)/len(self.readings)

    def hottest(self):
        if len(self.readings) < 1:
            return None
        else:
            return max(self.readings)


    # Q2
    # Q2
    def __repr__(self):
        return f"Thermometer(location={self.location!r}, n_readings={len(self.readings)}, average={self.average()})"
        #Thermometer(location='Charlotte', n_readings=4, average=18.6)

#Create a Thermometer for a location of your choice, add at least four readings, and print the average and the hottest.
my_city = Thermometer("DC", [27, 22, 18, 33])
print(my_city.average())
print(my_city.hottest())
#why does average() need to handle the empty case? What would happen without that check?
#if the list is empty, the average will be 0/0, which will raise a error.

my_themometer = Thermometer("DC", [27, 22, 18, 33])
my_themometer2 = Thermometer("Virginia", [25, 22, 19, 36])
print(my_themometer)
#print both in a list
print([my_themometer, my_themometer2])
#what Python displays when a class has no __repr__, and why that is unhelpful when debugging.
#without __repr__, python displays only the class name and memory address. 
# It wont be able to tell the detailed information inside a class.

# Q3-----------------------------------

class TemperatureAlert:
    def __init__(self, threshold=30.0):
        self.threshold = threshold

    def breaches(self, thermometer):
        #returns a list of every reading in that Thermometer above the threshold.
        #threshold = 30.0
        temp = []       
        for i in thermometer.readings:
            if i > self.threshold:
                temp.append(i)

        return temp

object1 =  TemperatureAlert(threshold=22)
object2 =  TemperatureAlert(threshold=35)
print("results for classes Q3:")
print(object1.breaches(my_themometer))
print(object2.breaches(my_themometer))
# answers to questions:  with the threshold stored in the constructor rather than passing to the breaches function, 
# it saves time by setting it once and use the breaches function to check on many numbers of thermometers.


#-------------------
# --- Dataclass ---
#-------------------
# Q1
from dataclasses import dataclass, field
@dataclass(frozen=True)
class Station:
    """A class for describing a station's location"""
    station_id: int
    name: str
    latitude: float
    longitude: float
    elevation: float

station_a = Station(1, "DC", 38.8951, 77.0364, 8)
station_b = Station(1, "DC", 38.8951, 77.0364, 8)
print(station_a == station_b)
# comment: the dataclass decorator overwrite the __eq__ method to look at the field values of the objects, so when two objects have the same values, the result will be True;
# when comparing objects in standard classes, the __eq__ method looks at the memory addresses rather than field values.So the result would have been False.



# Q2
from dataclasses import FrozenInstanceError
try:
    station_a.name = "LA"

except FrozenInstanceError as e:
    print(f"error: {e}")

station_c = Station(3, 'WA', 34.0522, 118.2437, 89)
station_set = {station_a, station_b, station_c}
print(len(station_set))
# comment: when frozen=True, Python generates a __hash__() method based on the object's fields which is used to identify duplicates. 
# Therefore it helps the set to determine which values are unique and ignore repeat values.

# Q3

@dataclass
class StationBatch:
    region: str
    #stations: list[Station] = []
    #ValueError: mutable default <class 'list'> for field stations is not allowed: use default_factory
    stations: list[Station] = field(default_factory=list)
    
    # In Python, lists are mutable objects. When you assign [] as a default value directly in a class definition, that single list is created once and shared across every single instance of that class.
    #If it were allowed, modifying the list in one instance would unexpectedly change it for all other instances. To prevent this notorious "mutable default argument" bug, dataclasses explicitly blocks you from doing it.
    def add(self, station: Station) -> None:
        """Appends a Station object to the batch's list of stations."""
        self.stations.append(station)
    def highest(self) -> Station | None:
        """ returns the station with the greatest elevation, or None if the batch is empty"""
        if len(self.stations) == 0:
            return None
        else:
            return max(self.stations, key=lambda station: station.elevation)

#-----------------------
#       Pydantic 
#-----------------------

# Question 1
from pydantic import BaseModel, Field, model_validator, ValidationError
class Reading(BaseModel):
    station_id: str = Field(min_length=3)
    timestamp: str = Field()
    temperature_c: float = Field(ge=-90, le=60)
    humidity: float = Field(ge=0, le=100)

    @model_validator(mode="after")
    def failed_sensor(self):
        """failed sensor if a combination of humidity and temperature_c happens"""
        if self.humidity == 0 and self.temperature_c < -40:
            raise ValueError(
                print("failed sensor")
            )
        return self
    

reading = Reading(station_id='A56', timestamp='morning', temperature_c=-56.0, humidity=68.0)
print(reading)

#Question 2
print("pydantic q2" )
try:
    reading = Reading(station_id='A56', temperature_c=-56.0, humidity=68.0)
except ValidationError as e:
    print(f"error: {e}")

try:
    reading = Reading(station_id='A56', timestamp='morning', temperature_c=150.0, humidity=68.0)
except ValidationError as e:
    print(f"error: {e}")

try:
     reading = Reading(station_id='A56', timestamp='morning', temperature_c=-56.0, humidity="very humid")
except ValidationError as e:
    print(f"error: {e}")


reading2 = Reading(station_id='A56', timestamp='morning', temperature_c="21.5", humidity=40)
print(reading2)
#Add a comment: why does Pydantic accept "21.5" but reject "very humid"? State the rule in your own words.
#A: in pydantic, it allows numeric string by converting the string into float with built in function float(v). 
# But when it's non-numeric string, the float()function fails and then throw a python ValueError


# Question 3
print("pydantic Q3\n")
# Trigger several errors at once. In one try block, construct a Reading with 
# a too-short station_id, a missing timestamp, and a non-numeric temperature_c.
#Catch the ValidationError and loop over e.errors(), printing the loc and msg for each.
 
try:
    reading3 = Reading(station_id='AD', temperature_c="hot", humidity=40)
except ValidationError as e:
    print(f"{e.error_count()} problems found\n")
    for err in e.errors():
        print(f"  field={err['loc']}  type={err['type']}  msg={err['msg']}")
#Add a comment: how many errors were reported, and why is reporting all of them at once more useful than stopping at the first? 
# Three errors were reported, reporting them all at once is more useful because it
# helps to oversee the problems and fix them altogether than having to fix the problem one by one.


# Question 4
#Add a model_validator(mode="after") to Reading that rejects any reading where humidity is exactly 0.0 and 
# temperature_c is below -40 -- a combination that indicates a failed sensor rather than real weather.
#Show that a valid reading still constructs, and that the bad combination raises. 
# Add a comment explaining why this rule cannot be expressed with Field constraints alone.
print('pydantic q4 :')
try:
    reading4 = Reading(station_id='A58', timestamp='2026-10-05', temperature_c="-56", humidity=0)
except ValidationError as e:
    print(f"error: {e}")
# this rule cannot be expressed with Field constraints alone,
# becauce it only happens when two attributes field values both meet the requirement at the same time.
#  While with field constraint, it only set the value to one attribute.


#--------------------------
#        pytest
#--------------------------
# Q1
import pytest
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a Celsius temperature to Fahrenheit."""
    return celsius * 9 / 5 + 32

def test_celsius_to_fahrenheit():
    assert celsius_to_fahrenheit(0) == 32
    assert celsius_to_fahrenheit(100) == 212
    assert celsius_to_fahrenheit(37) == pytest.approx(98.6)
    # Floating-point arithmetic in Python produces 98.60000000000001 instead of 98.6.
    # pytest.approx is necessary here to allow for tiny floating-point precision errors.

# Q2
def mean(values: list[float]) -> float:
    """raises a ValueError with a useful message when values is empty."""
    if len(values) == 0:
            raise ValueError("values list can't be empty!")
    mean_value = sum(values)/len(values)
    return mean_value

def test_mean_of_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        mean([])

#The match= argument checks the error message against a regular expression,
#  Without match, pytest.raises(ValueError) passes if any ValueError occurs, 
# including one caused by a typo in your test setup. 
# That produces a test that passes for the wrong reason.

# Q3
@pytest.mark.parametrize(
        "values, expected",
        [
            ([6], 6.0),
            ([-8, 4, -5], -3.0),
            ([36,7,9,20], 18.0),
            ([26, 8, 2], 12.0)
        ]
)       
def test_mean_values(values, expected):
    assert mean(values) == pytest.approx(expected)
# 6 passed in 0.09s
# one parametrized test with four test cases is better than four nearly identical test functions, 
# because each one gets its own line in the output and its own pass or fail result,
#  so a single broken case does not hide the others.
    
# Q4
"""def test_celsius_to_fahrenheit():
        assert celsius_to_fahrenheit(0) == 32
>       assert celsius_to_fahrenheit(100) == 212
E       assert 257.0 == 212
E        +  where 257.0 = celsius_to_fahrenheit(100)

warmup_01.py:226: AssertionError"""

#what specific values did pytest show you in the failure report, 
# and why is that more useful than a bare "assertion failed"?
#it shows the expected value 212 and the actual value 257.this is more useful than a bare "assertion failed"
# because it gives you a clue about what went wrong to help you manually debug the code
