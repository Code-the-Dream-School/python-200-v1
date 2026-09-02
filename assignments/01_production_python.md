# Week 1 Assignments

This week's assignments cover the week 1 material:

- Classes: attributes, methods, `__init__`, `__repr__`
- Dataclasses, type hints, and docstrings
- Pydantic models for validating data at your program's boundary
- `pytest`: test functions, assertions, error cases, parametrize, fixtures
- Splitting code into importable modules and a package

The warmup exercises help you practice the core mechanics, so try to work through them without AI assistance. The project differs from previous weeks in one important way: **you are building a small package rather than a script.** The structure of what you submit is part of what is being assessed.

Everything you build this week is an early version of something you will build again later. The schema in Task 2 becomes the extract step in Week 9, and the package layout becomes the structure of your Week 4 model component.

---

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_01/`. Inside it, build this structure:

```text
assignments_01/
├── warmup_01.py            <- Part 1: the warmup exercises
├── weather_raw.json        <- copied from the course repo (see below)
├── weatherkit/             <- Part 2: your package
│   ├── __init__.py
│   ├── schemas.py          <- Pydantic models (the boundary)
│   ├── records.py          <- dataclasses (inside the boundary)
│   └── summarize.py        <- the aggregation class
├── tests/
│   ├── test_schemas.py
│   ├── test_records.py
│   └── test_summarize.py
└── report.py               <- a script that uses the package
```

Copy `weather_raw.json` from the course repo at `assignments/resources/weather_raw.json` into your `assignments_01/` folder before you start.

Install this week's two new packages:

```bash
uv pip install pydantic pytest
```

When finished, commit and open a PR as described in the [assignments README](README.md).

**Primary submission**: A link to your open GitHub PR. Your grader will run `pytest` from inside `assignments_01/`, so make sure it passes from there.

---

# Part 1: Warmup Exercises

Put all warmup exercises in a single file: `warmup_01.py`. Use comments to mark each section and question (e.g. `# --- Classes ---` and `# Q1`). Use `print()` to display all outputs.

## Classes

### Classes Question 1

Write a class `Thermometer` that stores a list of temperature readings in Celsius.

- `__init__` takes a `location` (a string) and an optional list of `readings` that defaults to an empty list.
- A method `add(reading)` appends one reading.
- A method `average()` returns the mean of the readings, or `None` if there are none.
- A method `hottest()` returns the highest reading, or `None` if there are none.

Create a `Thermometer` for a location of your choice, add at least four readings, and print the average and the hottest.

Then add a comment: why does `average()` need to handle the empty case? What would happen without that check?

### Classes Question 2

Add a `__repr__` to `Thermometer` that prints something like:

```text
Thermometer(location='Charlotte', n_readings=4, average=18.6)
```

Print the object directly (`print(my_thermometer)`) to confirm it works, and also print a list containing two of them.

Add a comment explaining what Python displays when a class has no `__repr__`, and why that is unhelpful when debugging.

### Classes Question 3

Write a second class `TemperatureAlert` that holds a `threshold` (a float, defaulting to 30.0) and has one method:

- `breaches(thermometer)` -- returns a list of every reading in that `Thermometer` above the threshold.

Create two `TemperatureAlert` objects with different thresholds and run both against the *same* `Thermometer`. Print both results.

Add a comment answering these questions: why is the threshold stored on `TemperatureAlert` rather than passed as an argument to `breaches()`? What advantage does that give you if you have twenty thermometers to check?

## Dataclasses, Type Hints, and Docstrings

### Dataclass Question 1

Rewrite this class as a dataclass. Add type hints to every field and a docstring describing what it represents.

```python
class Station:
    def __init__(self, station_id, name, latitude, longitude, elevation):
        self.station_id = station_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
```

Create two `Station` objects with identical field values and print `station_a == station_b`. Add a comment explaining why the result is what it is, and what it would have been with the original hand-written class.

### Dataclass Question 2

Make `Station` frozen. Then:

1. Show that assigning to a field now raises `FrozenInstanceError` (catch it and print the message -- do not let the script crash).
2. Build a `set` containing three `Station` objects where two are identical, and print the length.

Add a comment: what does `frozen=True` give you besides immutability, and why is that useful here?

### Dataclass Question 3

Write a dataclass `StationBatch` with:

- A `region` field (a string)
- A `stations` field that is a list of `Station`, defaulting to empty
- A method `add(station: Station) -> None`
- A method `highest(self) -> Station | None` that returns the station with the greatest elevation, or `None` if the batch is empty

First try writing the default as `stations: list[Station] = []`, run it, and paste the error you get into a comment. Then fix it properly and explain in that comment why Python refuses the first version.

Give every method a type-hinted signature and a docstring.

## Pydantic

### Pydantic Question 1

Write a Pydantic model `Reading` with these fields:

| Field | Type | Constraint |
|---|---|---|
| `station_id` | `str` | at least 3 characters |
| `timestamp` | `str` | required |
| `temperature_c` | `float` | between -90 and 60 |
| `humidity` | `float` | between 0 and 100 |

Construct one valid `Reading` and print it.

### Pydantic Question 2

Show three separate failures, each wrapped in `try` / `except ValidationError` so your script keeps running. Print the error each time.

1. A missing required field
2. A `temperature_c` of `150.0`
3. A `humidity` of `"very humid"`

Then construct a `Reading` where `temperature_c` is passed as the *string* `"21.5"` and `humidity` is passed as the *integer* `40`. Print the resulting object and the `type()` of both fields.

Add a comment: why does Pydantic accept `"21.5"` but reject `"very humid"`? State the rule in your own words.

### Pydantic Question 3

Trigger several errors at once. In one `try` block, construct a `Reading` with a too-short `station_id`, a missing `timestamp`, and a non-numeric `temperature_c`.

Catch the `ValidationError` and loop over `e.errors()`, printing the `loc` and `msg` for each.

Add a comment: how many errors were reported, and why is reporting all of them at once more useful than stopping at the first?

### Pydantic Question 4

Add a `model_validator(mode="after")` to `Reading` that rejects any reading where `humidity` is exactly `0.0` **and** `temperature_c` is below `-40` -- a combination that indicates a failed sensor rather than real weather.

Show that a valid reading still constructs, and that the bad combination raises. Add a comment explaining why this rule cannot be expressed with `Field` constraints alone.

## pytest

Write these as real pytest tests inside `warmup_01.py`, named `test_*` as usual.

pytest will not *discover* `warmup_01.py` on its own, because the filename does not match the `test_*.py` pattern. But it will happily run it if you name the file explicitly:

```bash
pytest warmup_01.py -v
```

Use that command to run this section. (Your Part 2 tests live in `tests/` and are discovered normally.)

### pytest Question 1

Write a function `celsius_to_fahrenheit(celsius: float) -> float` with a docstring.

Then write `test_celsius_to_fahrenheit()` asserting that:

- 0 C is 32 F
- 100 C is 212 F
- 37 C is approximately 98.6 F

The third one will fail with a plain `==`. Make it pass with `pytest.approx`, and add a comment explaining why it was necessary.

### pytest Question 2

Write a function `mean(values: list[float]) -> float` that raises a `ValueError` with a useful message when `values` is empty.

Write `test_mean_of_empty_raises()` using `pytest.raises(ValueError, match=...)` to confirm both that the error is raised and that the message contains the word you expect.

Add a comment: what would `pytest.raises(ValueError)` alone fail to catch that `match=` catches?

### pytest Question 3

Write `test_mean_values()` using `@pytest.mark.parametrize` to check at least four input/output pairs for `mean`, including a single-element list and a list containing negative numbers.

Run `pytest warmup_01.py -v` and look at the output: each parametrized case gets its own line. Paste the summary line into a comment.

Add a comment: why is one parametrized test with four cases better than four nearly identical test functions?

### pytest Question 4

Deliberately break `celsius_to_fahrenheit` (for example, change `9 / 5` to `9 / 4`). Run your test again and paste the failure output into a comment. Then fix the function.

Add a comment answering: what specific values did pytest show you in the failure report, and why is that more useful than a bare "assertion failed"?

---

# Part 2: Project -- The `weatherkit` Package

You are going to build the first version of a package that turns a raw weather API response into clean daily summaries. This is a real pipeline step, compressed: Week 9 does the same job against a live API and a cloud database.

The input is `weather_raw.json` -- an actual response from the [Open-Meteo](https://open-meteo.com/) API containing **168 hourly observations** (7 days) for Charlotte, NC. Open it in a text editor before you write any code and look at its shape.

Notice two things about this file:

- The measurements live under an `"hourly"` key, and they are **columnar**: `time`, `temperature_2m`, and `precipitation` are three parallel lists, not a list of hour objects. Hour *i* is assembled by taking index *i* from each list.
- There is other metadata at the top level (`latitude`, `longitude`, `timezone`, `elevation`, `hourly_units`) that you may or may not choose to model.

## Task 1: Package Skeleton

Create the `weatherkit/` directory with an `__init__.py`, plus a `tests/` directory. Confirm you can run `pytest` from `assignments_01/` and have it collect zero tests without erroring.

Your `__init__.py` should export the main classes so that callers can write `from weatherkit import HourlyReading` rather than `from weatherkit.records import HourlyReading`. Add those imports as you build each piece.

## Task 2: The Boundary -- `weatherkit/schemas.py`

Write Pydantic models describing the API response.

- `HourlyBlock` -- the columnar arrays: `time` (list of str), `temperature_2m` (list of float), `precipitation` (list of float).
- `WeatherResponse` -- the top level: `latitude`, `longitude`, `timezone`, `elevation`, and a nested `hourly: HourlyBlock`.

Constrain `latitude` to -90 to 90 and `longitude` to -180 to 180. Give both models a docstring.

Add a `model_validator(mode="after")` to `HourlyBlock` that rejects the response if the three lists are not all the same length. A response in which `time` has 168 entries and `temperature_2m` has 167 is corrupt. Index *i* would then pair the wrong readings together without any error, which is the kind of bug that produces answers that look correct but are not.

Then, in `report.py` or a scratch cell, load `weather_raw.json` and validate it with `WeatherResponse.model_validate(...)`. Print the latitude, timezone, and the number of hourly observations. You should see 168.

## Task 3: Inside the Boundary -- `weatherkit/records.py`

Write a **dataclass** `HourlyReading` with fields `timestamp: str`, `temperature_c: float`, and `precipitation_mm: float`, plus a docstring documenting the units.

Then write a function:

```python
def to_readings(response: WeatherResponse) -> list[HourlyReading]:
    ...
```

that converts the columnar `hourly` block into one `HourlyReading` per hour, preserving order. Give it a full docstring with `Args:` and `Returns:` sections.

Add a comment answering this question: **why is `HourlyReading` a dataclass rather than a Pydantic model, when `WeatherResponse` is a Pydantic model?** Be specific. A good answer identifies where the boundary is.

## Task 4: The Aggregation -- `weatherkit/summarize.py`

Write a dataclass `DailySummary` with fields `date: str`, `temp_max: float`, `temp_min: float`, `precipitation_sum: float`, and `hours_observed: int`. Add a method `temp_range() -> float`.

Then write a class `DailyAggregator` that groups hourly readings into daily summaries:

- `__init__` takes a parameter `min_hours: int = 24`, which is the minimum number of hourly observations required before a day is reported. You should not trust the daily maximum from a day with only 6 hours of data.
- A method `summarize(readings: list[HourlyReading]) -> list[DailySummary]` that groups readings by calendar date (the first 10 characters of the timestamp), computes the max and min temperature and the total precipitation for each, records how many hours contributed, and **drops** any day with fewer than `min_hours` observations. Return the summaries sorted by date.
- A method `incomplete_days(readings: list[HourlyReading]) -> list[str]` returning the dates that were dropped, so nothing disappears silently.

Give everything type hints and docstrings.

### Self-check

Run your aggregator on the full file with the default `min_hours=24`. You should get **7 summaries**, and the first two should be:

| date | temp_max | temp_min | precipitation_sum | hours_observed |
|---|---|---|---|---|
| 2026-04-08 | 16.8 | 7.8 | 0.0 | 24 |
| 2026-04-09 | 19.3 | 3.7 | 0.0 | 24 |

If your numbers differ, check whether you are grouping on the date portion of the timestamp rather than the whole string.

## Task 5: The Test Suite

Write tests in `tests/`. They must pass when you run `pytest` from `assignments_01/`.

**`tests/test_schemas.py`** -- at least four tests:

1. A valid response validates, and `hourly.time` has 168 entries. Load the real JSON file for this one.
2. A latitude of `200.0` raises `ValidationError`.
3. Mismatched list lengths raise `ValidationError`. Build a small hand-written dict for this -- three or four entries is plenty, and one list one element short.
4. A `null` inside `temperature_2m` raises `ValidationError`.

For test 1, the path to `weather_raw.json` must work regardless of the directory pytest is run from. Use `Path(__file__).parent.parent / "weather_raw.json"` rather than a plain relative path, and add a comment explaining why a plain relative path is unreliable.

**`tests/test_records.py`** -- at least three tests:

1. `to_readings` returns one reading per hour, in order (check the first and last timestamps).
2. The values in reading *i* match index *i* of each input list. This test catches the case where readings are paired with the wrong timestamps.
3. Two `HourlyReading` objects with identical fields compare equal.

**`tests/test_summarize.py`** -- at least five tests. Use a `@pytest.fixture` for shared input.

1. Grouping works: a hand-built list spanning two dates produces two summaries.
2. `temp_max` and `temp_min` are correct for a known small input.
3. `precipitation_sum` adds up correctly. Use `pytest.approx`.
4. **A day with fewer than `min_hours` readings is dropped**, and its date appears in `incomplete_days()`.
5. Lowering `min_hours` causes that same day to be *kept* -- proving the parameter is actually consulted rather than ignored.

At least one test must use `@pytest.mark.parametrize`.

> Before you submit, deliberately break one function in `weatherkit/` and confirm that the relevant test fails. A test that cannot fail is not a useful test. Note in a comment which test caught the change.

## Task 6: The Script -- `report.py`

Write a script at `assignments_01/report.py` that ties it all together:

1. Loads `weather_raw.json`
2. Validates it into a `WeatherResponse`
3. Converts it to `HourlyReading` objects
4. Aggregates to `DailySummary` objects
5. Prints a readable table -- one row per day with date, high, low, total precipitation, and temperature range
6. Prints a warning line listing any incomplete days that were dropped

Put the work in a `main()` function and call it under an `if __name__ == "__main__":` guard.

Add a comment explaining what would happen if you omitted the guard and someone imported `report.py` to reuse one of its helper functions.

## Task 7: Reflection

At the bottom of `report.py`, in a comment block, answer:

1. Your `WeatherResponse` rejects the whole file if a single temperature is `null`. Is that the right behavior for a weather pipeline? Describe one situation where you would want it, and one where you would rather tolerate the gap. What would you change in the schema to tolerate it?
2. `DailyAggregator.min_hours` defaults to 24. What goes wrong if a pipeline runs at noon and the day is only half over? How does `incomplete_days()` help?
3. You wrote `weatherkit` as a package rather than one file. Name one concrete thing that becomes easier in Week 10, when a pipeline needs to import this code.

---

# Optional Extensions

## Extension A: Handle Missing Readings (Low)

Change `HourlyBlock` to tolerate `None` in `temperature_2m` and `precipitation`, and update `to_readings` and `DailyAggregator` to skip missing values while still counting the hours correctly. Add tests covering a day with a gap.

## Extension B: Configurable Summaries (Moderate)

Add a `RunningWindow` class that finds, for each day, the longest run of consecutive hours where the temperature was inside a configurable comfortable range and precipitation was zero. Return the start hour and length. Test the boundaries carefully -- runs at the start and end of a day, and a day with no qualifying hours.

## Extension C: Make It Installable (Moderate)

Write a minimal `pyproject.toml` for `weatherkit` and install it with `uv pip install -e .`. Confirm that your tests now pass when run from *any* directory, not just `assignments_01/`. Explain in a comment what changed.

Good luck. Remember that this week, the structure of your code is a central part of the assignment.
