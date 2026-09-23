# Week 4 Assignments

This week you turn the model you saved in Week 3 into a reusable component. This assignment applies everything from Week 1 (classes, dataclasses, type hints, docstrings, `pytest`, and packaging) to a real machine learning model.

The warmup exercises rebuild the core mechanics quickly. The project is a single, guided build: the `weather_model` package that a cloud pipeline will import in Week 10. As in Week 1, **the structure of what you submit is part of what is being assessed.**

---

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_04/`. Inside it, build this structure:

```text
assignments_04/
├── warmup_04.py                        <- Part 1: the warmup exercises
├── weather_classification.csv          <- copied from the course repo (see below)
├── weather_model/                      <- Part 2: your component
│   ├── __init__.py
│   └── classifier.py
├── tests/
│   └── test_classifier.py
├── models/
│   ├── weather_classifier.pkl          <- copied from your Week 3 work
│   └── weather_classifier_metadata.json
├── conftest.py                         <- empty file (see below)
└── predict_weather.py
```

Two files to copy in before you start:

- Copy `weather_classification.csv` from `lessons/03_ML_classification/resources/` into `assignments_04/`. The warmups and the training step use it.
- Copy the `weather_classifier.pkl` and `weather_classifier_metadata.json` you saved in the Week 3 assignment into `assignments_04/models/`. If you do not have them, retrain and save a model using your Week 3 `train_classifier.py`.

Create an **empty** file called `conftest.py` at the top of `assignments_04/`, exactly as you did in Week 1. It lets `pytest` import your `weather_model` package when run from `assignments_04/`. Without it, the tests fail with `ModuleNotFoundError: No module named 'weather_model'`.

Install this week's packages if needed:

```bash
uv pip install scikit-learn joblib pytest
```

When finished, commit and open a PR as described in the [assignments README](README.md).

**Primary submission**: A link to your open GitHub PR. Your grader will run `pytest` from inside `assignments_04/`, so make sure it passes from there.

---

# Part 1: Warmup Exercises

Put all warmup exercises in a single file: `warmup_04.py`. Use comments to mark each question. Use `print()` to display outputs.

pytest will not discover `warmup_04.py` on its own, because the filename does not match `test_*.py`. Run its tests explicitly with:

```bash
pytest warmup_04.py -v
```

### Warmup Question 1

Write a class `ModelInfo` that reads a JSON file once in `__init__` and stores its contents.

- `__init__(self, path)` opens the file at `path`, loads it with `json.load`, and stores the result in `self.data`.
- A method `feature_count(self) -> int` returns the number of items in `self.data["features"]`.

Create a small JSON file with a `"features"` list (you can write it from Python), build a `ModelInfo` from it, and print the feature count. Add a comment: why is loading the file in `__init__` better than loading it inside `feature_count()` if the method is called many times?

### Warmup Question 2

Write a dataclass `DayForecast` with three type-hinted fields: `date` (str), `high_c` (float), and `will_rain` (bool). Give it a method `summary(self) -> str` that returns a readable sentence such as `"2023-06-15: high 24.1C, rain expected"`.

Create two `DayForecast` objects and print each summary. Add a comment: name one thing the `@dataclass` decorator wrote for you that you did not have to write by hand.

### Warmup Question 3

Write a function `parse_temperature(text: str) -> float` that converts a string like `"24.1"` to a float, and raises a `ValueError` with a message containing the word `"temperature"` when the text is not a number.

Then write two pytest tests in the same file:

- `test_parse_temperature_valid()` asserts that `parse_temperature("24.1")` returns `24.1` (use `pytest.approx`).
- `test_parse_temperature_bad_input_raises()` uses `pytest.raises(ValueError, match="temperature")` to confirm that `parse_temperature("hot")` raises the right error.

Run `pytest warmup_04.py -v` and confirm both pass. Add a comment: what would `pytest.raises(ValueError)` without `match` fail to catch?

---

# Part 2: Project — The `weather_model` Component

You will package your Week 3 classifier into a component with a clean interface, a test suite, and a script that uses it. When you finish, another program can predict running weather with three lines of code and no knowledge of how the model was built.

## Task 1: The `Prediction` Dataclass

In `weather_model/classifier.py`, write a dataclass `Prediction` with two type-hinted fields:

- `label` (str) -- either `"good"` or `"skip"`
- `probability` (float) -- the probability, from 0 to 1, that the day is good for running

Give it a docstring.

## Task 2: The `WeatherClassifier` Class

In the same file, write a class `WeatherClassifier`.

`__init__(self, model_path)` must:

- Accept a path to a saved `.pkl` file.
- Raise a `FileNotFoundError` with a helpful message if no file exists at that path.
- Otherwise load the pipeline with `joblib.load` and store it on `self`.

`predict(self, days)` must:

- Accept a list of dictionaries, each with the keys `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, and `wind_speed_10m_max`.
- Return an empty list if `days` is empty.
- Raise a `ValueError` naming the missing features if any required feature is absent.
- Select the four features in a fixed order, run the model, and return a list of `Prediction` objects, one per day, in the same order. Convert the model's `1` to `"good"` and `0` to `"skip"`, and take the probability of "good" from `predict_proba(...)[:, 1]`.

Give the class and the `predict` method type-hinted signatures and docstrings, including a `Raises:` note where an error can be raised.

## Task 3: The Package Entry Point

Write `weather_model/__init__.py` so that `from weather_model import WeatherClassifier, Prediction` works. Include an `__all__` list.

## Task 4: The Test Suite

Write tests in `tests/test_classifier.py`. They must pass when you run `pytest` from `assignments_04/`.

So the tests do not depend on any particular saved file, build a tiny model inside a fixture and save it to pytest's `tmp_path`, then load a `WeatherClassifier` from it. Write **at least six** tests covering both the success path and the error paths:

1. A clearly good day is labeled `"good"`.
2. A clearly bad day (cold, rainy, windy) is labeled `"skip"`.
3. The returned probability is between 0 and 1.
4. Passing three days returns three `Prediction` objects, in order.
5. Passing an empty list returns an empty list.
6. A day missing a required feature raises `ValueError` (use `pytest.raises(ValueError, match=...)`).
7. Constructing a `WeatherClassifier` with a path to a missing file raises `FileNotFoundError` (use `match`).

At least one test must use `@pytest.mark.parametrize` (for example, several days each with their expected label).

> Before you submit, deliberately break one thing in `classifier.py` (for example, always return `"skip"`) and confirm that a test fails. A test that cannot fail is not protecting anything. Note in a comment which test caught the change, then undo the break.

## Task 5: The Script

Write `predict_weather.py` that uses your **real** saved model in `models/weather_classifier.pkl`:

1. Create a `WeatherClassifier` from the saved model.
2. Predict for at least four hypothetical days covering clearly good, clearly bad, and borderline conditions.
3. Print a readable line per day with the inputs, the label, and the probability.

Put the work in a `main()` function under an `if __name__ == "__main__":` guard.

Add a comment explaining what would happen if you omitted the guard and another script imported `predict_weather.py` to reuse a helper.

## Task 6: Reflection

At the bottom of `predict_weather.py`, in a comment block, answer:

1. Your `predict()` selects the four features in a fixed order rather than using whatever order the caller passed. Describe a concrete bug this prevents.
2. The graded tests train their own tiny model in a fixture instead of loading `models/weather_classifier.pkl`. Why is that a better design for a test suite than depending on the real file?
3. In Week 10 a pipeline will import `WeatherClassifier` and call `predict()` on batches of weather records from a database. Name one thing about your component that makes it ready for that, and one thing you might add before it runs in production.

---

# Optional Extensions

## Extension A (Optional): Predict From a DataFrame (Low)

Add a method `predict_frame(self, frame)` that accepts a pandas DataFrame instead of a list of dictionaries and returns the same list of `Prediction` objects. Add a test for it.

## Extension B (Optional): A Confidence Threshold (Moderate)

Add an optional parameter to `predict` that only labels a day `"good"` when the probability is above a caller-supplied threshold (for example 0.7), and `"skip"` otherwise. Add tests that show the same borderline day flips label as the threshold changes.

## Extension C (Optional): Make It Installable (Moderate)

Write a minimal `pyproject.toml` for `weather_model` and install it with `uv pip install -e .`. Confirm your tests pass when run from any directory, not just `assignments_04/`. Explain in a comment what changed.

Good luck. The component you build this week is the one your pipeline will depend on later in the course.

---

<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

### Required Deliverables/Tasks

**General grading notes:**

- **The graded test suite is self-contained.** The tests in `tests/` train a tiny model in a fixture, so they do not depend on the student's specific `weather_classifier.pkl`. They should pass on any correct submission. `predict_weather.py` uses the real copied model, whose exact probabilities vary by the student's Week 3 model -- do not fail a student for specific probability values.
- **Class, dataclass, method, and feature names are exact.** `Use exactly as written (the tests and the Week 10 pipeline depend on these names)`: `WeatherClassifier`, `Prediction`, the `predict` method, the fields `label` and `probability`, and the feature keys `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `wind_speed_10m_max`.
- **File paths and folder layout are enforced by the automated `pytest` run, not by inspection.** The reviewer cannot see the filesystem. Do not fail a student for a path you cannot verify; what matters is that `pytest` passes from `assignments_04/`. The warmup file `warmup_04.py` is intentionally not collected by a bare `pytest` run, so do not fail a student because it is not part of the discovered suite.
- **Sample values are examples.** `Example — adapt to your own values`: the specific hypothetical days in `predict_weather.py` and in the tests.

**Part 1 — `warmup_04.py`** (run with `pytest warmup_04.py -v`):

- **Warmup Q1** — a `ModelInfo` class that loads a JSON file in `__init__` and a `feature_count()` method; a demo and a comment on why loading in `__init__` is better for repeated calls.
- **Warmup Q2** — a `DayForecast` dataclass with three type-hinted fields and a `summary()` method; two objects printed; a comment naming something `@dataclass` generated.
- **Warmup Q3** — a `parse_temperature` function that raises `ValueError` on bad input, plus `test_parse_temperature_valid` (using `pytest.approx`) and `test_parse_temperature_bad_input_raises` (using `pytest.raises(..., match="temperature")`); a comment on what `match` adds.

**Part 2 — the `weather_model` package:**

- **Task 1 — `Prediction` dataclass** in `weather_model/classifier.py` with `label: str` and `probability: float` and a docstring.
- **Task 2 — `WeatherClassifier` class**: `__init__` raises `FileNotFoundError` for a missing file and otherwise loads the pipeline with `joblib`; `predict` returns `[]` for empty input, raises `ValueError` naming missing features, selects the four features in fixed order, and returns one `Prediction` per day (converting 1/0 to "good"/"skip" and taking the probability from column 1). Type hints and docstrings present.
- **Task 3 — `weather_model/__init__.py`** re-exports `WeatherClassifier` and `Prediction` (so `from weather_model import WeatherClassifier` works) with an `__all__`.
- **Task 4 — `tests/test_classifier.py`**: at least six tests covering the successes (good label, skip label, probability in range, one result per day in order, empty list) and the error paths (missing feature raises `ValueError`, missing file raises `FileNotFoundError`), using a `tmp_path`-based fixture and `pytest.raises(..., match=...)`. At least one test uses `@pytest.mark.parametrize`. Passes via `pytest` from `assignments_04/`.
- **Task 5 — `predict_weather.py`**: loads the real saved model into a `WeatherClassifier`, predicts for at least four varied days, prints a readable line per day, with the work in `main()` under an `if __name__ == "__main__":` guard; a comment on omitting the guard.
- **Task 6 — Reflection**: a comment block answering the three questions (a bug the fixed feature order prevents; why the test fixture trains its own model; one production-readiness point and one thing to add).

### Optional Deliverables/Tasks

**Do not fail a student for omitting any of these.** They are marked "(Optional)".

- **Extension A (Optional)** — a `predict_frame` method accepting a DataFrame, with a test.
- **Extension B (Optional)** — a confidence threshold parameter on `predict`, with tests showing a borderline day flips label as the threshold changes.
- **Extension C (Optional)** — a minimal `pyproject.toml` and editable install, with a comment on what changed.

</details>
