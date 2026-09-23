# Testing with pytest

For a helpful overview before diving in: [pytest documentation -- Get Started](https://docs.pytest.org/en/stable/getting-started.html)

You have already been testing your code. Every time you added a `print()` to check a value, ran a cell to see if it worked, or eyeballed a DataFrame after a merge, you were testing -- manually, once, and then throwing the result away.

A **test** is that same check written down as code, so that it runs again every time. That difference is what makes testing valuable. Manual checking confirms the code worked once, on your machine, on the day you wrote it. A test confirms that it still works after you restructure it in Week 4, after a library upgrade, and after a teammate changes something they believed was unrelated.

This matters immediately: the Practicum requires you to write tests for your extract client in Sprint 1, and in Week 4 you will refactor your machine learning model into a component -- which is exactly the operation tests exist to make safe.

Install pytest if you have not already:

```bash
uv pip install pytest
```

## A Note on Running This Lesson

pytest works on `.py` files that it discovers in a directory. That does not fit inside a notebook, so the cells below write real files to a `pytest_demo/` folder and then run pytest on them using `subprocess`.

When you write tests in a real project, you will create these files in your editor and run `pytest` in a terminal. Pay attention to the file contents. The `write_text` calls exist only so that this lesson runs as a notebook.

```python
import subprocess
import sys
from pathlib import Path

DEMO = Path("pytest_demo")
DEMO.mkdir(exist_ok=True)


def run_pytest(*args: str) -> None:
    """Run pytest in the demo directory and print its output."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        cwd=DEMO,
        capture_output=True,
        text=True,
    )
    print(result.stdout[-4000:])


print(f"Working in: {DEMO.resolve()}")
```

## The Code Under Test

Testing requires something to test, so we will start with a small module. It contains the running-conditions logic from earlier this week, with a few improvements:

```python
(DEMO / "weather.py").write_text('''
"""Weather record types and running-condition logic."""

from dataclasses import dataclass


@dataclass
class DailyWeather:
    """One day of observed weather at a single location."""

    date: str
    temp_max: float
    temp_min: float
    precipitation: float
    wind_speed: float

    def temp_range(self) -> float:
        """The day's temperature swing in Celsius (high minus low)."""
        return self.temp_max - self.temp_min


def is_good_for_running(day: DailyWeather) -> bool:
    """Whether conditions are suitable for an outdoor run.

    Args:
        day: The day's observed weather.

    Returns:
        True if the day is mild, dry, and not too windy.
    """
    return (
        7 <= day.temp_max <= 26
        and day.temp_min >= 0
        and day.precipitation < 3.0
        and day.wind_speed < 30
    )


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a Celsius temperature to Fahrenheit."""
    return celsius * 9 / 5 + 32
''')
print("wrote weather.py")
```

## Your First Test

A pytest test is an ordinary function. There is no class to inherit from and no special assertion methods, because you use Python's built-in `assert`.

Three conventions are all pytest needs to find your tests:

- The file is named `test_*.py` (or `*_test.py`)
- The function is named `test_*`
- The function takes no arguments (unless it uses a fixture -- more on that later)

```python
(DEMO / "test_weather.py").write_text('''
from weather import DailyWeather, celsius_to_fahrenheit, is_good_for_running


def test_temp_range():
    day = DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2)
    assert day.temp_range() == 9.4


def test_mild_dry_day_is_good_for_running():
    day = DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2)
    assert is_good_for_running(day) is True


def test_freezing_day_is_not_good_for_running():
    day = DailyWeather("2023-01-10", 2.0, -6.0, 0.0, 22.0)
    assert is_good_for_running(day) is False
''')

run_pytest("-v")
```

Read the output. Each test has its own line marked `PASSED` or `FAILED`, and the summary at the bottom counts them. Look closely, because one of the tests failed.

## Reading a Failure

`test_temp_range` fails, and pytest tells you exactly why:

```text
E       AssertionError: assert 9.400000000000002 == 9.4
E        +  where 9.400000000000002 = temp_range()
E        +    where temp_range = DailyWeather(date='2023-06-15', temp_max=20.1, temp_min=10.7, precipitation=0.0, wind_speed=11.2).temp_range
```

This is one of pytest's most useful features. It rewrites your `assert` statements so that when one fails, it shows the actual values on both sides instead of only reporting "assertion failed." You did not have to write `assertEqual(a, b, "range was wrong")`. You wrote a plain `assert`, and pytest reconstructed the detail for you.

The failure is real rather than a mistake in the code. In binary floating point, `20.1 - 10.7` equals `9.400000000000002` rather than `9.4`. Every language that uses IEEE 754 floating point behaves this way. This is the most common surprise in numeric testing, and the solution is `pytest.approx`:

```python
(DEMO / "test_weather.py").write_text('''
import pytest

from weather import DailyWeather, celsius_to_fahrenheit, is_good_for_running


def test_temp_range():
    day = DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2)
    assert day.temp_range() == pytest.approx(9.4)


def test_mild_dry_day_is_good_for_running():
    day = DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2)
    assert is_good_for_running(day) is True


def test_freezing_day_is_not_good_for_running():
    day = DailyWeather("2023-01-10", 2.0, -6.0, 0.0, 22.0)
    assert is_good_for_running(day) is False
''')

run_pytest("-v")
```

All three tests now pass. **Never compare floats with `==` in a test.** Use `pytest.approx`, which compares values within a small relative tolerance. It also works on collections: `assert results == pytest.approx([1.0, 2.0, 3.0])`.

### Anatomy of a test

Each of those tests has the same three parts, and it is a useful habit to name them:

```
def test_mild_dry_day_is_good_for_running():
    day = DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2)   # Arrange
    result = is_good_for_running(day)                          # Act
    assert result is True                                      # Assert
```

**Arrange** the inputs, **Act** by calling the code you are testing, and then **Assert** something about the result. When a test is difficult to write, the cause is usually a very large Arrange step. That difficulty is a signal about the design of the code rather than about testing.

Note the test *names*. A name like `test_freezing_day_is_not_good_for_running` tells you what broke as soon as the test fails. A name like `test_2` forces you to read the function body. Names are documentation, and in a failure report they are the first thing you see.

## Testing the Failure Path

Every test so far has checked the case where everything works. It is equally important to test that your code fails *when it should*, and that it fails in the way you promised.

Add validation to the module:

```python
(DEMO / "weather.py").write_text('''
"""Weather record types and running-condition logic."""

from dataclasses import dataclass


@dataclass
class DailyWeather:
    """One day of observed weather at a single location."""

    date: str
    temp_max: float
    temp_min: float
    precipitation: float
    wind_speed: float

    def __post_init__(self) -> None:
        """Validate the record after the generated __init__ runs."""
        if self.temp_min > self.temp_max:
            raise ValueError(
                f"temp_min ({self.temp_min}) is above temp_max ({self.temp_max})"
            )
        if self.precipitation < 0:
            raise ValueError(f"precipitation cannot be negative: {self.precipitation}")

    def temp_range(self) -> float:
        """The day's temperature swing in Celsius (high minus low)."""
        return self.temp_max - self.temp_min


def is_good_for_running(day: DailyWeather) -> bool:
    """Whether conditions are suitable for an outdoor run."""
    return (
        7 <= day.temp_max <= 26
        and day.temp_min >= 0
        and day.precipitation < 3.0
        and day.wind_speed < 30
    )


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a Celsius temperature to Fahrenheit."""
    return celsius * 9 / 5 + 32


def mean_temp_max(days: list[DailyWeather]) -> float:
    """Average daily high across a list of records.

    Raises:
        ValueError: If `days` is empty.
    """
    if not days:
        raise ValueError("cannot average an empty list of records")
    return sum(day.temp_max for day in days) / len(days)
''')
print("wrote weather.py with validation")
```

> `__post_init__` is a dataclass hook: it runs immediately after the generated `__init__` finishes. It is the standard place to put validation in a dataclass. This is a lighter-weight alternative to Pydantic for internal records -- fine for a couple of invariants, though Pydantic is what you want at a real boundary.

Now test that the errors happen. `pytest.raises` is a context manager that asserts the block raises what you expect:

```python
(DEMO / "test_errors.py").write_text('''
import pytest

from weather import DailyWeather, mean_temp_max


def test_swapped_temperatures_raise_value_error():
    with pytest.raises(ValueError):
        DailyWeather("2023-06-15", temp_max=10.7, temp_min=20.1,
                     precipitation=0.0, wind_speed=11.2)


def test_negative_precipitation_raises_value_error():
    with pytest.raises(ValueError):
        DailyWeather("2023-06-15", temp_max=20.1, temp_min=10.7,
                     precipitation=-5.0, wind_speed=11.2)


def test_error_message_names_the_problem():
    """The message should be specific enough to debug from."""
    with pytest.raises(ValueError, match="temp_min"):
        DailyWeather("2023-06-15", temp_max=10.7, temp_min=20.1,
                     precipitation=0.0, wind_speed=11.2)


def test_mean_of_empty_list_raises():
    with pytest.raises(ValueError, match="empty"):
        mean_temp_max([])


def test_valid_record_does_not_raise():
    day = DailyWeather("2023-06-15", temp_max=20.1, temp_min=10.7,
                       precipitation=0.0, wind_speed=11.2)
    assert day.temp_max == 20.1
''')

run_pytest("-v", "test_errors.py")
```

The test *passes* when the error is raised. If the code stopped validating, `pytest.raises` would report "DID NOT RAISE", which is exactly the regression you want to detect.

The `match=` argument checks the error message against a regular expression, and you should use it. Without `match`, `pytest.raises(ValueError)` passes if *any* `ValueError` occurs, including one caused by a typo in your test setup. That produces a test that passes for the wrong reason.

Notice `test_valid_record_does_not_raise` at the end. When you add validation, it is easy to make it too strict. A test confirming that valid input still works costs very little and protects against that.

## Running Many Cases: parametrize

The following tests have a problem:

```
def test_cold_day_is_bad():
    assert is_good_for_running(DailyWeather("d", 5.0, 1.0, 0.0, 5.0)) is False

def test_hot_day_is_bad():
    assert is_good_for_running(DailyWeather("d", 35.0, 20.0, 0.0, 5.0)) is False

def test_wet_day_is_bad():
    assert is_good_for_running(DailyWeather("d", 20.0, 12.0, 10.0, 5.0)) is False
```

The same structure appears three times with different numbers. `@pytest.mark.parametrize` combines them into one test that runs several times:

```python
(DEMO / "test_conditions.py").write_text('''
import pytest

from weather import DailyWeather, is_good_for_running


@pytest.mark.parametrize(
    "temp_max, temp_min, precipitation, wind_speed, expected, reason",
    [
        (20.1, 10.7, 0.0, 11.2, True,  "mild and dry"),
        (20.0, 12.0, 2.9, 29.0, True,  "just inside every threshold"),
        (5.0,   1.0, 0.0,  5.0, False, "too cold"),
        (35.0, 20.0, 0.0,  5.0, False, "too hot"),
        (20.0, 12.0, 10.0, 5.0, False, "too wet"),
        (20.0, 12.0, 0.0, 45.0, False, "too windy"),
        (20.0, -2.0, 0.0,  5.0, False, "freezing overnight"),
    ],
)
def test_running_conditions(temp_max, temp_min, precipitation, wind_speed,
                            expected, reason):
    day = DailyWeather("2023-06-15", temp_max, temp_min, precipitation, wind_speed)
    assert is_good_for_running(day) is expected, reason
''')

run_pytest("-v", "test_conditions.py")
```

One function body produces seven separate test cases. Each one gets its own line in the output and its own pass or fail result, so a single broken case does not hide the others.

Two details are worth copying into your own tests. First, the `reason` column becomes the message printed on failure, which the `assert ... , reason` syntax attaches. Second, the case labeled "just inside every threshold" is a **boundary test**, using `precipitation=2.9` against a `< 3.0` rule and `wind_speed=29.0` against a `< 30` rule. Off-by-one errors and incorrect comparison operators appear exactly at these boundaries, so boundaries are where the most valuable test cases are. Testing `precipitation=0.0` proves much less than testing `2.9` and `3.0`.

## Removing Repetition: fixtures

Several of the tests above build the same `DailyWeather` object in their first line. A **fixture** is a reusable piece of setup. You define it once, and any test can request it by naming it as a parameter.

```python
(DEMO / "test_fixtures.py").write_text('''
import pytest

from weather import DailyWeather, is_good_for_running, mean_temp_max


@pytest.fixture
def mild_day() -> DailyWeather:
    """A pleasant June day: mild, dry, light wind."""
    return DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2)


@pytest.fixture
def week_of_weather() -> list[DailyWeather]:
    """Three days spanning good and bad conditions."""
    return [
        DailyWeather("2023-06-15", 20.1, 10.7, 0.0, 11.2),
        DailyWeather("2023-06-16", 27.3, 16.2, 2.4, 18.7),
        DailyWeather("2023-06-17", 30.0, 21.0, 0.0, 8.0),
    ]


def test_mild_day_is_good(mild_day):
    assert is_good_for_running(mild_day) is True


def test_mild_day_range(mild_day):
    assert mild_day.temp_range() == pytest.approx(9.4)


def test_mean_across_week(week_of_weather):
    assert mean_temp_max(week_of_weather) == pytest.approx(25.8)


def test_only_first_day_is_good(week_of_weather):
    good = [d for d in week_of_weather if is_good_for_running(d)]
    assert len(good) == 1
    assert good[0].date == "2023-06-15"
''')

run_pytest("-v", "test_fixtures.py")
```

`test_mild_day_is_good(mild_day)` does not receive a global variable. pytest reads the parameter name, finds the fixture with that name, calls it, and passes the result to the test. Importantly, pytest calls the fixture **again for every test**, so one test modifying the object cannot affect another. That isolation is the reason to use a fixture instead of a module-level constant.

Fixtures shared across several test files go in a file named `conftest.py`, which pytest loads automatically -- no import needed.

## Running the Whole Suite

With no arguments, pytest discovers and runs everything:

```python
run_pytest("-v")
```

The output ends with a summary line: how many passed, how many failed, and how long it took. In a real project this is what runs on every commit.

A few flags worth knowing:

```python
run_pytest("-q")                          # quiet: one character per test
run_pytest("-x")                          # stop at the first failure
run_pytest("-k", "running")               # only tests whose name matches "running"
run_pytest("test_errors.py::test_mean_of_empty_list_raises")   # one specific test
```

You will use `-x` most often while fixing a specific problem. Use `-k` when a test suite becomes large enough to be slow.

## Seeing a Real Failure

Tests that always pass will not teach you how to read pytest output. We will break something on purpose:

```python
(DEMO / "test_broken.py").write_text('''
from weather import DailyWeather, celsius_to_fahrenheit, is_good_for_running


def test_fahrenheit_conversion_is_wrong_on_purpose():
    assert celsius_to_fahrenheit(100.0) == 100.0


def test_hot_day_wrongly_expected_good():
    day = DailyWeather("2023-07-20", 35.0, 24.0, 0.0, 8.0)
    assert is_good_for_running(day) is True
''')

run_pytest("test_broken.py")
```

Read the failure report from top to bottom. For each failure, pytest shows the test name, the source line that failed, the actual values (`212.0` where you asserted `100.0`), and a one-line summary at the bottom. You rarely need a debugger to understand a pytest failure, because the report already contains the values.

Now clean up the deliberate breakage:

```python
(DEMO / "test_broken.py").unlink()
run_pytest("-q")
```

## What Is Worth Testing

You will not test everything, and you should not try. Focus on the following:

- **The core logic**, meaning the function that makes a decision, transforms data, or computes a result. `is_good_for_running` is worth testing, and a one-line attribute getter is not.
- **The boundaries**, meaning values right at a threshold, empty lists, zero, negative numbers, and the first and last element.
- **The error paths.** Every `raise` in your code should have a test proving that it happens when it should.
- **Every bug you fix.** Write a test that fails first, and *then* fix the bug. After that, the bug cannot return without a test reporting it. These are the most valuable tests you will write.

Do not test the standard library, and do not test that Python's `+` operator works. Test the decisions your own code makes.

One warning: a test that can never fail is worse than no test at all, because it creates false confidence. After writing a test, break the code deliberately and confirm that the test fails. If it still passes, the test is not checking what you believe it is checking.

## Why This Matters in Week 4

Next month you will take a working machine learning workflow and restructure it into a class with a `predict()` method. That is a **refactor**: the behavior should stay identical while the structure changes completely.

Without tests, the only way to check a restructuring is to run the script and read the output carefully. That approach catches obvious breakage and misses subtle breakage, such as predictions that are still plausible numbers but were computed from features in the wrong order.

With tests, you run `pytest` before the change, confirm everything passes, restructure the code, and run `pytest` again. You then know whether the behavior changed. That is the value tests provide, and it is why this lesson comes before Week 4 rather than after it.

## Key Takeaways

A pytest test is a function named `test_*` in a file named `test_*.py` that uses a plain `assert`. pytest rewrites those assert statements to show the actual values on failure, so you rarely need a debugger. Always use `pytest.approx` when comparing floats. Use `pytest.raises(SomeError, match="...")` to prove your error paths fire, with `match` so the test cannot pass for the wrong reason. Use `@pytest.mark.parametrize` for the same test across many inputs, and fixtures for setup shared across tests. Aim tests at core logic, boundary values, and error paths, and write a test for every bug you fix.

## Check for Understanding

1. Why does `assert day.temp_range() == 9.4` fail when the values are 20.1 and 10.7?

    a. `temp_range()` has a bug
    b. Binary floating point cannot represent 20.1 and 10.7 exactly, so the subtraction gives 9.400000000000002 -- use `pytest.approx`
    c. pytest requires `assertEqual` rather than `assert`
    d. The dataclass stored the values as strings

    <details>
    <summary>Show Answer</summary>
    b -- This is standard IEEE 754 floating-point behavior, not an oddity of pytest or a bug in the code. Any float comparison in a test should use `pytest.approx`, which compares values within a relative tolerance.
    </details>

2. What does `pytest.raises(ValueError)` assert?

    a. That the code inside the block does not raise an error
    b. That the code inside the block raises a `ValueError` -- the test fails with "DID NOT RAISE" if no error occurs
    c. That a `ValueError` is caught and logged
    d. That the test should be skipped

    <details>
    <summary>Show Answer</summary>
    b -- It asserts that the error occurs. Testing failure paths matters as much as testing success paths, because it proves your validation actually runs.
    </details>

3. Why add `match="temp_min"` to `pytest.raises(ValueError, ...)`?

    a. It makes the test run faster
    b. It is required syntax
    c. Without it, the test passes on *any* `ValueError` -- including one accidentally raised by broken test setup -- so `match` confirms the error is the one you meant
    d. It converts the error into a warning

    <details>
    <summary>Show Answer</summary>
    c -- `match` checks the message against a regular expression. It prevents the test from passing for the wrong reason, which is a common way for a test suite to create false confidence.
    </details>

4. In the parametrize table, why is the case `(20.0, 12.0, 2.9, 29.0, True, "just inside every threshold")` more valuable than a case with `precipitation=0.0` and `wind_speed=5.0`?

    a. It uses more decimal places
    b. It sits right at the boundaries of the `< 3.0` and `< 30` rules, which is where off-by-one and wrong-operator bugs actually live
    c. It runs faster
    d. It is not more valuable; both are equivalent

    <details>
    <summary>Show Answer</summary>
    b -- A case comfortably inside the range passes under almost any implementation, including an incorrect one. A boundary case distinguishes `<` from `<=` and catches thresholds that were typed with the wrong digit. Boundaries are where most of these bugs occur.
    </details>

5. What is wrong with a test that has never failed?

    a. Nothing -- passing tests are the goal
    b. It may not actually be exercising the code you think, giving false confidence; break the code deliberately and confirm the test goes red
    c. It runs too fast to be meaningful
    d. pytest will eventually skip it automatically

    <details>
    <summary>Show Answer</summary>
    b -- A test that cannot fail is worse than no test, because it appears to provide coverage while providing none. Confirming that a test fails when the code is broken is a quick and worthwhile habit.
    </details>
