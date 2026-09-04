# Assignment 4 Answer Key: From Model to Reusable Component

**Mentor note:** This week students turn the model they saved in Week 3 into a reusable component. They refactor the loose prediction code into a packaged `weather_model/` component built around a `WeatherClassifier` class, add a `pytest` suite, and write a `predict_weather.py` script that uses the real saved model. This applies the Week 1 material (classes, dataclasses, type hints, docstrings, `pytest`, packaging) to a real machine learning model.

Two things are graded differently. The **test suite** is self-contained: the tests train a tiny model inside a `tmp_path` fixture, so they do not depend on any student's specific `.pkl` and should pass on any correct submission. The **`predict_weather.py` script** uses the real copied model, whose exact probabilities depend on the student's Week 3 model, so do not fail a student for specific probability values.

**Contractual names (grade as EXACT).** The class `WeatherClassifier`, the dataclass `Prediction`, the method `predict`, the fields `label` and `probability`, the package name `weather_model`, and the four feature keys `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `wind_speed_10m_max` must appear exactly as written. The graded tests and the Week 10 and Week 11 pipelines import these names, so a spelling change is a real break, not a style choice. Everything else (sample day values, probability numbers, the tiny model's training rows) is an example the student adapts.

The verified demo outputs quoted below come from the lessons and the fixed course dataset. Cite them only where the student mirrors the lesson demo. Where a student uses their own saved model or their own sample days, values vary, so grade the method.

---

## Expected File Setup

Assignment lives in `assignments_04/`:

```text
assignments_04/
├── warmup_04.py                        # Part 1: the warmup exercises
├── weather_classification.csv          # copied from the course repo
├── weather_model/                      # Part 2: the component (a package)
│   ├── __init__.py                     # public entry point, re-exports
│   └── classifier.py                   # Prediction dataclass + WeatherClassifier
├── tests/
│   └── test_classifier.py              # pytest suite (>= 6 tests)
├── models/
│   ├── weather_classifier.pkl          # copied from Week 3 work
│   └── weather_classifier_metadata.json
├── conftest.py                         # empty; makes weather_model importable under pytest
└── predict_weather.py                  # script that uses the real saved model
```

Submitted as a PR link. The grader runs `pytest` from inside `assignments_04/`, so the suite must pass from there.

Two setup checks that cause most failures:

- **The empty `conftest.py` at the top of `assignments_04/`.** Without it, `pytest` cannot import the package and every test fails with `ModuleNotFoundError: No module named 'weather_model'`. This is the same fix students used in Week 1. The file must exist and may be empty. Do not fail a student for its contents; check only that its absence is not what broke the run.
- **The warmup file `warmup_04.py` is intentionally not collected by a bare `pytest` run**, because its name does not match `test_*.py`. It is run separately with `pytest warmup_04.py -v`. Do not fail a student because `warmup_04.py` is missing from the discovered suite.

---

# Part 1: Warmup Exercises (`warmup_04.py`)

Run with `pytest warmup_04.py -v`. Warmup 3 contains the two tests that this run collects. Warmups 1 and 2 are demonstration code that prints output.

### Warmup Q1 — `ModelInfo` — **Objective + Subjective**

A class `ModelInfo` that reads a JSON file once in `__init__` and stores its contents.

- `__init__(self, path)` opens the file at `path`, loads it with `json.load`, and stores the result in `self.data`.
- `feature_count(self) -> int` returns `len(self.data["features"])`.
- The student creates a small JSON file with a `"features"` list, builds a `ModelInfo` from it, and prints the feature count.

Reference:

```python
import json

class ModelInfo:
    def __init__(self, path):
        with open(path) as f:
            self.data = json.load(f)

    def feature_count(self) -> int:
        return len(self.data["features"])
```

**Objective checks:** the file is opened and read inside `__init__` (not inside `feature_count`); `self.data` holds the loaded dictionary; `feature_count` returns an `int` count of the `"features"` list.

**Subjective (the comment):** why loading in `__init__` is better than loading inside `feature_count()` when the method is called many times. A correct answer says the file is read from disk only once, so repeated calls to `feature_count()` reuse the already-loaded data instead of re-reading the file every time. This is the same "load once, use many times" idea the `WeatherClassifier` uses for its model.

### Warmup Q2 — `DayForecast` dataclass — **Objective + Subjective**

A dataclass `DayForecast` with three type-hinted fields: `date` (str), `high_c` (float), `will_rain` (bool), and a method `summary(self) -> str` returning a readable sentence.

Reference:

```python
from dataclasses import dataclass

@dataclass
class DayForecast:
    date: str
    high_c: float
    will_rain: bool

    def summary(self) -> str:
        rain = "rain expected" if self.will_rain else "no rain"
        return f"{self.date}: high {self.high_c}C, {rain}"
```

**Objective checks:** the `@dataclass` decorator is present; all three fields carry type hints; `summary` returns a string; two `DayForecast` objects are created and each summary is printed. The exact wording of the sentence is the student's choice.

**Subjective (the comment):** name one thing `@dataclass` generated. Accept any correct item: the `__init__` constructor, the `__repr__`, or the `__eq__` method. The point is that the decorator wrote code the student did not have to write by hand.

### Warmup Q3 — `parse_temperature` plus two tests — **Objective**

A function `parse_temperature(text: str) -> float` that converts a numeric string to a float and raises a `ValueError` whose message contains the word `"temperature"` on bad input, plus two `pytest` tests.

Reference:

```python
def parse_temperature(text: str) -> float:
    try:
        return float(text)
    except ValueError:
        raise ValueError(f"temperature must be a number, got {text!r}")


def test_parse_temperature_valid():
    assert parse_temperature("24.1") == pytest.approx(24.1)


def test_parse_temperature_bad_input_raises():
    with pytest.raises(ValueError, match="temperature"):
        parse_temperature("hot")
```

**Objective checks:**

- The error message contains the word `temperature` (required for the `match` in the second test to pass).
- `test_parse_temperature_valid` uses `pytest.approx` (comparing floats with `==` directly is the error to watch for).
- `test_parse_temperature_bad_input_raises` uses `pytest.raises(ValueError, match="temperature")`.
- Running `pytest warmup_04.py -v` shows both tests passing.

**Subjective (the comment):** what `pytest.raises(ValueError)` without `match` would fail to catch. A correct answer explains that without `match`, the test passes on *any* `ValueError`, including one raised by an unrelated bug in the test setup, so it would not confirm that the *right* error, for the right reason, was raised.

---

# Part 2: Project — The `weather_model` Component

**Overall check:** the student builds an importable package with a clean interface, a self-contained test suite, and a script that uses the real model. The proof that it works is a passing `pytest` run from `assignments_04/`. Grade the interface and the tests, not the specific probabilities.

## Task 1: The `Prediction` Dataclass — **Objective**

In `weather_model/classifier.py`, a dataclass `Prediction` with two type-hinted fields and a docstring.

Reference:

```python
from dataclasses import dataclass

@dataclass
class Prediction:
    """The model's verdict for a single day.

    Attributes:
        label: Either "good" or "skip".
        probability: The probability, from 0 to 1, that the day is good for running.
    """
    label: str
    probability: float
```

**Objective checks (names are EXACT):** the class is named `Prediction`; the fields are named `label` (typed `str`) and `probability` (typed `float`); the `@dataclass` decorator is present; a docstring is present. These names are imported by the tests and by later weeks, so they must match exactly.

## Task 2: The `WeatherClassifier` Class — **Objective**

In the same file, the class `WeatherClassifier` with a validating `__init__` and a `predict` method. This is the core deliverable of the week. See lesson `02_the_classifier_class.md` for the full reference implementation.

**`__init__(self, model_path)` — objective checks:**

- Accepts a path to a `.pkl` file.
- Raises `FileNotFoundError` with a helpful message when no file exists at that path. The check must happen *before* the load, so a missing file produces the clear message rather than an obscure `joblib` error.
- Otherwise loads the pipeline with `joblib.load` and stores it on `self` (for example `self.model`). The model is loaded once here, not inside `predict`, so many later predictions reuse the loaded model.
- Stores the fixed feature list on `self` (for example `self.features = FEATURES`).

**`predict(self, days)` — objective checks:**

- Accepts a list of dictionaries, each with the four feature keys.
- Returns an empty list when `days` is empty (this must be checked before building a DataFrame).
- Raises `ValueError` naming the missing feature(s) when any required feature is absent.
- Selects the four features in a fixed order, runs the model, and returns one `Prediction` per day in the same order.
- Converts the model's `1` to `"good"` and `0` to `"skip"`.
- Takes the probability of "good" from `predict_proba(...)[:, 1]` and returns it as a plain `float`.

**Documentation checks:** the class and the `predict` method have type-hinted signatures and docstrings, and the docstrings include a `Raises:` note where an error can be raised.

The four feature keys and the `1`-means-good convention are EXACT. Selecting the features in a fixed order (rather than trusting the caller's key order) is the important correctness point: a scikit-learn pipeline produces silently wrong answers if the columns arrive in a different order than it was trained on.

## Task 3: The Package Entry Point — **Objective**

`weather_model/__init__.py` re-exports the public names so `from weather_model import WeatherClassifier, Prediction` works, and includes an `__all__` list.

Reference:

```python
"""weather_model: a reusable weather classifier component."""

from weather_model.classifier import WeatherClassifier, Prediction, FEATURES

__all__ = ["WeatherClassifier", "Prediction", "FEATURES"]
```

**Objective checks:** `WeatherClassifier` and `Prediction` are importable directly from `weather_model`; an `__all__` list is present. Whether the student also re-exports `FEATURES` is fine either way; the tests in the lesson import it, so re-exporting it is the safer choice, but the graded requirement is only the two contractual names.

## Task 4: The Test Suite — **Objective**

`tests/test_classifier.py` must pass when `pytest` runs from `assignments_04/`. See lesson `03_packaging_and_testing.md` for the full reference suite.

**Fixture check:** the tests build a tiny model inside a fixture and save it to pytest's `tmp_path`, then load a `WeatherClassifier` from it. They must not depend on the committed `weather_classifier.pkl`. This keeps the suite self-contained, fast, and clean on each run.

**Required coverage — at least six tests spanning success and error paths:**

1. A clearly good day is labeled `"good"`.
2. A clearly bad day (cold, rainy, windy) is labeled `"skip"`.
3. The returned probability is between 0 and 1 (`0.0 <= p <= 1.0`).
4. Passing three days returns three `Prediction` objects, in order. (The lesson uses two days; three is what the assignment asks for. Either satisfies the "one result per day, in order" intent; check the count matches the input and the results are `Prediction` instances.)
5. Passing an empty list returns an empty list (`clf.predict([]) == []`).
6. A day missing a required feature raises `ValueError`, tested with `pytest.raises(ValueError, match=...)`.
7. Constructing a `WeatherClassifier` with a path to a missing file raises `FileNotFoundError`, tested with `match`.

**Additional required checks:**

- At least one test uses `@pytest.mark.parametrize` (for example, several days each with an expected label).
- Both error-path tests use `match=` so they pass only on the specific expected error, not any error of that type.

**The deliberate-break exercise (Subjective, comment):** the student temporarily breaks something in `classifier.py` (for example, always returning `"skip"`), confirms a test turns red, notes in a comment which test caught it, then undoes the break. The point is that a test that cannot fail protects nothing. Accept a comment naming the test that failed (typically the "good day" test if the break forces `"skip"`).

**Passing evidence (from the lesson, self-contained suite):** the reference suite reports `7 passed`. A student with the required seven tests plus any parametrized cases should show all passing.

## Task 5: The Script — **Objective (approach) + Subjective (comment)**

`predict_weather.py` uses the **real** saved model in `models/weather_classifier.pkl`.

**Objective checks:**

- Creates a `WeatherClassifier` from `models/weather_classifier.pkl`.
- Predicts for at least four hypothetical days covering clearly good, clearly bad, and borderline conditions.
- Prints a readable line per day showing the inputs, the label, and the probability.
- The work is inside a `main()` function under an `if __name__ == "__main__":` guard.

**Values vary.** The exact probabilities depend on the student's Week 3 model, so do not grade specific numbers. As a sanity check only, the lesson demo (three sample days on the course model) prints:

```text
18C, 0mm rain, 12 km/h wind -> good (0.97)
22C, 9mm rain, 14 km/h wind -> skip (0.01)
25C, 0mm rain, 33 km/h wind -> skip (0.33)
```

A clearly mild, dry, calm day should come out `good` with high confidence, and a cold, rainy, windy day should come out `skip`. Borderline days may land near 0.5 either way.

**Subjective (the guard comment):** what would happen if the `if __name__ == "__main__":` guard were omitted and another script imported `predict_weather.py` to reuse a helper. A correct answer explains that `main()` would run on import, so simply importing the file would load the model and print the report as a side effect, which is not what an importer wants.

## Task 6: Reflection — **Subjective**

A comment block at the bottom of `predict_weather.py` answering three questions.

1. **A concrete bug the fixed feature order prevents.** A correct answer describes passing the four features in a different key order than the model was trained on. Because `predict` selects `self.features` in a fixed order, the columns always align with training; without that, the pipeline would read, for example, wind speed as temperature and produce confident but wrong predictions with no error raised.
2. **Why the graded tests train their own tiny model instead of loading `models/weather_classifier.pkl`.** A correct answer notes that a self-contained fixture keeps the tests independent of any one saved file, so they run fast, start clean each time, and pass on any correct submission rather than breaking when the `.pkl` is missing, retrained, or different.
3. **One thing that makes the component ready for the Week 10 pipeline, and one thing to add before production.** Ready: it loads the model once and exposes a stable `predict(list[dict]) -> list[Prediction]` interface that hides `joblib`, scaling, and the probability column, so a pipeline can call it on batches without knowing the internals. To add: accept any reasonable answer, such as logging, input-schema or range validation beyond presence, handling missing or malformed values, batching or performance limits, model versioning, or monitoring.

---

# Optional Extensions — Not Required

**Do not fail a student for omitting any of these.** They are marked "(Optional)."

- **Extension A (Optional, Low):** a `predict_frame(self, frame)` method accepting a pandas DataFrame and returning the same list of `Prediction` objects, with a test. Check it selects the same four features in fixed order and reuses the same conversion logic.
- **Extension B (Optional, Moderate):** an optional threshold parameter on `predict` that labels a day `"good"` only when the probability exceeds a caller-supplied threshold. The required evidence is tests showing the *same* borderline day flips label as the threshold changes.
- **Extension C (Optional, Moderate):** a minimal `pyproject.toml` for `weather_model` installed with `uv pip install -e .`, plus a comment on what changed. After an editable install, the package imports from any directory, so the tests no longer depend on the `conftest.py` path trick.

---

## Running and Verification

The grader runs `pytest` from inside `assignments_04/`. A correct submission:

- Passes `pytest` from `assignments_04/` (the package test suite, at least seven passing tests, driven by the `tmp_path` fixture and independent of the committed `.pkl`).
- Passes `pytest warmup_04.py -v` (the two Warmup 3 tests).
- Runs `python predict_weather.py` and prints one readable line per sample day using the real saved model.

If the package suite fails with `ModuleNotFoundError: No module named 'weather_model'`, check first for the empty `conftest.py` at the top of `assignments_04/` before assuming a code error. That single missing file is the most common cause of a whole-suite failure, and the fix is the same one students used in Week 1.
