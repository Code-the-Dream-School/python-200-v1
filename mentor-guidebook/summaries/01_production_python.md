# Week 1 Mentor Summary: Production Python

**Lesson files:** `lessons/01_production_python.md` (overview) and five lessons in `lessons/01_production_python/`
**Assignment file:** `assignments/01_production_python.md`
**Answer key:** `mentor-guidebook/answer-key/assignment_01_key.md`
**Slides:** `mentor-guidebook/slides/01_production_python.pdf`

**Learning objective:** Students build `weatherkit`, a small importable package that validates a raw Open-Meteo weather response with Pydantic, converts it into dataclass records, and aggregates hourly readings into daily summaries. They test the package with `pytest` and run it from a script that uses the `if __name__ == "__main__"` guard.

**Where this fits:** This week builds on Python for Data Analysis, which taught students to load and plot data. Week 4 reuses the package layout, the empty `conftest.py`, and `pytest` to turn the Week 3 model into a `weather_model` package. Week 9 builds the extract step of a cloud pipeline on the same Open-Meteo data, and Week 10 imports the Week 4 package. Later bridge assignments also use `pytest` fixtures.

---

## Lesson Overview

Every lesson uses the same running example: a `DailyWeather` record with a date, a high and low temperature, precipitation, and wind speed. A day is good for running when the high is between 7 and 26 °C, the low is at least 0 °C, rain is under 3 mm, and wind is under 30 km/h. Later weeks use the same rule.

| Lesson | What students learn |
|---|---|
| **1. Classes and Objects** | Three problems with dictionaries: typos create new keys silently, nothing enforces the structure, and the functions are not connected to the data. `__init__`, `self`, attributes, and methods. `__repr__` for readable printing. A `RunningConditions` class that stores thresholds once and applies them to many days, which has the same structure as the Week 4 `WeatherClassifier`. When a plain function is the better choice. |
| **2. Dataclasses, Type Hints, and Docstrings** | Type hint syntax, including `list[float]` and `float \| None`. Python does not enforce type hints at runtime. `@dataclass` generates `__init__`, `__repr__`, and `__eq__`. The mutable-default error and `field(default_factory=list)`. `frozen=True`, which also makes instances hashable. Google-style docstrings. |
| **3. Validating Data at the Boundary** | Pydantic `BaseModel`, `ValidationError`, and safe coercion (`"14.8"` becomes a float, `"hot"` is rejected). `Field` constraints such as `ge` and `le`. `field_validator` for one field and `model_validator(mode="after")` for rules across fields. Nested models for the columnar Open-Meteo daily response. `model_validate`, `model_dump`, and when to use a dataclass instead. |
| **4. Testing with pytest** | Test discovery rules, plain `assert`, and pytest's detailed failure output. `pytest.approx` for floats, because `20.1 - 10.7` is `9.400000000000002`. `pytest.raises` with `match=`, `@pytest.mark.parametrize`, boundary tests, fixtures, and `conftest.py`. The lesson writes files to disk and runs pytest through `subprocess`, so it works as a notebook. |
| **5. Modules and Project Structure** | Modules, packages, and `__init__.py` as the public entry point. Why to avoid star imports. Library modules compared with scripts, and the `__main__` guard. A layout with separate zones for the package, `tests/`, and scripts. Why `ModuleNotFoundError` appears when pytest runs from the wrong directory, and the three fixes. |

---

## Assignment Deliverables

**Setup:** Students work in `assignments_01/` and copy `weather_raw.json` from `assignments/resources/` into it. They also create an **empty** `conftest.py` at the top of `assignments_01/`. They install `pydantic` and `pytest`.

**Grading:** The project numbers are fixed, because every student uses the same `weather_raw.json`. The rubric enforces folder layout through the `pytest` run only, so do not fail a student for a file split you cannot verify. Class, method, and function names are exact, because the tests depend on them. Warmup values that students choose, such as locations and readings, vary.

| Part | File | What students do | Concepts practiced |
|---|---|---|---|
| Warmup | `warmup_01.py` | Fourteen short exercises: `Thermometer` and `TemperatureAlert` classes, a frozen `Station` dataclass and `StationBatch`, a constrained Pydantic `Reading` model with a `model_validator`, and four pytest questions. | Everything in Lessons 1–4 |
| Project, Tasks 1–2 | `weatherkit/__init__.py`, `weatherkit/schemas.py` | Builds the package skeleton and the Pydantic models `HourlyBlock` and `WeatherResponse`. A validator rejects lists of unequal length. Validating the file reports 168 hourly observations. | Pydantic, nested models |
| Project, Tasks 3–4 | `weatherkit/records.py`, `weatherkit/summarize.py` | Writes the `HourlyReading` dataclass and `to_readings()`, then `DailySummary` and `DailyAggregator` with `min_hours=24` and `incomplete_days()`. The self-check expects 7 summaries. | Dataclasses, the boundary, classes |
| Project, Task 5 | `tests/` | Writes at least 12 tests across three files, with a fixture and at least one `parametrize`. All tests must pass when `pytest` runs from `assignments_01/`. | pytest |
| Project, Tasks 6–7 | `report.py` | Prints a daily table and a warning about dropped days from a `main()` function under the `__main__` guard. A comment block answers three reflection questions. | Scripts compared with libraries |

**Optional:** Extension A (tolerate missing readings), Extension B (a `RunningWindow` class), and Extension C (make the package installable with `pyproject.toml`). These are marked "(Optional)" and are not graded.

**Submission:** A link to an open pull request in the student's `python200-homework` repository. The grader runs `pytest` from inside `assignments_01/`.

---

## Key Concepts

These short explanations cover the ideas students ask about most this week. Expand any one you need.

<details>
<summary><strong>Type hints, dataclasses, and Pydantic: where the boundary is</strong></summary>

All three tools use the same field syntax, so students often think they do the same job. Only Pydantic checks values. Python ignores type hints at runtime, and a dataclass assigns whatever it receives. Lesson 2 shows `DailyWeather(temp_max="hot", temp_min=None, ...)` succeeding with no error.

The course rule is to validate once at the **boundary**, the place where outside data enters the program. API responses, files, and user input cross the boundary, so they get a Pydantic model. Records your own code builds from validated data are already inside, so a dataclass is enough.

In the assignment, `WeatherResponse` and `HourlyBlock` describe the raw JSON, so they are Pydantic models. `HourlyReading` is built by `to_readings()` from an already-validated response, so it is a dataclass. Task 3 asks students to explain this choice. A good answer names the boundary. An answer that says only "Pydantic is slower" misses the point.

</details>

<details>
<summary><strong>Why the empty `conftest.py` makes the imports work</strong></summary>

When a test runs `from weatherkit import ...`, Python searches the directories listed in `sys.path`. A bare `pytest` command does not add the current directory to that list. It adds the test file's directory, `tests/`, and `weatherkit/` is not inside `tests/`. The result is `ModuleNotFoundError: No module named 'weatherkit'` for every test.

Lesson 5 gives three fixes:

- Run `python -m pytest` from the project root. The `-m` form adds the current directory to `sys.path`.
- Put an empty `conftest.py` in the project root. pytest adds the directory of the topmost `conftest.py` to `sys.path`. The assignment uses this fix, because the grader runs a bare `pytest`.
- Install the package with `uv pip install -e .`. This needs a `pyproject.toml` file and is Extension C.

The file must stay empty and must sit at the top of `assignments_01/`, not inside `tests/`. Week 4 uses the same setup.

</details>

<details>
<summary><strong>Pydantic validation: coercion, `Field`, and the two validator types</strong></summary>

Pydantic converts a value when there is exactly one reasonable interpretation. The string `"21.5"` and the integer `40` both become floats. The string `"very humid"` has no numeric meaning, so Pydantic rejects it. This matters because JSON and CSV files often deliver numbers as text.

Students choose among three tools:

- **`Field(ge=..., le=..., min_length=...)`** checks one field against fixed limits, such as a temperature between -90 and 60.
- **`field_validator`** runs custom code on one field, such as checking that a date is a real calendar day. It needs `@classmethod` below it.
- **`model_validator(mode="after")`** runs after every field is set, so it can compare fields.

Both the warmup rule (humidity of exactly 0.0 together with a temperature below -40) and the project rule (three lists of equal length) compare fields. They need a `model_validator`. Lesson 3 notes that a validator must return the value, and a `model_validator` returns `self`.

</details>

---

## FAQs and Common Trouble Spots

**1. "Every test fails with `ModuleNotFoundError: No module named 'weatherkit'`."**
Check for the empty `conftest.py` at the top of `assignments_01/` first. The answer key calls this the most common failure point. Then confirm that the student runs `pytest` from `assignments_01/` and not from inside `tests/`.

**2. "pytest Question 1 says the 36.6 °C test fails with `==`. Why?"**
Floats are stored in binary, so `36.6 * 9 / 5 + 32` gives `97.88000000000001`, not `97.88`. This happens with every common way of writing the formula. The student should use `pytest.approx` and explain that floats need a tolerance. An older version of the question used 37 °C, which gives exactly `98.6` with `celsius * 9 / 5 + 32`, so `==` passed. If a student worked from that version and noticed the test passed, give credit for the observation.

**3. "My warmup script crashes partway through, or pytest cannot collect it."**
Dataclass Question 3 asks students to try `stations: list[Station] = []` and copy the error into a comment. Python raises the `ValueError` when it defines the class, which stops the script and pytest collection. The broken version must not stay in the running code. Students should paste the error into a comment and keep only the `field(default_factory=list)` version.

**4. "pytest does not run my warmup tests."**
This is expected. A bare `pytest` does not discover `warmup_01.py`, because the file name does not match `test_*.py`. Students run those tests with `pytest warmup_01.py -v`. The rubric says not to fail a student for this.

**5. "My daily summaries do not match the self-check table."**
The usual cause is grouping on the full timestamp, such as `2026-04-08T00:00`, instead of its first 10 characters. That produces 168 groups of one hour each. The correct output has 7 summaries, and the first row is `2026-04-08`, 16.8, 7.8, 0.0, 24.

**6. "`incomplete_days()` returns an empty list. Is my code wrong?"**
The code is probably correct. All seven days in `weather_raw.json` have exactly 24 hours, so no day is dropped with the default `min_hours=24`. To test dropping (Task 5, tests 4 and 5), students need a small hand-built list with a short day.

**7. "My schema test cannot find `weather_raw.json`."**
A plain relative path resolves against the directory where pytest was started, and that directory changes. Task 5 requires `Path(__file__).parent.parent / "weather_raw.json"`, which is anchored to the test file. Students also need a comment explaining why.
