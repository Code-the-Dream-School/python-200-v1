# Classes and Objects

For a helpful overview before diving in: [Object-Oriented Programming in Python (YouTube)](https://www.youtube.com/watch?v=Ej_02ICOIgs)

Everything you have written in Python so far has used objects. A string is an object, and `"hello".upper()` calls a method on it. A DataFrame is an object, and `df.head()` calls a method on it. This lesson is about writing your own.

We will approach this by starting with dictionaries, using them until their limitations become clear, and then fixing the specific problems they cause.

## Starting with a Dictionary

Suppose you are working with daily weather observations. Each day has a date, a high and low temperature, precipitation, and wind speed. The obvious first move is a dictionary:

```python
day = {
    "date": "2023-06-15",
    "temp_max": 24.1,
    "temp_min": 14.8,
    "precipitation": 0.0,
    "wind_speed": 11.2,
}

print(day["temp_max"])
```

This works. For a quick script this is the right choice, and there is nothing wrong with using it.

Now we will add some behavior. You want to know the temperature range for a day, and whether the day looked good for a run:

```python
def temp_range(day):
    return day["temp_max"] - day["temp_min"]

def is_good_for_running(day):
    return (
        7 <= day["temp_max"] <= 26
        and day["temp_min"] >= 0
        and day["precipitation"] < 3.0
        and day["wind_speed"] < 30
    )

print(temp_range(day))
print(is_good_for_running(day))
```

This also works. Notice what has happened, though: the data lives in one place and the operations on it live somewhere else. The only thing connecting them is the convention that you pass the right kind of dictionary. Nothing enforces that connection. Watch three ways this goes wrong.

**Problem 1: typos do not raise errors.**

```python
day["temp_maximum"] = 30.0   # typo -- Python is perfectly happy
print(day.keys())
```

You added a new key instead of updating an existing one, and Python did not raise an error. The bug appears later, somewhere else, as a wrong number.

**Problem 2: nothing guarantees the shape.**

```python
partial_day = {"date": "2023-06-16", "temp_max": 22.0}
# temp_range(partial_day)  # KeyError: 'temp_min'
```

The function has no way to state its requirements. It fails when it reaches the missing key, possibly deep inside a loop over 365 records.

**Problem 3: the functions are not connected to the data.**

`temp_range` and `is_good_for_running` only make sense for weather dictionaries, but nothing in your program states that. In a large file, or across several files, nothing connects them to the data they describe. Six months from now, someone will ask what `temp_range` accepts as an argument, and the only way to answer is to read the function body.

## The Fix: Bundling Data with Behavior

A **class** is a template for building objects that carry data *and* the operations that belong to that data. An **object** (or *instance*) is one thing built from that template.

Here is the same weather record as a class:

```python
class DailyWeather:
    def __init__(self, date, temp_max, temp_min, precipitation, wind_speed):
        self.date = date
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.precipitation = precipitation
        self.wind_speed = wind_speed

    def temp_range(self):
        return self.temp_max - self.temp_min

    def is_good_for_running(self):
        return (
            7 <= self.temp_max <= 26
            and self.temp_min >= 0
            and self.precipitation < 3.0
            and self.wind_speed < 30
        )
```

And here is how you use it:

```python
day = DailyWeather("2023-06-15", 24.1, 14.8, 0.0, 11.2)

print(day.date)
print(day.temp_range())
print(day.is_good_for_running())
```

Compare this to the dictionary version. The data and the two operations now arrive together as a single object. `day.temp_range()` reads better than `temp_range(day)`. More importantly, you can discover it: type `day.` in your editor and it will list everything a `DailyWeather` can do.

We will now examine the class one piece at a time.

### `class` and instantiation

```
class DailyWeather:
```

This defines a new type. By convention, class names use `CapWords` (also called PascalCase), which is how you can usually tell a class from a function at a glance.

`DailyWeather` by itself is the template. To make an actual record you *instantiate* it by calling the class like a function:

```python
day = DailyWeather("2023-06-15", 24.1, 14.8, 0.0, 11.2)
print(type(day))
```

`day` is an *instance* of `DailyWeather`. You can make as many as you like, and each one holds its own data:

```python
hot_day  = DailyWeather("2023-07-20", 35.0, 24.0, 0.0, 8.0)
cold_day = DailyWeather("2023-01-10", 2.0, -6.0, 0.0, 22.0)

print(hot_day.temp_max, cold_day.temp_max)
```

### `__init__` and `self`

```
    def __init__(self, date, temp_max, temp_min, precipitation, wind_speed):
```

`__init__` is a special method Python calls automatically when you instantiate the class. Its job is to set up the new object -- the name is short for "initialize." The double underscores on both sides mark it as one of Python's special methods (people usually say "dunder init"). You never call `__init__` yourself; calling `DailyWeather(...)` does it for you.

`self` is the object being created or operated on. It is the first parameter of every method, and Python passes it automatically. When you write `day.temp_range()`, Python internally calls `DailyWeather.temp_range(day)`, so `day` becomes `self`. That is all there is to it. The mechanism is surprising the first time you see it, and after that it is simply a rule you know.

> `self` is a naming convention, not a keyword -- you *could* name it something else and the code would run. Do not. Every Python programmer expects `self`, and using anything else makes your code harder for others to read.

### Attributes

```
        self.date = date
```

Attributes are the data attached to an object. Assigning to `self.date` inside `__init__` creates an attribute on this specific instance, and you read it back with dot notation:

```python
print(day.date)
day.temp_max = 25.0     # attributes can be reassigned
print(day.temp_max)
```

Notice we did not have to declare the attributes ahead of time. Python creates them on assignment. This flexibility is also the source of the typo problem described earlier: `day.temp_maximum = 30.0` would create a new attribute instead of raising an error. We will address that problem in the next two lessons.

### Methods

```
    def temp_range(self):
        return self.temp_max - self.temp_min
```

A method is a function defined inside a class. The only structural difference from a regular function is that first `self` parameter, which gives it access to the object's data. Methods can take other parameters too:

```python
class DailyWeather:
    def __init__(self, date, temp_max, temp_min, precipitation, wind_speed):
        self.date = date
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.precipitation = precipitation
        self.wind_speed = wind_speed

    def temp_range(self):
        return self.temp_max - self.temp_min

    def is_good_for_running(self):
        return (
            7 <= self.temp_max <= 26
            and self.temp_min >= 0
            and self.precipitation < 3.0
            and self.wind_speed < 30
        )

    def warmer_than(self, other):
        """Is this day's high warmer than another day's high?"""
        return self.temp_max > other.temp_max

    def to_dict(self):
        """Convert back to a plain dictionary -- useful when writing to a database."""
        return {
            "date": self.date,
            "temp_max": self.temp_max,
            "temp_min": self.temp_min,
            "precipitation": self.precipitation,
            "wind_speed": self.wind_speed,
        }


hot_day  = DailyWeather("2023-07-20", 35.0, 24.0, 0.0, 8.0)
cold_day = DailyWeather("2023-01-10", 2.0, -6.0, 0.0, 22.0)

print(hot_day.warmer_than(cold_day))
print(cold_day.to_dict())
```

`warmer_than` takes a second `DailyWeather` object and compares it to this one. `to_dict` takes no extra arguments and converts the object back to a dictionary. You will need that method in Week 9, when these records are written to a cloud database that expects plain dictionaries.

## Making Objects Print Nicely

Try printing a `DailyWeather` directly:

```python
print(hot_day)
```

You get something like `<__main__.DailyWeather object at 0x104f3a2d0>`. That output is technically correct, but it tells you nothing useful. Python shows the type and the memory address because you have not given it anything better to show.

The `__repr__` method fixes this. It returns the string Python shows when it displays your object:

```python
class DailyWeather:
    def __init__(self, date, temp_max, temp_min, precipitation, wind_speed):
        self.date = date
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.precipitation = precipitation
        self.wind_speed = wind_speed

    def __repr__(self):
        return (
            f"DailyWeather(date={self.date!r}, temp_max={self.temp_max}, "
            f"temp_min={self.temp_min}, precipitation={self.precipitation}, "
            f"wind_speed={self.wind_speed})"
        )

    def temp_range(self):
        return self.temp_max - self.temp_min


day = DailyWeather("2023-06-15", 24.1, 14.8, 0.0, 11.2)
print(day)
print([day, day])
```

The convention for `__repr__` is to return something that looks like the code you would type to recreate the object. This makes debugging much easier. When you print a list of 20 records, or when a record appears in a stack trace, you see the actual values instead of memory addresses.

> The `!r` in the f-string calls `repr()` on the value, which is why the date comes out with quotes around it. That is what makes the output look like real Python source.

Writing `__repr__` by hand is tedious, and in the next lesson you will stop doing it, because `dataclasses` writes it for you. It is worth seeing once so that you know what is being generated on your behalf.

## A Class That Is Mostly Behavior

Not every class is a data record. Some classes exist to hold a *configuration* and apply it repeatedly. This pattern is important in Week 4.

Consider the running thresholds. Writing `7 <= temp_max <= 26` directly inside `DailyWeather` assumes that everyone agrees on what a good running day is. A runner in Phoenix and a runner in Minneapolis would disagree. We can move the thresholds into their own class:

```python
class RunningConditions:
    def __init__(self, min_temp=7.0, max_temp=26.0, max_precip=3.0, max_wind=30.0):
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.max_precip = max_precip
        self.max_wind = max_wind

    def is_good(self, day):
        """Does this DailyWeather meet these running conditions?"""
        return (
            self.min_temp <= day.temp_max <= self.max_temp
            and day.temp_min >= 0
            and day.precipitation < self.max_precip
            and day.wind_speed < self.max_wind
        )

    def label_all(self, days):
        """Label a list of DailyWeather records. Returns a list of booleans."""
        return [self.is_good(day) for day in days]
```

The thresholds are now data that you can change, and the logic that uses them is written in one place:

```python
days = [
    DailyWeather("2023-06-15", 24.1, 14.8, 0.0, 11.2),   # mild
    DailyWeather("2023-07-20", 30.0, 21.0, 0.0, 8.0),    # warm
    DailyWeather("2023-01-10", 2.0, -6.0, 0.0, 22.0),    # freezing
]

default = RunningConditions()
heat_tolerant = RunningConditions(max_temp=32.0)

print("default:      ", default.label_all(days))
print("heat tolerant:", heat_tolerant.label_all(days))
```

The warm day changes from `False` to `True` when the upper limit moves from 26 to 32 degrees. These are the same three days evaluated against two different sets of criteria, and the logic is written only once. Notice the default arguments in `__init__`. Calling `RunningConditions()` with no arguments gives you reasonable defaults, and you override only the values you care about.

Most useful classes have this shape: something is configured once, then applied many times. In Week 4 you will write a `WeatherClassifier` class that loads a trained machine learning model once in `__init__` and then provides a `predict()` method you can call on as many records as you like. Structurally, this is the same idea as `RunningConditions`.

## When to Use a Class, and When Not To

Use a class when any of the following is true:

- You have data and behavior that clearly belong together
- You will create many instances of the same kind of thing
- Something needs to be set up once and reused (a loaded model, an API client, a database connection)
- You want the thing to be discoverable and self-documenting

Do not use a class when a plain function is enough. A class with one method and no stored data is a function with unnecessary structure around it:

```python
# Don't do this
class TemperatureConverter:
    def celsius_to_fahrenheit(self, c):
        return c * 9 / 5 + 32

# Do this
def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32
```

Unlike some other languages, Python does not require you to put every function inside a class. Standalone functions are completely normal, and a module of well-named functions is often a better design than a class hierarchy.

## Key Takeaways

A class combines data (attributes) with the operations that belong to that data (methods). `__init__` runs when you instantiate the class and sets up the new object's attributes. `self` refers to the instance a method is operating on, and Python passes it automatically when you call `obj.method()`. `__repr__` controls how your object prints, which saves time the first time you have to debug a list of objects.

We care about this because a `DailyWeather` object states what it contains and what it can do, and a dictionary does not. That difference grows more important as a codebase grows, and the codebase you are building in this course will keep growing for ten more weeks.

## Check for Understanding

1. What does `self` refer to inside a method?

    a. The class itself
    b. The specific object the method was called on
    c. The `__init__` method
    d. A reserved Python keyword that cannot be renamed

    <details>
    <summary>Show Answer</summary>
    b -- `self` is the instance. When you write `day.temp_range()`, Python passes `day` as the first argument, and inside the method that argument is named `self`. (Note that `self` is a strong convention, not a keyword -- but renaming it would be a bad idea.)
    </details>

2. When is `__init__` called?

    a. Every time you access an attribute
    b. Only when you explicitly call `obj.__init__()`
    c. Automatically, when you instantiate the class by calling `DailyWeather(...)`
    d. When the object is printed

    <details>
    <summary>Show Answer</summary>
    c -- Calling the class runs `__init__` on the newly created object. You do not call it yourself.
    </details>

3. You run `print(my_object)` and get `<__main__.DailyWeather object at 0x104f3a2d0>`. What should you add to the class?

    a. A `__init__` method
    b. A `__repr__` method that returns a useful string
    c. A `to_dict` method
    d. Nothing -- that is the only output Python can produce for a custom class

    <details>
    <summary>Show Answer</summary>
    b -- Without `__repr__`, Python falls back to showing the type and memory address. Defining `__repr__` lets you control the display, and the convention is to return something resembling the code that would recreate the object.
    </details>

4. Why is `RunningConditions` written as a class rather than a function with four extra parameters?

    a. Because functions cannot take default arguments
    b. Because the thresholds are configured once and then applied to many records, so bundling them into an object avoids passing four values through every call
    c. Because classes run faster than functions
    d. Because `is_good` needs access to `self`

    <details>
    <summary>Show Answer</summary>
    b -- The thresholds are set up once and reused. A function would require threading all four values through every call site. This "configure once, apply many times" pattern is exactly what a class is good at, and it is the shape of the model component you will build in Week 4.
    </details>
