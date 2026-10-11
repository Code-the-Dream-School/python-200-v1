#Task 3
#Write a dataclass HourlyReading with fields timestamp: str, 
# temperature_c: float, and precipitation_mm: float, plus a docstring documenting the units.

from weatherkit import  WeatherResponse

from dataclasses import dataclass, field

@dataclass
class HourlyReading:
    """A class for storing the hourly weather data as timestamp, temperature in celsius, 
    precipitation in mm """
    timestamp: str
    temperature_c: float
    precipitation_mm: float
def to_readings(response: WeatherResponse) -> list[HourlyReading]:
        """converts the columnar hourly block from the WeatherResponse object into one HourlyReading per hour, preserving order.
            Args:
                response: WeatherResponse object storing weather data.
            Returns:
                A list of HourlyReading objects storing repackaged weather data.
        """
        hourly_reading_list = []
        for i, timestamp in enumerate(response.hourly.time):
            temp = response.hourly.temperature_2m[i]
            precipitation = response.hourly.precipitation[i]

            hourly_reading_list.append(HourlyReading(timestamp=timestamp, temperature_c=temp, precipitation_mm=precipitation))
        return hourly_reading_list

# pydantic model is for validating untrusted data,but it costs lower performance and increased memory usage.
#the WeatherResponse need to be written in pydantic because it needs to validate the API date, once the data is in WeatherResponse,
#it can be trusted. So future operations on that data can use unvalidated strutures like dataclass,which is faster.