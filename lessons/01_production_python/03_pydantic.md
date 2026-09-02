# Validating Data at the Boundary

The last lesson ended with this:

```
nonsense = DailyWeather(
    date="not a date",
    temp_max="hot",
    temp_min=None,
    precipitation=-500.0,
    wind_speed=[1, 2, 3],
)
```

Python does not raise an error. A dataclass assigns whatever you give it. When you wrote the values yourself, this is tolerable, because your editor was marking the mistake as you typed. Most data does not come from you, however. It comes from an API, a CSV, a database, a form, or another team's service, and none of those sources read your type hints.

This lesson is about [Pydantic](https://docs.pydantic.dev/latest/), a library that turns a schema into an actual validator, so bad data fails at the edge of your program instead of five steps into it.

Install it if you have not already:

```bash
uv pip install pydantic
```

## The Boundary

It helps to think of your program as having an inside and an outside.

**Inside**, you control everything. You wrote the functions, you know the types, and a dataclass with type hints is a perfectly good record. Nothing needs checking because nothing unexpected can get in.

**Outside** is everything else -- HTTP responses, files, environment variables, user input, message queues. Data crossing in from there is *untrusted*: not necessarily malicious, just unverified. The API's documentation says `temperature_2m_max` is a number, but on one day out of 365 it is `null` because the sensor was down, and nobody told you.

The **boundary** is where outside data becomes inside data. The discipline is simple: validate at the boundary, once, and everything downstream can assume the data is well-formed.

The alternative is to check defensively at every step. Code written that way looks like this:

```
if row.get("temperature_2m_max") is not None:
    if isinstance(row["temperature_2m_max"], (int, float)):
        if -90 <= row["temperature_2m_max"] <= 60:
            ...
```

That is three lines of checking around one line of actual work, repeated in every function that touches the data, and it will still miss some cases.

## Your First Model

A Pydantic model looks almost exactly like a dataclass:

```python
from pydantic import BaseModel


class DailyWeather(BaseModel):
    date: str
    temp_max: float
    temp_min: float
    precipitation: float
    wind_speed: float


day = DailyWeather(
    date="2023-06-15",
    temp_max=24.1,
    temp_min=14.8,
    precipitation=0.0,
    wind_speed=11.2,
)
print(day)
print(day.temp_max)
```

The field declarations, attribute access, and readable repr are all the same. You inherit from `BaseModel` instead of applying `@dataclass`, and that is the only visible difference.

The invisible difference is that the type hints are now enforced:

```python
from pydantic import ValidationError

try:
    DailyWeather(
        date="2023-06-15",
        temp_max="hot",
        temp_min=14.8,
        precipitation=0.0,
        wind_speed=11.2,
    )
except ValidationError as e:
    print(e)
```

You get a `ValidationError` that names the field, states what was expected, and shows what it received. Compare that to the dataclass version, which accepted `"hot"` silently and failed hundreds of lines later with a message about unsupported operand types.

### Errors report everything at once

Pydantic does not stop at the first problem:

```python
try:
    DailyWeather(
        date="2023-06-15",
        temp_max="hot",
        temp_min=None,
        wind_speed=[1, 2, 3],
    )
except ValidationError as e:
    print(f"{e.error_count()} problems found\n")
    for err in e.errors():
        print(f"  field={err['loc']}  type={err['type']}  msg={err['msg']}")
```

Four problems appear in one report: two values of the wrong type, one missing required field (`precipitation`), and one more value of the wrong type. When you are debugging a malformed API payload under time pressure, receiving the whole list at once instead of fixing the problems one at a time saves a great deal of effort.

Notice that `precipitation` was reported as missing. In Pydantic, a field with no default is **required** -- the omission is an error, not a silent `None`.

### Sensible coercion

Pydantic converts when the conversion is unambiguous and safe:

```python
day = DailyWeather(
    date="2023-06-15",
    temp_max=24,          # int -> float
    temp_min="14.8",      # numeric string -> float
    precipitation=0,
    wind_speed=11.2,
)
print(day)
print(type(day.temp_max), type(day.temp_min))
```

Both became floats. This behavior is deliberate and useful. JSON does not distinguish floats from integers, CSV values are all strings, and query parameters are always text. Pydantic handles those conversions so that you do not have to write `float(row["temp_max"])` throughout your code.

Pydantic refuses to convert when doing so would require guessing:

```python
for bad in ["hot", "", None, [24.1]]:
    try:
        DailyWeather(date="2023-06-15", temp_max=bad, temp_min=14.8,
                     precipitation=0.0, wind_speed=11.2)
        print(f"{bad!r} -> accepted")
    except ValidationError:
        print(f"{bad!r} -> rejected")
```

The string `"14.8"` is a number written as text, while `"hot"` is not a number at all. Pydantic converts a value when there is exactly one reasonable interpretation of it.

## Constraints

A value can have the correct type and still be invalid. A precipitation of `-500.0` is a valid float, but it is a physically impossible measurement. `Field` lets you attach constraints:

```python
from pydantic import BaseModel, Field, ValidationError


class DailyWeather(BaseModel):
    date: str
    temp_max: float = Field(ge=-90, le=60, description="Daily high in Celsius")
    temp_min: float = Field(ge=-90, le=60, description="Daily low in Celsius")
    precipitation: float = Field(ge=0, description="Total precipitation in mm")
    wind_speed: float = Field(ge=0, le=500, description="Max wind speed in km/h")


print(DailyWeather(date="2023-06-15", temp_max=24.1, temp_min=14.8,
                   precipitation=0.0, wind_speed=11.2))

try:
    DailyWeather(date="2023-06-15", temp_max=24.1, temp_min=14.8,
                 precipitation=-500.0, wind_speed=11.2)
except ValidationError as e:
    print("\n", e)
```

The common numeric constraints are `ge` (greater than or equal), `gt`, `le`, `lt`. For strings there are `min_length`, `max_length`, and `pattern` (a regular expression). The `description` is documentation that travels with the schema.

The bounds above are chosen to catch *impossible* values rather than unusual ones. The lowest temperature ever recorded on Earth is about -89 C, so `ge=-90` rejects invalid sensor output without rejecting real readings from Antarctica. Avoid tightening constraints to match only the values you expect. A validator that rejects real data is worse than no validator, because it will fail on the one day that matters most.

## Custom Validation

Some rules cannot be expressed with `Field`. For those, Pydantic provides validator decorators.

A `field_validator` checks one field:

```python
from datetime import date as date_type
from pydantic import BaseModel, Field, field_validator, ValidationError


class DailyWeather(BaseModel):
    date: str
    temp_max: float = Field(ge=-90, le=60)
    temp_min: float = Field(ge=-90, le=60)
    precipitation: float = Field(ge=0)
    wind_speed: float = Field(ge=0, le=500)

    @field_validator("date")
    @classmethod
    def date_must_be_iso(cls, v: str) -> str:
        """Require YYYY-MM-DD, and require it to be a real calendar date."""
        try:
            date_type.fromisoformat(v)
        except ValueError:
            raise ValueError(f"expected an ISO date like 2023-06-15, got {v!r}")
        return v


print(DailyWeather(date="2023-06-15", temp_max=24.1, temp_min=14.8,
                   precipitation=0.0, wind_speed=11.2).date)

for bad_date in ["06/15/2023", "2023-02-30", "not a date"]:
    try:
        DailyWeather(date=bad_date, temp_max=24.1, temp_min=14.8,
                     precipitation=0.0, wind_speed=11.2)
    except ValidationError as e:
        print(f"{bad_date!r} rejected: {e.errors()[0]['msg']}")
```

Note that `2023-02-30` is rejected. It has the correct shape but is not a real calendar day, which is the kind of value a regular expression would accept without checking.

The mechanics work as follows. The decorator names the field it guards, the method receives that field's value, and the method must **return** the value (possibly changed) or raise a `ValueError`. Pydantic catches that `ValueError` and includes it in the `ValidationError` report along with every other problem. The `@classmethod` line below `@field_validator` is required.

A `model_validator` runs after all fields are populated, so it can compare them:

```python
from pydantic import BaseModel, Field, model_validator, ValidationError


class DailyWeather(BaseModel):
    date: str
    temp_max: float = Field(ge=-90, le=60)
    temp_min: float = Field(ge=-90, le=60)
    precipitation: float = Field(ge=0)
    wind_speed: float = Field(ge=0, le=500)

    @model_validator(mode="after")
    def check_temp_order(self):
        """The daily high cannot be below the daily low."""
        if self.temp_min > self.temp_max:
            raise ValueError(
                f"temp_min ({self.temp_min}) is above temp_max ({self.temp_max})"
            )
        return self


try:
    DailyWeather(date="2023-06-15", temp_max=14.8, temp_min=24.1,
                 precipitation=0.0, wind_speed=11.2)
except ValidationError as e:
    print(e)
```

Neither temperature is suspicious on its own, since 14.8 and 24.1 are both ordinary values. The problem is their *relationship*. A bug in an upstream system that swaps two columns produces exactly this result, and no per-field check would detect it.

## Nested Models: A Real API Response

We can now handle the case that nested models are designed for. Below is what the Open-Meteo historical weather API actually returns. This is the API you will call in Weeks 3, 9, and 11:

```python
api_response = {
    "latitude": 35.23,
    "longitude": -80.84,
    "timezone": "America/New_York",
    "daily_units": {
        "time": "iso8601",
        "temperature_2m_max": "°C",
        "temperature_2m_min": "°C",
        "precipitation_sum": "mm",
        "wind_speed_10m_max": "km/h",
    },
    "daily": {
        "time": ["2023-06-15", "2023-06-16", "2023-06-17"],
        "temperature_2m_max": [24.1, 27.3, 30.0],
        "temperature_2m_min": [14.8, 16.2, 21.0],
        "precipitation_sum": [0.0, 2.4, 0.0],
        "wind_speed_10m_max": [11.2, 18.7, 8.0],
    },
}
```

Notice two things about this structure before writing any code.

First, it is **columnar**. There is no list of day objects; there are five parallel lists, and day *i* is assembled by taking index *i* from each. This format is efficient to transmit but awkward to work with, so converting it into rows is one of the first steps in any pipeline.

Second, it is **nested**. `daily` is a dictionary inside the response, so the schema has to describe structure, not just fields.

Pydantic models nest by using one model as another's field type:

```python
from pydantic import BaseModel, Field


class DailyBlock(BaseModel):
    """The columnar arrays returned under the `daily` key."""

    time: list[str]
    temperature_2m_max: list[float]
    temperature_2m_min: list[float]
    precipitation_sum: list[float]
    wind_speed_10m_max: list[float]


class OpenMeteoResponse(BaseModel):
    """A daily historical weather response from the Open-Meteo archive API."""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str
    daily: DailyBlock


parsed = OpenMeteoResponse.model_validate(api_response)
print(parsed.latitude, parsed.timezone)
print(parsed.daily.temperature_2m_max)
```

`model_validate` is how you validate an existing dictionary, as opposed to passing keyword arguments. It is what you will call on `response.json()`.

Three useful things happened automatically. First, the nested `daily` dictionary was validated against `DailyBlock` and converted into an object, so `parsed.daily.temperature_2m_max` autocompletes in your editor. Second, the `daily_units` key was ignored, because Pydantic ignores unknown fields by default, which means the API can add fields without breaking your code. Third, every element of every list was checked to confirm it is a float.

The third point is the most important. Consider a failure that happens regularly in practice:

```python
from pydantic import ValidationError

broken = {
    "latitude": 35.23,
    "longitude": -80.84,
    "timezone": "America/New_York",
    "daily": {
        "time": ["2023-06-15", "2023-06-16", "2023-06-17"],
        "temperature_2m_max": [24.1, None, 30.0],     # sensor outage
        "temperature_2m_min": [14.8, 16.2, 21.0],
        "precipitation_sum": [0.0, 2.4, 0.0],
        "wind_speed_10m_max": [11.2, 18.7, 8.0],
    },
}

try:
    OpenMeteoResponse.model_validate(broken)
except ValidationError as e:
    err = e.errors()[0]
    print("location:", err["loc"])
    print("message: ", err["msg"])
```

There is a `null` in the middle of one array. The error reports the exact path to it, naming `daily`, then `temperature_2m_max`, then index 1, so you know precisely which measurement on which day is missing.

Without validation, that `None` becomes a `NaN` in a DataFrame. It is then passed to a model, which raises an unclear error stating that the input contains NaN, and you spend twenty minutes working backwards to find the one bad reading. This is the main argument for validating at the boundary.

If you would rather *tolerate* missing readings than reject the batch, say so in the schema by widening the type:

```python
class TolerantDailyBlock(BaseModel):
    time: list[str]
    temperature_2m_max: list[float | None]
    temperature_2m_min: list[float]
    precipitation_sum: list[float]
    wind_speed_10m_max: list[float]


class TolerantResponse(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    daily: TolerantDailyBlock


tolerant = TolerantResponse.model_validate(broken)
print(tolerant.daily.temperature_2m_max)
```

Either choice is reasonable. What matters is that the choice is now recorded in the schema, where the next reader can see it, rather than happening by accident.

## Columnar to Rows

Once the response is validated, converting it into row records is straightforward. It is also safe, because you already know the lists contain the correct types:

```python
from dataclasses import dataclass


@dataclass
class WeatherRow:
    """One day of weather, ready for a database insert."""

    date: str
    temperature_2m_max: float
    temperature_2m_min: float
    precipitation_sum: float
    wind_speed_10m_max: float


def to_rows(response: OpenMeteoResponse) -> list[WeatherRow]:
    """Convert a columnar Open-Meteo response into one record per day.

    Args:
        response: A validated response from the Open-Meteo archive API.

    Returns:
        One WeatherRow per date, in the order returned by the API.
    """
    d = response.daily
    return [
        WeatherRow(
            date=d.time[i],
            temperature_2m_max=d.temperature_2m_max[i],
            temperature_2m_min=d.temperature_2m_min[i],
            precipitation_sum=d.precipitation_sum[i],
            wind_speed_10m_max=d.wind_speed_10m_max[i],
        )
        for i in range(len(d.time))
    ]


rows = to_rows(parsed)
for row in rows:
    print(row)
```

This function has the same structure as the extract step you will write in Week 9 and orchestrate in Week 11. It also demonstrates the value of validation. `to_rows` indexes five lists in parallel and performs no checks of its own, which would be unsafe on unvalidated input but is completely safe here.

> Note the two different tools doing two different jobs. `OpenMeteoResponse` is a Pydantic model because it describes *outside* data that must be checked. `WeatherRow` is a dataclass because it describes *inside* data your own code just produced. Validating twice would be wasted work.

## Getting Data Back Out

Once the data is inside, you often need it back as plain Python or JSON -- to send to a database, write to a file, or return from an API:

```python
day = DailyWeather(date="2023-06-15", temp_max=24.1, temp_min=14.8,
                   precipitation=0.0, wind_speed=11.2)

print(day.model_dump())
print(day.model_dump_json())
```

`model_dump()` gives you a dictionary, `model_dump_json()` gives you a JSON string. In Week 9 you will hand `model_dump()` output straight to a Supabase insert.

Round-tripping is symmetrical:

```python
as_dict = day.model_dump()
restored = DailyWeather.model_validate(as_dict)
print(restored == day)
```

## Dataclass or Pydantic Model?

Both tools describe a record with typed fields. The difference is whether the values are checked.

| | `@dataclass` | Pydantic `BaseModel` |
|---|---|---|
| Standard library | Yes | No; install with `uv pip install pydantic` |
| Validates types at runtime | No | Yes |
| Coerces `"24.1"` to `24.1` | No | Yes |
| Constraints (ranges, patterns) | No | Yes, via `Field` |
| Custom validation rules | No | Yes, via validators |
| Serialize to JSON | Manual | `model_dump_json()` |
| Overhead per object | Almost none | Small, but real |

Use a **dataclass** for internal records your own code creates: intermediate results, configuration you wrote in the file, anything already inside the boundary.

Use a **Pydantic model** wherever data crosses in from outside: API responses, parsed files, environment settings, request payloads.

The overhead is worth taking seriously. Validating three fields on 365 records costs almost nothing. Validating on every row of a ten-million-row loop costs a noticeable amount. The rule is the same in both cases: validate once at the boundary, then use lightweight objects inside.

## Key Takeaways

Type hints describe data, and Pydantic enforces rules about it. A `BaseModel` uses the same field syntax as a dataclass, but it checks types when the object is constructed, converts values safely where the conversion is unambiguous, and raises a `ValidationError` that lists every problem at once with the exact path to each one. `Field` adds range and format constraints, `field_validator` adds rules for one field, and `model_validator` adds rules that span fields. Models can be nested inside one another, which is what allows you to describe a real API response rather than only a flat record.

The most important habit from this lesson is about design rather than syntax: **decide where your boundary is, validate there, and let everything inside it assume the data is correct.** That decision determines whether your pipeline tells you which sensor reading was null, or tells you only `ValueError: Input contains NaN` from somewhere inside scikit-learn.

## Check for Understanding

1. What does Pydantic do that a `@dataclass` does not?

    a. Generates `__init__` and `__repr__`
    b. Enforces the declared types at runtime, coercing where safe and raising `ValidationError` otherwise
    c. Allows type hints on fields
    d. Lets you attach methods to the record

    <details>
    <summary>Show Answer</summary>
    b -- Dataclasses do a, c, and d perfectly well. The difference is enforcement: a dataclass assigns whatever you pass it, while a Pydantic model checks it first.
    </details>

2. `temp_max="24.1"` is accepted but `temp_max="hot"` is rejected. Why the difference?

    a. Pydantic accepts any string shorter than five characters
    b. `"24.1"` has exactly one reasonable interpretation as a float, while `"hot"` has none -- Pydantic coerces when the conversion is unambiguous and refuses when it would be a guess
    c. `"hot"` contains letters, and Pydantic rejects all strings containing letters
    d. It is undefined behavior and varies between runs

    <details>
    <summary>Show Answer</summary>
    b -- Safe coercion is deliberate, because JSON, CSVs, and query strings all deliver numbers as text. The line is drawn at whether there is a single obvious conversion.
    </details>

3. You need to reject any record where `temp_min` is greater than `temp_max`. Which tool?

    a. `Field(ge=...)` on `temp_min`
    b. A `field_validator` on `temp_min`
    c. A `model_validator(mode="after")`, because the rule compares two fields and needs both to be populated
    d. A try/except around the constructor

    <details>
    <summary>Show Answer</summary>
    c -- A `field_validator` sees only its own field's value, and `Field` constraints are per-field constants. A cross-field rule needs `model_validator(mode="after")`, which runs once every field has been set.
    </details>

4. Your schema declares `temperature_2m_max: list[float]` and the API returns `[24.1, None, 30.0]`. What happens, and what is the benefit?

    a. The `None` is silently converted to `0.0`
    b. The whole response is accepted and the `None` becomes `NaN` later
    c. A `ValidationError` is raised identifying the exact path (`daily`, `temperature_2m_max`, index 1), so the bad reading is reported where it enters instead of causing an obscure failure downstream
    d. Only the second day is dropped and the rest is returned
    <details>
    <summary>Show Answer</summary>
    c -- Validation fails at the boundary with a precise location. Had it passed, the `None` would become a `NaN` in a DataFrame and surface much later as an opaque error from scikit-learn. If you would rather tolerate missing readings, that is a schema change (`list[float | None]`) -- a visible decision rather than an accident.
    </details>
