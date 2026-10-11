# Write Pydantic models describing the API response

#Add a model_validator(mode="after") to HourlyBlock that rejects the response 
# if the three lists are not all the same length. 
# A response in which time has 168 entries and temperature_2m has 167 is corrupt. 
# Index i would then pair the wrong readings together without any error, 
# which is the kind of bug that produces answers that look correct but are not.
#Then, in report.py or a scratch cell, load weather_raw.json and 
# validate it with WeatherResponse.model_validate(...). Print the latitude, timezone,
#  and the number of hourly observations. You should see 168.

from pydantic import BaseModel, Field, model_validator, ValidationError
class HourlyBlock(BaseModel):
    """A class to store data in the hourly block"""
    time: list[str]
    temperature_2m: list[float]
    precipitation: list[float]

    @model_validator(mode="after")
    def reject_response(self):
        """rejects the response if the three lists are not all the same length."""
        if len(self.time) != len(self.temperature_2m) or len(self.time) != len(self.precipitation):
            raise ValueError("lists in HourlyBlock must have the same length!")
        return self




class WeatherResponse(BaseModel):
    """A class for storing metadata in response from the Open-Meteo API """
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str
    elevation: int
    hourly: HourlyBlock


