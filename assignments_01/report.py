import json
from weatherkit import WeatherResponse, DailyAggregator
from weatherkit.records import to_readings

def main():

    """Main execution flow for generating the weather report."""

    with open("../assignments/resources/weather_raw.json", 'r') as file:
        weather_raw = json.load(file)

    test_response = WeatherResponse.model_validate(weather_raw)

    hourly_list = to_readings(test_response)

    daily_agg = DailyAggregator()
    daily_summary = daily_agg.summarize(hourly_list)
    #print(daily_agg.incomplete_days(hourly_list))
    print(' date          temp_max      temp_min   precipitation_sum  temp_range')
    for i in daily_summary:
        print(f"{i.date}, {i.temp_max:10}, {i.temp_min:10}, {i.precipitation_sum:10}, {i.temp_range():20}")

    #Prints a warning line listing any incomplete days that were dropped   
    dropped_days = daily_agg.incomplete_days(hourly_list)
    if dropped_days:
        print("warning: this days are dropped due to incompltete hours.", daily_agg.incomplete_days(hourly_list))

if __name__ == "__main__":
    main()

#If the main function doesn't exist, and someone imported the file, then all of the code would execute imediately.

#Task 7

#1.Your WeatherResponse rejects the whole file if a single temperature is null. 
# Is that the right behavior for a weather pipeline? Describe one situation where you would want it, 
# and one where you would rather tolerate the gap. What would you change in the schema to tolerate it?
#A1: No, it should reject the whole file when the data is strictly important and would have big effect with one temperature missing.
#    I would tolerate the gap if one missing data wouldn't affect the overall analyst result. I would replace null values with the mean value.

#2.DailyAggregator.min_hours defaults to 24. What goes wrong if a pipeline runs at noon and the day is only half over? 
# How does incomplete_days() help?
#A2: This day would be droped and put in the incomplete_days list. incomplete_days() helps the user to see which days are incomplete.

#3.You wrote weatherkit as a package rather than one file. Name one concrete thing that becomes easier in Week 10, 
# when a pipeline needs to import this code.
#A3: a package is modular. So each module could be used separately, which reduces overhead and makes code more efficient.
