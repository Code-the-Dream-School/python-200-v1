# Assignment 1 Answer Key: Production Python (the `weatherkit` package)

**Mentor note:** This key covers Week 1, which was rewritten from the old analysis-intro week into Production Python. The warmups practice classes, dataclasses, type hints, Pydantic, and pytest in a single file. The project builds a small importable package, `weatherkit`, that validates a raw weather API response and turns it into daily summaries. The structure of what the student submits is part of what is assessed, so read Task 1 and Task 5 carefully.

Objective items have one expected result. Subjective items list what a good answer discusses. Many warmup values (locations, temperatures, dates) are student-chosen, so those are marked as variable, and the method to check is given instead of a fixed number. The project numbers are fixed, because every student runs the same `weather_raw.json`.

The single most common failure point for this assignment is the **empty `conftest.py` at the root of `assignments_01/`**. Without it, a bare `pytest` run from `assignments_01/` cannot import `weatherkit`, and every project test fails with `ModuleNotFoundError: No module named 'weatherkit'`. Check for that file first when a submission's tests fail to collect.

---

## Expected File Setup

The assignment lives in `assignments_01/` inside the student's `python200-homework` repository:

```text
assignments_01/
├── warmup_01.py            # Part 1: every warmup answer, with # Q markers
├── weather_raw.json        # copied from assignments/resources/weather_raw.json
├── conftest.py             # EMPTY file; makes weatherkit importable under bare pytest
├── weatherkit/             # Part 2: the package
│   ├── __init__.py         # re-exports the main classes
│   ├── schemas.py          # Pydantic models (the boundary)
│   ├── records.py          # dataclass + to_readings (inside the boundary)
│   └── summarize.py        # DailySummary + DailyAggregator
├── tests/
│   ├── test_schemas.py
│   ├── test_records.py
│   └── test_summarize.py
└── report.py               # a script that uses the package
```

Submitted as a link to an open GitHub PR. The grader runs `pytest` from inside `assignments_01/`, so the `tests/` suite must pass from there.

Two grading rules from the rubric that mentors must respect:

- **File paths and folder layout are enforced by the automated `pytest` run, not by inspection.** Do not fail a student for a path or an internal file split you cannot verify, such as the location of `weather_raw.json` or the exact division of the package into `schemas.py`, `records.py`, and `summarize.py`. What matters is that the package imports and the `tests/` suite passes from `assignments_01/`.
- **Class, model, method, and function names in the tasks are exact.** These names are depended on by later tasks and by the tests: `HourlyBlock`, `WeatherResponse`, `HourlyReading`, `to_readings`, `DailySummary`, `DailyAggregator`, `min_hours`, `summarize`, `incomplete_days`, `temp_range`, and the warmup names `Thermometer`, `TemperatureAlert`, `Station`, `StationBatch`, `Reading`, `celsius_to_fahrenheit`, `mean`. Sample values (any location, date, or temperature the student picks, and the exact `Thermometer` repr format) are examples and may vary.

The warmup `pytest` functions live inside `warmup_01.py` and are run explicitly with `pytest warmup_01.py -v`. They are intentionally **not** collected by a bare `pytest` run of the `tests/` suite, because the filename does not match the `test_*.py` pattern. Do not fail a student because `warmup_01.py` is absent from the discovered suite.

---

# Part 1: Warmup Exercises (`warmup_01.py`)

All output uses `print()`. Comment markers separate the sections and questions. Students are asked to work these without AI assistance.

## Classes

### Classes Q1 — **Objective (structure) + Subjective (comment)**

`Thermometer` stores readings in Celsius.

- `__init__(self, location, readings=...)` where `readings` defaults to an empty list. A correct default uses `None` and assigns a fresh list inside `__init__`, or otherwise avoids sharing one list across instances. A literal `readings=[]` default is a known mutable-default trap; it is acceptable here for a warmup, but the cleaner pattern is worth praising.
- `add(reading)` appends one reading.
- `average()` returns the mean, or `None` when there are no readings.
- `hottest()` returns the highest reading, or `None` when there are no readings.

The demo creates one `Thermometer`, adds at least four readings, and prints the average and the hottest. The location and readings are student-chosen, so the printed numbers vary. Check that the average is the arithmetic mean of the readings the student added, and that the hottest is their maximum.

Reference:

```python
class Thermometer:
    def __init__(self, location, readings=None):
        self.location = location
        self.readings = readings if readings is not None else []

    def add(self, reading):
        self.readings.append(reading)

    def average(self):
        if not self.readings:
            return None
        return sum(self.readings) / len(self.readings)

    def hottest(self):
        if not self.readings:
            return None
        return max(self.readings)
```

Subjective comment: `average()` must handle the empty case because `sum(self.readings) / len(self.readings)` divides by zero when the list is empty, which raises `ZeroDivisionError`. Returning `None` reports "no data" without crashing.

### Classes Q2 — **Objective (structure) + Subjective (comment)**

A `__repr__` on `Thermometer` that produces something like `Thermometer(location='Charlotte', n_readings=4, average=18.6)`. The exact format is an example; the assignment says "something like". Check that printing the object directly shows the readable string rather than a memory address, and that printing a list of two `Thermometer` objects shows the repr for each element.

Subjective comment: without `__repr__`, Python prints the default form, `<__main__.Thermometer object at 0x...>`, which shows the type and memory address but none of the field values. That is unhelpful when debugging, because a list of records shows only addresses instead of the data.

### Classes Q3 — **Objective (structure) + Subjective (comment)**

`TemperatureAlert` holds a `threshold` field defaulting to `30.0` and has one method, `breaches(thermometer)`, that returns the list of readings in that `Thermometer` above the threshold. Two alerts with different thresholds are run against the *same* `Thermometer`, and both results are printed. The specific readings returned depend on the student's data; check that each result contains exactly the readings strictly above that alert's threshold.

Subjective comment: the threshold lives on the `TemperatureAlert` object so that the configuration is set once and applied many times. With twenty thermometers to check, the student creates the alert once and calls `breaches()` on each thermometer, rather than passing the threshold value through twenty separate calls. This is the "configure once, apply many times" pattern from the classes lesson.

## Dataclasses, Type Hints, and Docstrings

### Dataclass Q1 — **Objective (result) + Subjective (comment)**

`Station` rewritten as a dataclass with a type hint on every field (`station_id: str`, `name: str`, `latitude: float`, `longitude: float`, `elevation: float`) and a docstring describing what a `Station` represents.

Objective: two `Station` objects with identical field values, and `print(station_a == station_b)` outputs `True`.

Subjective comment: the result is `True` because `@dataclass` generates an `__eq__` that compares field values. The original hand-written class had no `__eq__`, so it would compare by object identity and print `False` for two separate instances.

### Dataclass Q2 — **Objective (result) + Subjective (comment)**

`Station` made frozen with `@dataclass(frozen=True)`.

1. Assigning to a field raises `FrozenInstanceError`. The student must catch it and print the message so the script does not crash. Check for the `try` / `except FrozenInstanceError` around the assignment.
2. A `set` containing three `Station` objects, two of which are identical, has length `2`. The two identical objects are deduplicated.

Subjective comment: besides immutability, `frozen=True` makes the dataclass hashable, so instances can be placed in a set or used as dictionary keys. That is what makes the deduplication in part 2 work.

### Dataclass Q3 — **Objective (structure) + Subjective (comment)**

`StationBatch` dataclass with:

- `region: str`
- `stations: list[Station]` defaulting to empty, correctly written as `field(default_factory=list)`.
- `add(self, station: Station) -> None` that appends.
- `highest(self) -> Station | None` returning the station with the greatest elevation, or `None` when the batch is empty.

Every method has a type-hinted signature and a docstring.

Subjective comment: the student first tries `stations: list[Station] = []`, runs it, and pastes the error, which is `ValueError: mutable default <class 'list'> for field stations is not allowed`. The comment explains that a bare default is created once when the class is defined, so every instance would share the same list, and dataclasses refuse this to prevent that shared-state bug. The fix is `field(default_factory=list)`, which calls `list()` fresh for each instance.

Reference for `highest`:

```python
def highest(self) -> Station | None:
    """Return the station with the greatest elevation, or None if empty."""
    if not self.stations:
        return None
    return max(self.stations, key=lambda s: s.elevation)
```

## Pydantic

### Pydantic Q1 — **Objective (structure)**

A Pydantic `Reading` model with four constrained fields:

- `station_id: str` with `min_length=3`
- `timestamp: str`, required (no default)
- `temperature_c: float` with `ge=-90, le=60`
- `humidity: float` with `ge=0, le=100`

One valid `Reading` is constructed and printed. Reference:

```python
from pydantic import BaseModel, Field

class Reading(BaseModel):
    station_id: str = Field(min_length=3)
    timestamp: str
    temperature_c: float = Field(ge=-90, le=60)
    humidity: float = Field(ge=0, le=100)
```

### Pydantic Q2 — **Objective (results) + Subjective (comment)**

Three separate failures, each wrapped in its own `try` / `except ValidationError` so the script keeps running, and the error is printed each time:

1. A missing required field raises (reported as "Field required").
2. `temperature_c=150.0` raises (violates `le=60`).
3. `humidity="very humid"` raises (cannot be parsed as a float).

Then a `Reading` where `temperature_c` is the string `"21.5"` and `humidity` is the integer `40`. After construction, both are floats: `type(reading.temperature_c)` and `type(reading.humidity)` both print `<class 'float'>`.

Subjective comment: Pydantic accepts `"21.5"` because it has exactly one reasonable interpretation as a float, and it rejects `"very humid"` because that string has no numeric interpretation. The rule is that Pydantic coerces a value when there is a single unambiguous conversion, and refuses when the conversion would require guessing.

### Pydantic Q3 — **Objective (result) + Subjective (comment)**

One construction that triggers several errors at once: a too-short `station_id`, a missing `timestamp`, and a non-numeric `temperature_c`, all in one `try` block. The student loops over `e.errors()` and prints the `loc` and `msg` for each.

Objective: **three** errors are reported, one per bad field. Check the loop prints all three rather than stopping at the first.

Subjective comment: reporting all errors at once is more useful because the student can fix every problem in a malformed payload in one pass, instead of fixing one field, re-running, discovering the next error, and repeating.

### Pydantic Q4 — **Objective (result) + Subjective (comment)**

A `model_validator(mode="after")` on `Reading` that rejects any reading where `humidity` is exactly `0.0` **and** `temperature_c` is below `-40`. A valid reading still constructs, and the bad combination raises `ValidationError`.

Reference:

```python
from pydantic import model_validator

@model_validator(mode="after")
def reject_failed_sensor(self):
    """A humidity of exactly 0 with a very low temperature indicates sensor failure."""
    if self.humidity == 0.0 and self.temperature_c < -40:
        raise ValueError("humidity 0 with temperature below -40 indicates a failed sensor")
    return self
```

Subjective comment: this rule cannot be expressed with `Field` constraints alone because it compares two fields against each other. `Field` constraints check one field in isolation, and neither `humidity == 0.0` nor `temperature_c < -40` is invalid on its own. Only their combination is invalid, and a `model_validator(mode="after")` is the tool that runs once every field is populated so both can be read together.

## pytest

These are real pytest tests inside `warmup_01.py`, named `test_*`, run with `pytest warmup_01.py -v`.

### pytest Q1 — **Objective (result) + Subjective (comment)**

`celsius_to_fahrenheit(celsius: float) -> float` with a docstring, and `test_celsius_to_fahrenheit()` asserting:

- 0 C is 32 F
- 100 C is 212 F
- 37 C is approximately 98.6 F

The 37 C case fails with a plain `==` because `37 * 9 / 5 + 32` is `98.60000000000001` in binary floating point, not exactly `98.6`. It must pass with `pytest.approx(98.6)`.

Subjective comment: `pytest.approx` was necessary because floating-point arithmetic does not produce an exact `98.6`, so a plain `==` comparison fails on a correct function. `pytest.approx` compares within a small tolerance.

### pytest Q2 — **Objective (result) + Subjective (comment)**

`mean(values: list[float]) -> float` that raises `ValueError` with a useful message when `values` is empty. `test_mean_of_empty_raises()` uses `pytest.raises(ValueError, match=...)` where the match pattern is a word the student expects in the message (for example "empty").

Subjective comment: `pytest.raises(ValueError)` alone would pass on *any* `ValueError`, including one accidentally raised by a mistake in the test setup. Adding `match=` confirms the error is the specific one the code is meant to raise, so the test cannot pass for the wrong reason.

### pytest Q3 — **Objective (result) + Subjective (comment)**

`test_mean_values()` using `@pytest.mark.parametrize` with at least four input/output pairs, including a single-element list and a list containing negative numbers. Each parametrized case appears on its own line in `pytest -v` output. The student pastes the summary line (for example `4 passed`) into a comment.

Subjective comment: one parametrized test with four cases is better than four near-identical test functions because the test logic is written once, each case still reports its own pass or fail, and adding a new case is one line rather than a new function.

### pytest Q4 — **Objective (result) + Subjective (comment)**

The student deliberately breaks `celsius_to_fahrenheit` (for example, changing `9 / 5` to `9 / 4`), runs the test, pastes the failure output into a comment, and then fixes the function.

Subjective comment: pytest showed the actual computed value against the expected value (for example `assert 257.0 == 212.0`), naming both sides of the failed assertion. That is more useful than a bare "assertion failed" because the student can see exactly what the function produced and what was expected, which points straight at the bug.

---

# Part 2: Project — The `weatherkit` Package

The input is `weather_raw.json`, the **hourly** Open-Meteo response for Charlotte, NC, containing **168 hourly observations** (7 days). The measurements are columnar: `time`, `temperature_2m`, and `precipitation` are three parallel lists under the `"hourly"` key. This shape is deliberately different from the daily response in the Pydantic lesson, so the student applies the same validation pattern to an unfamiliar shape.

Confirmed facts about the supplied file, for checking student output:

- 168 hourly observations.
- `latitude` about 35.22, `longitude` about -80.83, `timezone` `"GMT"`, `elevation` `254.0`.
- The observations span 2026-04-08 through 2026-04-14, and **every one of the seven days has exactly 24 hours**. This matters for the self-check below.

## Task 1: Package Skeleton — **Objective (structure)**

- `weatherkit/` directory with an `__init__.py`.
- A `tests/` directory.
- An **empty** `conftest.py` at the root of `assignments_01/`.
- Running `pytest` from `assignments_01/` collects zero tests without error at this stage.
- `__init__.py` re-exports the main classes so callers can write `from weatherkit import HourlyReading` rather than `from weatherkit.records import HourlyReading`. The re-exports grow as each piece is built.

This is the failure point named in the mentor note. If the tests do not collect, check for the empty `conftest.py` at the root of `assignments_01/` before anything else. Its presence tells pytest to add `assignments_01/` to the module search path, so `from weatherkit import ...` resolves. Without it, pytest searches from `tests/`, where `weatherkit/` is not visible, and every test fails with `ModuleNotFoundError: No module named 'weatherkit'`.

## Task 2: The Boundary — `schemas.py` — **Objective (structure + result)**

Two Pydantic models with docstrings:

- `HourlyBlock` with `time: list[str]`, `temperature_2m: list[float]`, `precipitation: list[float]`, plus a `model_validator(mode="after")` that rejects the response when the three lists are not all the same length.
- `WeatherResponse` with `latitude` constrained to -90…90, `longitude` constrained to -180…180, `timezone`, `elevation`, and a nested `hourly: HourlyBlock`.

Reference:

```python
from pydantic import BaseModel, Field, model_validator

class HourlyBlock(BaseModel):
    """The columnar hourly arrays from an Open-Meteo response."""
    time: list[str]
    temperature_2m: list[float]
    precipitation: list[float]

    @model_validator(mode="after")
    def lists_same_length(self):
        """All three parallel lists must be the same length."""
        if not (len(self.time) == len(self.temperature_2m) == len(self.precipitation)):
            raise ValueError("hourly lists must all be the same length")
        return self

class WeatherResponse(BaseModel):
    """A validated hourly Open-Meteo weather response."""
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str
    elevation: float
    hourly: HourlyBlock
```

Objective result: validating `weather_raw.json` with `WeatherResponse.model_validate(...)` and printing the latitude, timezone, and the number of hourly observations shows **168** observations. The latitude is about 35.22 and the timezone is `"GMT"`.

The reason the length validator matters: if `time` had 168 entries and `temperature_2m` had 167, indexing them in parallel would silently pair the wrong readings together, producing output that looks correct but is not.

## Task 3: Inside the Boundary — `records.py` — **Objective (structure) + Subjective (comment)**

- A **dataclass** `HourlyReading` with `timestamp: str`, `temperature_c: float`, `precipitation_mm: float`, and a docstring documenting the units.
- `to_readings(response: WeatherResponse) -> list[HourlyReading]` that converts the columnar `hourly` block into one `HourlyReading` per hour, preserving order, with a docstring containing `Args:` and `Returns:` sections.

Reference:

```python
from dataclasses import dataclass

@dataclass
class HourlyReading:
    """One hour of weather. temperature_c in Celsius, precipitation_mm in millimeters."""
    timestamp: str
    temperature_c: float
    precipitation_mm: float

def to_readings(response: WeatherResponse) -> list[HourlyReading]:
    """Convert a validated columnar response into one reading per hour.

    Args:
        response: A validated WeatherResponse.

    Returns:
        One HourlyReading per hour, in the order returned by the API.
    """
    h = response.hourly
    return [
        HourlyReading(h.time[i], h.temperature_2m[i], h.precipitation[i])
        for i in range(len(h.time))
    ]
```

Subjective comment: a good answer identifies where the boundary is. `WeatherResponse` describes *outside* data that arrives from the API and must be checked, so it is a Pydantic model. `HourlyReading` describes *inside* data that the student's own code produces from an already-validated response, so it is a dataclass. The data is validated once at the boundary, and validating it again inside would be wasted work.

## Task 4: The Aggregation — `summarize.py` — **Objective (structure + exact numbers) + Subjective**

- A dataclass `DailySummary` with `date: str`, `temp_max: float`, `temp_min: float`, `precipitation_sum: float`, `hours_observed: int`, and a `temp_range() -> float` method (`temp_max - temp_min`).
- A class `DailyAggregator`:
  - `__init__(self, min_hours: int = 24)`.
  - `summarize(readings: list[HourlyReading]) -> list[DailySummary]` that groups readings by calendar date (the first 10 characters of the timestamp), computes the max and min temperature and the total precipitation for each date, records how many hours contributed, drops any day with fewer than `min_hours` observations, and returns the summaries sorted by date.
  - `incomplete_days(readings: list[HourlyReading]) -> list[str]` returning the dates that were dropped.

Everything has type hints and docstrings.

### Self-check — **Objective (exact numbers)**

Running the aggregator on the full file with the default `min_hours=24` produces exactly **7 summaries**, and the first two rows are:

| date | temp_max | temp_min | precipitation_sum | hours_observed |
|---|---|---|---|---|
| 2026-04-08 | 16.8 | 7.8 | 0.0 | 24 |
| 2026-04-09 | 19.3 | 3.7 | 0.0 | 24 |

These are confirmed exact values. All seven days have 24 hours, so at the default `min_hours=24` no day is dropped and `incomplete_days()` returns an empty list on the full file. If a student's numbers differ, the usual cause is grouping on the whole timestamp string instead of the first 10 characters, which splits each calendar day into 24 separate one-hour groups.

## Task 5: The Test Suite — **Objective (structure) + must pass from `assignments_01/`**

The suite must pass when `pytest` is run from `assignments_01/`. Verify the required test count and behavior rather than exact wording.

**`tests/test_schemas.py`** — at least four tests:

1. A valid response validates, and `hourly.time` has 168 entries. The real JSON is loaded via `Path(__file__).parent.parent / "weather_raw.json"`.
2. A latitude of `200.0` raises `ValidationError`.
3. Mismatched list lengths raise `ValidationError`, using a small hand-written dict with one list one element short.
4. A `null` inside `temperature_2m` raises `ValidationError`.

Check that test 1 uses `Path(__file__).parent.parent / "weather_raw.json"` and includes a comment explaining that a plain relative path is unreliable because it resolves against the current working directory, which changes depending on where pytest is launched, whereas the `__file__`-based path is anchored to the test file itself.

**`tests/test_records.py`** — at least three tests:

1. `to_readings` returns one reading per hour in order, checked by the first and last timestamps.
2. The values in reading *i* match index *i* of each input list, which catches readings paired with the wrong timestamps.
3. Two `HourlyReading` objects with identical fields compare equal.

**`tests/test_summarize.py`** — at least five tests, using a `@pytest.fixture` for shared input:

1. Grouping works: a hand-built list spanning two dates produces two summaries.
2. `temp_max` and `temp_min` are correct for a known small input.
3. `precipitation_sum` adds up correctly, checked with `pytest.approx`.
4. A day with fewer than `min_hours` readings is dropped, and its date appears in `incomplete_days()`.
5. Lowering `min_hours` causes that same day to be kept, proving the parameter is actually consulted.

At least one test in the whole suite uses `@pytest.mark.parametrize`.

The student is also asked to deliberately break one function in `weatherkit/`, confirm the relevant test fails, and note in a comment which test caught the change. Check for that comment.

## Task 6: The Script — `report.py` — **Objective (structure) + Subjective (comment)**

A script that loads `weather_raw.json`, validates it into a `WeatherResponse`, converts it to `HourlyReading` objects, aggregates to `DailySummary` objects, prints a readable per-day table (date, high, low, total precipitation, and temperature range), and prints a warning line listing any incomplete days that were dropped. On the supplied file with the default `min_hours=24`, seven rows print and the dropped-days warning is empty.

The work is in a `main()` function called under an `if __name__ == "__main__":` guard.

Subjective comment: without the guard, `main()` would run at import time. If someone imported `report.py` to reuse one of its helper functions, the whole report would execute as a side effect of the import, printing output and doing work the importer did not ask for. The guard runs `main()` only when the file is executed directly.

## Task 7: Reflection — **Subjective**

A comment block at the bottom of `report.py` answering three questions. Good answers engage with the trade-offs rather than restating the question.

1. **Rejecting the whole file on a single `null` temperature.** A good answer names one situation where strict rejection is right (for example, a training dataset where a silent `NaN` would corrupt a model, so failing loudly at the boundary is safer) and one where tolerance is better (for example, a monitoring dashboard that should still show 167 good hours rather than nothing). The schema change to tolerate the gap is widening the type to `list[float | None]`, which records the decision to tolerate missing values in the schema itself.
2. **`min_hours=24` when a pipeline runs at noon.** A good answer explains that a day only half over has roughly 12 hours of data, so its "daily maximum" is really a half-day maximum and cannot be trusted. `incomplete_days()` helps because the partial day is dropped from the summaries but its date is still reported, so the gap is visible rather than silent.
3. **Package rather than one file, and Week 10.** A good answer names one concrete benefit, such as a pipeline being able to `import weatherkit` and call its classes directly, testing the package in isolation, or reorganizing internal files without breaking callers because the public interface is defined in `__init__.py`.

---

# Optional Extensions

**Do not fail a student for omitting any of these.** They are marked "(Optional)".

- **Extension A** — `HourlyBlock` tolerates `None` in `temperature_2m` and `precipitation` (type widened to `list[float | None]`); `to_readings` and `DailyAggregator` skip missing values while still counting the hours correctly; tests cover a day with a gap.
- **Extension B** — a `RunningWindow` class returning, per day, the start hour and length of the longest run of consecutive hours inside a configurable comfortable temperature range with zero precipitation; boundary tests for runs at the start and end of a day and a day with no qualifying hours.
- **Extension C** — a minimal `pyproject.toml` and `uv pip install -e .`; tests then pass from any directory, not only `assignments_01/`; a comment explaining that installing the package added it to the environment's import path, so `conftest.py` is no longer what makes it importable.

---

# Running and Verification

The grader runs `pytest` from inside `assignments_01/`. To reproduce a student's result:

```bash
cd assignments_01
uv pip install pydantic pytest
pytest -v            # discovers and runs the tests/ suite
pytest warmup_01.py -v   # runs the warmup tests, which a bare pytest does not collect
python report.py     # prints the 7-row table and the (empty) dropped-days warning
```

A passing submission shows the `tests/` suite green from `assignments_01/`, the warmup tests green under the explicit `pytest warmup_01.py -v` command, and `report.py` printing seven daily rows. If the `tests/` suite fails to collect with `ModuleNotFoundError: No module named 'weatherkit'`, the empty `conftest.py` at the root of `assignments_01/` is missing or misplaced; that is the first thing to check.
