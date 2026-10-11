import pytest
import json
from weatherkit.schemas import WeatherResponse
from pathlib import Path
from pydantic import ValidationError

def test_validation_of_weather_raw():
    with open(Path(__file__).parent.parent / "weather_raw.json", 'r') as file:
        #A relative path would be unreliable because it depends on the working directory in the terminal where this code is invoked.
        weather_raw = json.load(file)
    test_response = WeatherResponse.model_validate(weather_raw)
    assert len(test_response.hourly.time) == 168

def test_latitude_200_raises():
    with open(Path(__file__).parent.parent / "weather_raw.json", 'r') as file:
        weather_raw = json.load(file)
    weather_raw['latitude']=200
    with pytest.raises(ValidationError): 
        WeatherResponse.model_validate(weather_raw)

def test_mismatch_list_length_raises():
    dict_1 = {"latitude":35.216976,"longitude":-80.83189,"timezone":"GMT","elevation":254.0,"hourly":{"time":["2026-04-11T17:00","2026-04-11T18:00","2026-04-11T19:00"], "temperature_2m":[18.3, 22.44, 19.02, 26.19], "precipitation":[0, 0, 0, 0, 0, 0]}}
    with pytest.raises(ValidationError):
        WeatherResponse.model_validate(dict_1)

def test_null_in_temperature_2m_raises():
    dict_2 = {"latitude":35.216976,"longitude":-80.83189,"timezone":"GMT","elevation":254.0,"hourly":{"time":["2026-04-11T17:00","2026-04-11T18:00","2026-04-11T19:00", "2026-04-11T20:00"], "temperature_2m":[18.3, 22.44, 19.02, None], "precipitation":[0, 0, 0, 0]}}
    with pytest.raises(ValidationError):
        WeatherResponse.model_validate(dict_2)