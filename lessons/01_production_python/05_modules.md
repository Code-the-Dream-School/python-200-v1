# Modules and Project Structure

You now have four tools: classes, dataclasses with type hints and docstrings, Pydantic schemas, and pytest. This lesson is about where to *put* them.

This may sound like simple tidiness, but it is not. A notebook that has grown to 800 cells and a script that has grown to 900 lines are the two most common ways a working analysis becomes impossible to maintain. Both have the same cause: everything lives in one place, so nothing can be reused, tested, or changed independently.

## Modules

A **module** is a `.py` file. That is the entire definition. Every script you have written is already a module, although you have not yet imported one of your own.

The cells below build a small project on disk so the lesson runs end to end. In practice you would create these files in your editor.

```python
import subprocess
import sys
from pathlib import Path

PROJECT = Path("weather_project")
(PROJECT / "weatherkit").mkdir(parents=True, exist_ok=True)
(PROJECT / "tests").mkdir(exist_ok=True)

print(f"Building project in: {PROJECT.resolve()}")
```

### Splitting code into files

We will start with the record types. They belong in their own module because they are the vocabulary that everything else uses:

```python
(PROJECT / "weatherkit" / "records.py").write_text('''
"""Record types for daily weather observations."""

from dataclasses import dataclass


@dataclass
class DailyWeather:
    """One day of observed weather at a single location.

    Attributes:
        date: Observation date as an ISO string, e.g. "2023-06-15".
        temp_max: Daily high temperature in degrees Celsius.
        temp_min: Daily low temperature in degrees Celsius.
        precipitation: Total precipitation in millimeters.
        wind_speed: Maximum wind speed in km/h.
    """

    date: str
    temp_max: float
    temp_min: float
    precipitation: float
    wind_speed: float

    def temp_range(self) -> float:
        """The day's temperature swing in Celsius (high minus low)."""
        return self.temp_max - self.temp_min

    def to_dict(self) -> dict:
        """Convert to a plain dict, ready for a database insert."""
        return {
            "date": self.date,
            "temp_max": self.temp_max,
            "temp_min": self.temp_min,
            "precipitation": self.precipitation,
            "wind_speed": self.wind_speed,
        }
''')
print("wrote weatherkit/records.py")
```

The logic that operates on those records goes in a second module:

```python
(PROJECT / "weatherkit" / "conditions.py").write_text('''
"""Deciding whether a day is suitable for running."""

from dataclasses import dataclass

from weatherkit.records import DailyWeather


@dataclass
class RunningConditions:
    """Thresholds defining a good day for an outdoor run.

    Attributes:
        min_temp: Lowest acceptable daily high, in Celsius.
        max_temp: Highest acceptable daily high, in Celsius.
        max_precip: Maximum tolerable precipitation, in millimeters.
        max_wind: Maximum tolerable wind speed, in km/h.
    """

    min_temp: float = 7.0
    max_temp: float = 26.0
    max_precip: float = 3.0
    max_wind: float = 30.0

    def is_good(self, day: DailyWeather) -> bool:
        """Whether a single day meets these conditions."""
        return (
            self.min_temp <= day.temp_max <= self.max_temp
            and day.temp_min >= 0
            and day.precipitation < self.max_precip
            and day.wind_speed < self.max_wind
        )

    def label_all(self, days: list) -> list:
        """Label every record in a list. Returns one bool per record."""
        return [self.is_good(day) for day in days]
''')
print("wrote weatherkit/conditions.py")
```

Notice the import at the top of `conditions.py`:

```
from weatherkit.records import DailyWeather
```

That line is one module using another. The rule for splitting code is **cohesion**, which means that things which change together belong together. Record definitions change when the shape of the data changes. Running-condition logic changes when the criteria change. Because those are two different reasons, they belong in two different files.

### Import forms

There are three you will use constantly:

```
import weatherkit.records                          # import the module
from weatherkit.records import DailyWeather        # import one name from it
from weatherkit.records import DailyWeather as DW  # ...and rename it
```

The middle form is the most common and the most readable, so use it whenever you can.

There is a fourth form, which you should avoid:

```
from weatherkit.records import *   # don't
```

A star import copies every public name into your namespace. Six months later, nobody, including you, can tell where `DailyWeather` came from. If two modules define the same name, one of them replaces the other without any warning.

## Packages

A **package** is a directory of modules. Turn one into a package by adding an `__init__.py` file:

```python
(PROJECT / "weatherkit" / "__init__.py").write_text('''
"""weatherkit: tools for working with daily weather observations."""

from weatherkit.conditions import RunningConditions
from weatherkit.records import DailyWeather

__all__ = ["DailyWeather", "RunningConditions"]
''')
print("wrote weatherkit/__init__.py")
```

`__init__.py` runs when the package is first imported. It defines the package's public entry point, and it has one genuinely useful job: deciding which names users of your package can reach easily.

Because of the imports above, both of these now work:

```
from weatherkit.records import DailyWeather        # the full path
from weatherkit import DailyWeather                # the shortcut
```

The second form is easier for anyone using your package, and it means you can reorganize your internal files later without breaking their code. This is the purpose of a public entry point: callers depend on `weatherkit` itself, not on which file happens to contain a particular name today.

`__all__` lists the names that make up your public interface. It documents those names for readers, and it controls which names `from weatherkit import *` would import.

> An `__init__.py` file can be empty, and often is. Modern Python can even treat a directory without one as a package. Include it anyway. It states your intent explicitly, it is what most tools expect, and it gives you a place to define your public entry point when you need one.

## Scripts vs. Libraries

There are two kinds of Python file, and confusing them causes real problems.

A **library module** defines things. Importing it should define classes and functions and do nothing else. It should not print, download, or write files.

A **script** performs actions. You run it, it does its work, and it finishes.

Problems arise when a single file tries to be both:

```
# bad_script.py -- defines a function AND runs it at import time
def summarize(days):
    return f"{len(days)} days"

print(summarize(load_everything()))   # runs on import!
```

If you import `bad_script` in order to use its `summarize` function, you also trigger a data load and a print statement. If you import it inside a test, the test suite does the same. Any code at module level runs the moment the file is imported, and an `import` statement should not cause side effects.

### The `__name__ == "__main__"` guard

Python sets a variable called `__name__` in every module. When you *run* a file directly, its `__name__` is the string `"__main__"`. When you *import* it, `__name__` is the module's name instead. So this condition means "only when run directly, not when imported":

```python
(PROJECT / "report.py").write_text('''
"""Print a running-conditions report for a few sample days."""

from weatherkit import DailyWeather, RunningConditions


SAMPLE_DAYS = [
    DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2),
    DailyWeather("2023-06-16", 27.3, 16.2, 2.4, 18.7),
    DailyWeather("2023-01-10", 2.0, -6.0, 0.0, 22.0),
]


def build_report(days: list, conditions: RunningConditions) -> str:
    """Format a one-line-per-day running report."""
    lines = []
    for day, good in zip(days, conditions.label_all(days)):
        verdict = "RUN " if good else "SKIP"
        lines.append(f"{day.date}  {verdict}  high {day.temp_max:5.1f}C  "
                     f"rain {day.precipitation:4.1f}mm")
    return "\\n".join(lines)


def main() -> None:
    """Entry point: build and print the report."""
    print(build_report(SAMPLE_DAYS, RunningConditions()))


if __name__ == "__main__":
    main()
''')

result = subprocess.run([sys.executable, "report.py"], cwd=PROJECT,
                        capture_output=True, text=True)
print(result.stdout or result.stderr)
```

Run it directly and `main()` fires. Import `build_report` from it and nothing happens except the definitions. You get both without conflict.

Defining a `main()` function is a convention worth adopting. Put the actual work in a named function and keep the guarded block down to a single call. This keeps `main` itself both testable and importable.

## Project Layout

Use the following layout, which is also the one your Week 4 project will follow:

```text
weather_project/
├── weatherkit/              <- the package: importable library code
│   ├── __init__.py          <- front door: what users import
│   ├── records.py           <- data types
│   └── conditions.py        <- logic
├── tests/                   <- tests, mirroring the package
│   ├── test_records.py
│   └── test_conditions.py
└── report.py                <- a script that uses the package
```

There are three zones, and each has one job. `weatherkit/` contains code that other files import, and it never runs on its own. `tests/` proves that the code works. `report.py` is an entry point that a person runs.

We separate them because they change for different reasons and are used by different people. Someone importing `weatherkit` does not need your report script. Someone running the report does not need your tests. Most importantly, the package can now be reused by *several* scripts. That is exactly what happens in Week 10, when a pipeline you have not written yet imports your Week 4 model component.

## Testing a Package

Tests import your package the same way any other caller does:

```python
(PROJECT / "tests" / "test_records.py").write_text('''
import pytest

from weatherkit import DailyWeather


def test_temp_range():
    day = DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2)
    assert day.temp_range() == pytest.approx(9.4)


def test_to_dict_round_trips():
    day = DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2)
    assert DailyWeather(**day.to_dict()) == day


def test_records_are_compared_by_value():
    a = DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2)
    b = DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2)
    assert a == b
''')

(PROJECT / "tests" / "test_conditions.py").write_text('''
import pytest

from weatherkit import DailyWeather, RunningConditions


@pytest.fixture
def sample_days() -> list:
    """Three days: mild, warm, and freezing."""
    return [
        DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2),
        DailyWeather("2023-07-20", 30.0, 21.0, 0.0, 8.0),
        DailyWeather("2023-01-10", 2.0, -6.0, 0.0, 22.0),
    ]


def test_default_conditions_accept_only_the_mild_day(sample_days):
    assert RunningConditions().label_all(sample_days) == [True, False, False]


def test_raising_max_temp_accepts_the_warm_day(sample_days):
    heat_tolerant = RunningConditions(max_temp=32.0)
    assert heat_tolerant.label_all(sample_days) == [True, True, False]


def test_freezing_day_is_rejected_by_every_configuration(sample_days):
    permissive = RunningConditions(min_temp=-50, max_temp=50,
                                   max_precip=1000, max_wind=1000)
    assert permissive.is_good(sample_days[2]) is False
''')
print("wrote tests/")
```

Run them from the **project root** -- the directory containing both `weatherkit/` and `tests/`:

```python
result = subprocess.run([sys.executable, "-m", "pytest", "-v"], cwd=PROJECT,
                        capture_output=True, text=True)
print(result.stdout[-3000:])
```

### Why the working directory matters

`from weatherkit import DailyWeather` works because Python searches for `weatherkit/` in a list of directories called `sys.path`, and the directory you run from is on that list. If you run pytest from the project root, `weatherkit/` is visible. If you run it from inside `tests/`, it is not:

```python
result = subprocess.run([sys.executable, "-m", "pytest", "test_records.py"],
                        cwd=PROJECT / "tests", capture_output=True, text=True)
tail = [ln for ln in result.stdout.splitlines() if "Error" in ln or "error" in ln]
print("\n".join(tail) or result.stdout[-800:])
```

The result is `ModuleNotFoundError: No module named 'weatherkit'`. This is the most common source of confusion when people begin splitting projects into packages. Two things fix it, and you usually want both.

First, run the command from the project root, not from inside `tests/`. Second, run it as `python -m pytest` rather than a bare `pytest`. The `-m` form adds the current directory to `sys.path`, which a bare `pytest` does not do. When your tests import your own package, as they do here, the plain `pytest` command run from the project root is often *not* enough on its own, because pytest searches from the test file's own directory instead. `python -m pytest` from the project root is the reliable combination.

There is a third option that lets a bare `pytest` work: place an empty file named `conftest.py` in the project root. pytest treats the directory containing the topmost `conftest.py` as a root and adds it to `sys.path`, so `weatherkit/` becomes visible again. The assignment this week uses that approach, so a bare `pytest` run from `assignments_01/` finds your package.

For a real project you would go one step further and make the package properly installable, so it works from anywhere:

```bash
uv pip install -e .
```

The `-e` flag means "editable", so the package is installed by reference and your edits take effect immediately without reinstalling. This requires a `pyproject.toml` file, which is beyond the scope of this week. Running from the project root is sufficient for everything you will do in this course.

## Where This Leads

Look back at the layout. That structure, consisting of a package of library code, a `tests/` directory, and scripts at the root, is what your Week 4 submission will look like:

```text
assignments_04/
├── weather_model/           <- your model component, importable
│   ├── __init__.py
│   └── classifier.py        <- the WeatherClassifier class
├── tests/
│   └── test_classifier.py   <- pytest tests for predictions and errors
├── models/
│   └── weather_classifier.pkl
└── predict_weather.py       <- a script that uses the component
```

In Week 10, a pipeline imports that package and calls `predict()` on database records. In Week 11, a Prefect flow runs the whole process on a schedule. None of that is possible if the model logic is buried in the middle of a 400-line script, which is why this week comes first.

## Week 1 in One Picture

Every tool from this week has a place in that structure:

| Tool | Where it lives | What it does |
|---|---|---|
| Classes | `weatherkit/` modules | Combine data with the behavior that belongs to it |
| Dataclasses + type hints | Record modules | Declare internal data shapes without boilerplate |
| Docstrings | Everywhere | Explain meaning, units, and intent |
| Pydantic models | The boundary -- wherever outside data enters | Validate and reject bad data at the edge |
| pytest | `tests/` | Prove it works, and keep proving it after you change it |
| Modules and packages | The layout itself | Make all of the above importable and reusable |

Starting next week, you will use these tools on real machine learning code. Week 2 fits regression models. Week 3 adds classification and saves a trained model to disk. Week 4 takes that saved model and turns it into the same kind of package you just built.

## Key Takeaways

A module is a `.py` file, and a package is a directory of modules containing an `__init__.py`. Split code by cohesion, meaning that things which change for the same reason belong in the same file. Library modules should define things and do nothing when imported. Scripts perform work, and the `if __name__ == "__main__"` guard is what prevents a file from accidentally doing both. Keep library code, tests, and entry-point scripts in separate zones, and run pytest from the project root so that your package can be imported.

## Check for Understanding

1. What does `if __name__ == "__main__":` accomplish?

    a. It makes the file run faster
    b. It marks the file as the program's entry point so Python knows which file to execute
    c. It lets the code inside run when the file is executed directly, but not when the file is imported by another module
    d. It is required in every Python file

    <details>
    <summary>Show Answer</summary>
    c -- `__name__` is `"__main__"` only when the file is run directly. Importing the file sets `__name__` to the module's name instead, so the guarded block is skipped. This is what lets one file provide importable functions *and* run as a script.
    </details>

2. Why avoid `from weatherkit.records import *`?

    a. It is slower than importing names individually
    b. It imports every public name into your namespace, so readers cannot tell where a name came from and colliding names silently overwrite each other
    c. It only works inside packages
    d. It causes a circular import

    <details>
    <summary>Show Answer</summary>
    b -- Explicit imports document where each name comes from and prevent one name from silently replacing another. `from weatherkit.records import DailyWeather` tells the reader exactly which name was imported and where it came from.
    </details>

3. You run `pytest` from inside `tests/` and get `ModuleNotFoundError: No module named 'weatherkit'`. Why?

    a. The tests are missing an `__init__.py`
    b. `weatherkit` was never installed from PyPI
    c. Python searches `sys.path`, which includes the directory you ran from -- `weatherkit/` is not inside `tests/`, so running from the project root (or installing the package with `uv pip install -e .`) is what makes it visible
    d. pytest cannot test packages, only single modules

    <details>
    <summary>Show Answer</summary>
    c -- The import works or fails based on where you invoke Python from. Run from the project root, where `weatherkit/` is a visible subdirectory. For a project used from many directories, install it in editable mode instead.
    </details>

4. What is the main reason to put `from weatherkit.records import DailyWeather` inside `weatherkit/__init__.py`?

    a. It is required for the package to be importable
    b. It makes `records.py` load faster
    c. It lets callers write `from weatherkit import DailyWeather`, so your package's public interface stays stable even if you reorganize which file holds what
    d. It prevents circular imports

    <details>
    <summary>Show Answer</summary>
    c -- `__init__.py` defines the package's public entry point. Callers depend on `weatherkit` itself rather than on your internal file layout, so you can move names between modules later without breaking anyone's code.
    </details>
