#Task 4: The Aggregation -- weatherkit/summarize.py
#Write a dataclass DailySummary with fields date: str, temp_max: float, temp_min: float, p
#recipitation_sum: float, and hours_observed: int. Add a method temp_range() -> float.
import pandas as pd
from weatherkit import  WeatherResponse, HourlyReading
from dataclasses import dataclass, field

@dataclass
class DailySummary:
    """class to store daily weather data summary"""
    date: str
    temp_max: float
    temp_min: float
    hours_observed: int
    precipitation_sum: float
    
    def temp_range(self) -> float:
        """shows the temperature range."""
        return self.temp_max - self.temp_min

class DailyAggregator:
    """class to perform daily weather data aggregation and summarization"""
    def __init__(self, min_hours: int = 24):
        self.min_hours = min_hours

    def summarize(self, readings: list[HourlyReading]) -> list[DailySummary]:
        """identifies datapoints which were captured on the same calendar day, discards data from incomplete days, 
        calculates max and min temperatures as well as the total precipitation. Summarized data is packaged into a list of DailySummary objects"""
        df = pd.DataFrame(readings)
        df['date'] = df['timestamp'].str.split('T').str[0]
        df = df.groupby('date').agg({'temperature_c': ['max', 'min', 'count'], 'precipitation_mm': 'sum'}).reset_index()
        
        #print("this is df after group by:\n", df)
        #Flatten the MultiIndex headers into clean strings
        df.columns = [f"{col[0]}_{col[1]}".rstrip('_') for col in df.columns]
        print("clean header:\n", df)

        incomplete_days = df[df['temperature_c_count'] < self.min_hours].index
        #print(incomplete_days)
        df.drop(index=incomplete_days, inplace=True)
        summary_list = [
            DailySummary(
                date=row.date,
                temp_max=row.temperature_c_max,
                temp_min=row.temperature_c_min,
                hours_observed=row.temperature_c_count,
                precipitation_sum=row.precipitation_mm_sum
            )
            for row in df.itertuples()
        ]
        #for i in range(df.shape[0]):
            #summary_list.append(DailySummary(date=df.index[i], temp_max=df.iloc[i,0].item(), temp_min=df.iloc[i,1].item(), precipitation_sum=df.iloc[i,3].item(), hours_observed=df.iloc[i,2].item()))
        return summary_list
    #A method incomplete_days(readings: list[HourlyReading]) -> list[str] returning the dates that were dropped, 
    # so nothing disappears silently.
    def incomplete_days(self, readings: list[HourlyReading]) -> list[str]:
        """returning a list of dates that have incomplete hours."""
        df = pd.DataFrame(readings)
        df['date'] = df['timestamp'].str.split('T').str[0]
        df = df.groupby('date').agg({'temperature_c': 'count'})
        incomplete_days = df[df['temperature_c'] < self.min_hours].index
        return incomplete_days.to_list()

