# Dataclasses, Type Hints, and Docstrings

In the last lesson you wrote `DailyWeather` twice: once with only `__init__`, and once more with a hand-written `__repr__`. The second version was better, but it also required more typing. This lesson shows how to get those benefits without the extra work. It also covers two habits, type hints and docstrings, that make code readable without running it.

## Type Hints

Look at this function signature and try to answer three questions. What is `records`? What is `threshold`? What does the function return?

```
def filter_days(records, threshold):
    ...
```

You cannot answer any of them from the signature alone. `records` might be a list, a DataFrame, or a generator. `threshold` might be a temperature, a probability, or a count. The return value might be a filtered list, a count, or `None` with the filtering done in place. The only way to find out is to read the body, and if the body calls other functions, read those too.

**Type hints** let you say it directly:

```
def filter_days(records: list[DailyWeather], threshold: float) -> list[DailyWeather]:
    ...
```

Now you know. `records` is a list of `DailyWeather` objects, `threshold` is a float, and you get back a list of `DailyWeather`. The syntax is a colon after each parameter name and `->` before the return type.

### The syntax

Here is a runnable tour of the common cases:

```python
def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32


def summarize(label: str, values: list[float]) -> str:
    return f"{label}: {len(values)} values, mean {sum(values) / len(values):.1f}"


def count_good_days(flags: list[bool]) -> int:
    return sum(flags)


print(celsius_to_fahrenheit(24.1))
print(summarize("temps", [24.1, 22.0, 19.5]))
print(count_good_days([True, False, True]))
```

Container types take their contents in square brackets: `list[float]`, `dict[str, float]`, `tuple[float, float]`, `set[str]`. You can nest them: `list[dict[str, float]]` is a list of dictionaries mapping strings to floats -- which is exactly what a batch of database rows looks like.

For a value that might be absent, use `| None`:

```python
def parse_temperature(raw: str) -> float | None:
    """Return the temperature as a float, or None if it cannot be parsed."""
    try:
        return float(raw)
    except ValueError:
        return None


print(parse_temperature("24.1"))
print(parse_temperature("n/a"))
```

`float | None` reads as "a float or `None`" and is how you signal that a function may not have an answer. This shows up constantly in pipeline code, where an API can return a null for a missing measurement.

A function that returns nothing is annotated `-> None`:

```python
def log_record(day: DailyWeather) -> None:
    print(f"[{day.date}] high {day.temp_max}C")
```

> The `list[float]` syntax requires Python 3.9+, and `float | None` requires Python 3.10+. This course uses Python 3.12, so both are fine. You may see older code using `List[float]` and `Optional[float]` imported from the `typing` module -- that is the same thing in pre-3.10 syntax.

### What type hints do *not* do

This is the part that surprises people. Python does not enforce type hints at runtime:

```python
def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32


try:
    print(celsius_to_fahrenheit("this is not a float"))
except TypeError as e:
    print("TypeError:", e)
```

You get `TypeError: unsupported operand type(s) for /: 'str' and 'int'`. Read that carefully, because it is more interesting than it looks.

The annotation was ignored entirely -- Python stored it as metadata and called the function anyway. And then `celsius * 9` *succeeded*: multiplying a string by an integer is legal Python, so it produced the input string repeated nine times. The failure appeared only on the next operation, which was the division. The error message does not mention the annotation and does not mention what `celsius_to_fahrenheit` promised to accept. It points at an operation two steps removed from the actual mistake.

Remember this pattern: a wrong type usually does not cause a failure at the point where it enters your program. It causes a failure later, somewhere else, with a message that describes a symptom rather than a cause.

So why bother? Three reasons, in increasing order of importance:

1. **Your editor uses them.** VS Code reads type hints and will autocomplete `day.temp_max`, flag `day.temp_maximum` as an unknown attribute, and warn you when you pass a `str` where a `float` is expected -- before you run anything.
2. **Type checkers use them.** Tools like `mypy` and `pyright` read your whole codebase and report inconsistencies as errors. This is optional and we will not require it in this course, but it is standard in production Python teams.
3. **People use them.** This is the big one. A type hint is a promise to the next reader about what a function expects, and it never goes stale the way a comment does, because it sits in the signature you are already reading.

Type hints are documentation that your tools can also read. The runtime checking you want at your program's boundaries requires a different tool, which is the subject of the next lesson.

## Dataclasses

Here is `DailyWeather` from the last lesson, with type hints added:

```python
class DailyWeather:
    def __init__(
        self,
        date: str,
        temp_max: float,
        temp_min: float,
        precipitation: float,
        wind_speed: float,
    ):
        self.date = date
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.precipitation = precipitation
        self.wind_speed = wind_speed

    def __repr__(self) -> str:
        return (
            f"DailyWeather(date={self.date!r}, temp_max={self.temp_max}, "
            f"temp_min={self.temp_min}, precipitation={self.precipitation}, "
            f"wind_speed={self.wind_speed})"
        )

    def __eq__(self, other) -> bool:
        return (
            self.date == other.date
            and self.temp_max == other.temp_max
            and self.temp_min == other.temp_min
            and self.precipitation == other.precipitation
            and self.wind_speed == other.wind_speed
        )
```

That version is 30 lines long, repeats every field name four times, and does nothing except hold five values. This is boilerplate, meaning mechanical code you write because the language requires it rather than because it expresses an idea.

The `dataclasses` module in the standard library generates all of it from the field declarations:

```python
from dataclasses import dataclass


@dataclass
class DailyWeather:
    date: str
    temp_max: float
    temp_min: float
    precipitation: float
    wind_speed: float


day = DailyWeather("2023-06-15", 24.1, 14.8, 0.0, 11.2)
print(day)
print(day.temp_max)
```

Five lines of declarations replace thirty lines of boilerplate, and you also gain capabilities the hand-written version did not have:

```python
a = DailyWeather("2023-06-15", 24.1, 14.8, 0.0, 11.2)
b = DailyWeather("2023-06-15", 24.1, 14.8, 0.0, 11.2)
c = DailyWeather("2023-07-20", 30.0, 21.0, 0.0, 8.0)

print(a == b)     # True  -- compares field values, not identity
print(a == c)     # False
print(a)          # readable repr, generated for you
```

`@dataclass` is a **decorator**. The `@` syntax means "pass this class to the `dataclass` function and use whatever that function returns." The decorator inspects the annotated class attributes and writes `__init__`, `__repr__`, and `__eq__` for you.

Note that the type hints are required here. `@dataclass` finds the fields by reading the annotations, so an attribute without an annotation is not treated as a field. This is the one place in Python where a type hint changes how your program behaves.

### Adding methods

A dataclass is a normal class. Everything from the last lesson still works:

```python
from dataclasses import dataclass


@dataclass
class DailyWeather:
    date: str
    temp_max: float
    temp_min: float
    precipitation: float
    wind_speed: float

    def temp_range(self) -> float:
        return self.temp_max - self.temp_min

    def to_dict(self) -> dict[str, float | str]:
        return {
            "date": self.date,
            "temp_max": self.temp_max,
            "temp_min": self.temp_min,
            "precipitation": self.precipitation,
            "wind_speed": self.wind_speed,
        }


day = DailyWeather("2023-06-15", 24.1, 14.8, 0.0, 11.2)
print(day.temp_range())
print(day.to_dict())
```

You write the methods that carry meaning, and the decorator handles the repetitive code.

### Defaults

Fields can have default values, exactly like function parameters:

```python
from dataclasses import dataclass


@dataclass
class RunningConditions:
    min_temp: float = 7.0
    max_temp: float = 26.0
    max_precip: float = 3.0
    max_wind: float = 30.0

    def is_good(self, day: DailyWeather) -> bool:
        """Does this day meet these running conditions?"""
        return (
            self.min_temp <= day.temp_max <= self.max_temp
            and day.temp_min >= 0
            and day.precipitation < self.max_precip
            and day.wind_speed < self.max_wind
        )


print(RunningConditions())
print(RunningConditions(max_temp=32.0))
```

Compare this to the hand-written `RunningConditions` from the previous lesson. The behavior is the same, and the thresholds are now easy to see instead of being hidden inside an `__init__` signature.

As with function parameters, fields with defaults must come after fields without them.

### Mutable defaults and `field`

There is one common mistake to avoid. The following code looks reasonable, but it does not work:

```
@dataclass
class WeatherBatch:
    city: str
    records: list[DailyWeather] = []   # ERROR
```

Python raises `ValueError: mutable default <class 'list'> for field records is not allowed`. A default value is created once when the class is defined, so every instance would share the *same* list. Appending to one batch would append to all of them. Dataclasses detect this problem and refuse to define the class.

The fix is `field(default_factory=...)`, which calls the factory fresh for each instance:

```python
from dataclasses import dataclass, field


@dataclass
class WeatherBatch:
    city: str
    records: list[DailyWeather] = field(default_factory=list)

    def add(self, day: DailyWeather) -> None:
        self.records.append(day)

    def good_day_count(self, conditions: RunningConditions) -> int:
        return sum(conditions.is_good(day) for day in self.records)


batch = WeatherBatch("Charlotte")
batch.add(DailyWeather("2023-06-15", 24.1, 14.8, 0.0, 11.2))
batch.add(DailyWeather("2023-01-10", 2.0, -6.0, 0.0, 22.0))

other = WeatherBatch("Minneapolis")

print(len(batch.records))
print(len(other.records))          # 0 -- separate lists, as it should be
print(batch.good_day_count(RunningConditions()))
```

`default_factory=list` means "call `list()` to make the default." Use `default_factory=dict` for dictionaries and `default_factory=set` for sets.

### Frozen dataclasses

Add `frozen=True` and instances become read-only:

```python
from dataclasses import dataclass, FrozenInstanceError


@dataclass(frozen=True)
class Location:
    name: str
    latitude: float
    longitude: float


charlotte = Location("Charlotte", 35.23, -80.84)
print(charlotte)

try:
    charlotte.latitude = 40.0
except FrozenInstanceError as e:
    print("Cannot modify:", e)
```

Use a frozen dataclass whenever a value should not change after it is created. Coordinates, configuration, and identifiers are all good candidates. A frozen dataclass also becomes hashable, so you can use it as a dictionary key or put it in a set:

```python
locations = {
    Location("Charlotte", 35.23, -80.84),
    Location("Charlotte", 35.23, -80.84),   # same values -- deduplicated
    Location("Minneapolis", 44.98, -93.27),
}
print(len(locations))
```

Two `Location` objects with identical fields are treated as the same key, which is why the set has two entries and not three.

## Docstrings

A docstring is a string literal as the first statement in a module, class, or function. It is not a comment -- Python keeps it, and tools read it.

```python
def classify_days(
    records: list[DailyWeather],
    conditions: RunningConditions,
) -> list[bool]:
    """Label each record as good or bad for running.

    Args:
        records: Daily weather observations to classify.
        conditions: Thresholds defining a good running day.

    Returns:
        A list of booleans, one per input record, in the same order.
    """
    return [conditions.is_good(day) for day in records]


print(classify_days([DailyWeather("2023-06-15", 24.1, 14.8, 0.0, 11.2)],
                    RunningConditions()))
```

Because Python stores it, you can read a docstring at runtime:

```python
print(classify_days.__doc__)
help(classify_days)
```

The output of `help()` in a notebook or REPL, and the hover text in VS Code, both come from this string. So does the documentation for every library you have used. When you call `help(pd.read_csv)`, you are reading a docstring that someone wrote.

### What to write

The style shown above is the Google convention: a one-line summary, followed by `Args:` and `Returns:` sections. It is widely used and easy to read. You will also encounter NumPy style, which uses underlined section headers. Either is acceptable, but stay consistent within a single project.

For something short and obvious, one line is plenty:

```python
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a Celsius temperature to Fahrenheit."""
    return celsius * 9 / 5 + 32
```

A useful guideline is that **the type hints say what a value is, and the docstring says what it means and why it matters.** Do not use the docstring to repeat the signature.

```
# Useless -- the signature already told us this
def temp_range(self) -> float:
    """Returns a float."""
    return self.temp_max - self.temp_min

# Useful -- explains meaning and units
def temp_range(self) -> float:
    """The day's temperature swing in degrees Celsius (high minus low)."""
    return self.temp_max - self.temp_min
```

Docstrings are the right place for units, edge cases, what happens on invalid input, and the reason behind a non-obvious choice. If a docstring is hard to write because the function does five unrelated things, that difficulty is telling you something about the function's design.

## Putting It Together

Here is the full record type as you will carry it forward, with dataclass, hints, and docstrings all in place:

```python
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
        """The day's temperature swing in degrees Celsius (high minus low)."""
        return self.temp_max - self.temp_min

    def to_dict(self) -> dict[str, float | str]:
        """Convert to a plain dict, ready for a database insert."""
        return {
            "date": self.date,
            "temp_max": self.temp_max,
            "temp_min": self.temp_min,
            "precipitation": self.precipitation,
            "wind_speed": self.wind_speed,
        }


day = DailyWeather(
    date="2023-06-15",
    temp_max=24.1,
    temp_min=14.8,
    precipitation=0.0,
    wind_speed=11.2,
)
print(day)
print(day.temp_range())
help(DailyWeather)
```

In about twenty lines, a reader who has never seen your code can learn what a `DailyWeather` holds, in what units, and what it can do.

Note the keyword arguments in the constructor call. With five values in a row, `DailyWeather("2023-06-15", 24.1, 14.8, 0.0, 11.2)` is easy to get wrong and hard to read. Naming each argument costs a few characters and prevents an entire category of mistake.

## One Thing Still Missing

Try this:

```python
nonsense = DailyWeather(
    date="not a date",
    temp_max="hot",
    temp_min=None,
    precipitation=-500.0,
    wind_speed=[1, 2, 3],
)
print(nonsense)
```

It works, and Python does not raise an error. The type hints are only documentation. The dataclass generated an `__init__` that assigns whatever you pass to it, so you now have an object that claims to be a `DailyWeather` and will cause a failure somewhere else in your program.

For data you construct yourself in code, this is usually acceptable, because your editor was warning you as you typed. For data arriving from an API, a CSV, or a user, it is not acceptable. The next lesson addresses that case.

## Key Takeaways

Type hints annotate what a function expects and returns. Python does not enforce them at runtime, but your editor, type checkers, and other humans all read them, which makes them the cheapest documentation available. `@dataclass` generates `__init__`, `__repr__`, and `__eq__` from annotated field declarations -- use `field(default_factory=list)` for mutable defaults and `frozen=True` for values that should not change. Docstrings explain meaning, units, and intent that the signature cannot express, and Python keeps them so `help()` and your editor can show them.

None of these three tools validate anything. They only describe.

## Check for Understanding

1. What happens at runtime if you pass a `str` to a parameter annotated `float`?

    a. Python raises a `TypeError` immediately, at the call
    b. Python converts the string to a float automatically
    c. Nothing -- the annotation is ignored, and the code fails later only if the string is used in a way that requires a number
    d. Python issues a warning but continues

    <details>
    <summary>Show Answer</summary>
    c -- Type hints are not enforced at runtime. Python records the annotation as metadata and runs the function normally. Any error comes from the operation itself (like multiplying a string by a float), not from the hint.
    </details>

2. Why does `@dataclass` require type annotations on its fields?

    a. So Python can validate the values passed in
    b. Because the decorator identifies the fields by reading the class annotations -- an unannotated attribute is not treated as a field
    c. To make the generated `__repr__` shorter
    d. It does not require them; they are optional

    <details>
    <summary>Show Answer</summary>
    b -- `@dataclass` inspects `__annotations__` to find the fields. This is the unusual case where a type hint genuinely changes behavior. It still does not validate the values.
    </details>

3. Why is `records: list[DailyWeather] = []` rejected in a dataclass?

    a. Lists cannot be dataclass fields
    b. The default is created once at class-definition time, so every instance would share the same list -- use `field(default_factory=list)` instead
    c. `list[DailyWeather]` is invalid type-hint syntax
    d. Fields with defaults are not allowed at all

    <details>
    <summary>Show Answer</summary>
    b -- A single mutable default would be shared across all instances, so appending to one object's list would change every other object's list. Dataclasses raise a `ValueError` rather than let you make that mistake. `field(default_factory=list)` calls `list()` fresh for each new instance.
    </details>

4. Which docstring is more useful for `precipitation`?

    a. `"""A float representing precipitation."""`
    b. `"""Total precipitation for the day in millimeters; 0.0 means no measurable rain."""`
    c. `"""precipitation"""`
    d. They are equally useful

    <details>
    <summary>Show Answer</summary>
    b -- The type hint already says the value is a float. The docstring should add what the signature cannot express: the units (millimeters), the time period (the day), and how to interpret an edge case (0.0). Option a only restates the annotation.
    </details>
