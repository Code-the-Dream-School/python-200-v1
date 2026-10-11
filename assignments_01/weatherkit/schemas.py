from pydantic import BaseModel, Field
from pydantic import ValidationError, model_validator

class HourlyBlock(BaseModel):
    time: list[str]
    temperature_2m: list[float]    
    precipitation: list[float]

    @model_validator(mode="after")
    def check_lengths(self):
        if not (len(self.time) == len(self.temperature_2m) == len(self.precipitation)):
            raise ValueError("All hourly lists must have the exact same lenght!")
        return self

class WeatherResponse(BaseModel):
    latitude:float = Field(ge=-90, le=90)
    longitude: float = Field(ge= -180, le=180)
    timezone:str
    elevation: float
    hourly: HourlyBlock