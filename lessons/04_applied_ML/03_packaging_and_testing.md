# Packaging and Testing the Component

You have a `WeatherClassifier` class. This lesson turns it into an importable package, writes the tests that prove it works, and adds the script that uses it. Everything here is Week 1's packaging and testing material applied to a real component.

## The Package Layout

A single class in a script is not yet reusable by other code. We give it the same package structure you built in Week 1:

```text
weather_model/
├── __init__.py     <- the public entry point
└── classifier.py   <- the WeatherClassifier class and Prediction dataclass
```

Put the full class from the last lesson in `weather_model/classifier.py`. Then `__init__.py` decides what a caller can import directly from the package:

```python
# weather_model/__init__.py
"""weather_model: a reusable weather classifier component."""

from weather_model.classifier import WeatherClassifier, Prediction, FEATURES

__all__ = ["WeatherClassifier", "Prediction", "FEATURES"]
```

Because of these imports, a caller can write the short form instead of the full path:

```python
from weather_model import WeatherClassifier   # the shortcut
# instead of
from weather_model.classifier import WeatherClassifier   # the full path
```

This is the public entry point idea from Week 1. Callers depend on `weather_model`, not on the fact that the class currently lives in `classifier.py`. If you later split the code across more files, callers do not change.

## Making the Package Importable Under pytest

There is one setup detail you met in the Week 1 assignment. When you run `pytest` from your project root, pytest needs to be able to import `weather_model`. On its own, it searches from the test file's directory, where `weather_model` is not visible, and the tests fail with `ModuleNotFoundError: No module named 'weather_model'`.

The fix is the same as in Week 1: put an **empty** file named `conftest.py` at the project root. Its presence tells pytest to add the project root to the list of places Python searches for modules, so `from weather_model import WeatherClassifier` works from inside the tests.

```text
your_project/
├── weather_model/
│   ├── __init__.py
│   └── classifier.py
├── tests/
│   └── test_classifier.py
├── models/
│   └── weather_classifier.pkl
└── conftest.py            <- empty; makes weather_model importable under pytest
```

## Writing the Tests

Now the tests. They pin down what "correct" means for the component, so you can change its internals later and confirm nothing broke.

The tests need a saved model to load. Rather than depend on a file on disk, we build a tiny model inside a fixture and save it to a temporary directory that pytest provides through the built-in `tmp_path` fixture. This keeps the tests self-contained and fast, and each test run starts clean.

```python
# tests/test_classifier.py
import pytest
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from weather_model import WeatherClassifier, Prediction, FEATURES


@pytest.fixture
def model_path(tmp_path):
    """Train a tiny model on obvious days and save it to a temp file."""
    good = [{"temperature_2m_max": 18, "temperature_2m_min": 9, "precipitation_sum": 0.0, "wind_speed_10m_max": 10}] * 15
    bad = [{"temperature_2m_max": 2, "temperature_2m_min": -6, "precipitation_sum": 12.0, "wind_speed_10m_max": 40}] * 15
    X = pd.DataFrame(good + bad)[FEATURES]
    y = [1] * 15 + [0] * 15

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("logreg", LogisticRegression(max_iter=1000)),
    ])
    pipe.fit(X, y)

    path = tmp_path / "weather_classifier.pkl"
    joblib.dump(pipe, path)
    return path


@pytest.fixture
def clf(model_path):
    """A WeatherClassifier loaded from the saved tiny model."""
    return WeatherClassifier(model_path)
```

With those two fixtures, the tests themselves are short. Any test that names `clf` as a parameter receives a ready-to-use classifier.

```python
def test_good_day_predicted_good(clf):
    result = clf.predict([
        {"temperature_2m_max": 18, "temperature_2m_min": 9, "precipitation_sum": 0.0, "wind_speed_10m_max": 10}
    ])
    assert result[0].label == "good"


def test_bad_day_predicted_skip(clf):
    result = clf.predict([
        {"temperature_2m_max": 3, "temperature_2m_min": -5, "precipitation_sum": 10.0, "wind_speed_10m_max": 38}
    ])
    assert result[0].label == "skip"


def test_probability_is_between_zero_and_one(clf):
    result = clf.predict([
        {"temperature_2m_max": 15, "temperature_2m_min": 8, "precipitation_sum": 1.0, "wind_speed_10m_max": 12}
    ])
    assert 0.0 <= result[0].probability <= 1.0


def test_one_prediction_per_day_in_order(clf):
    days = [
        {"temperature_2m_max": 18, "temperature_2m_min": 9, "precipitation_sum": 0.0, "wind_speed_10m_max": 10},
        {"temperature_2m_max": 2, "temperature_2m_min": -6, "precipitation_sum": 12.0, "wind_speed_10m_max": 40},
    ]
    results = clf.predict(days)
    assert len(results) == 2
    assert all(isinstance(r, Prediction) for r in results)


def test_empty_list_returns_empty(clf):
    assert clf.predict([]) == []
```

Those cover the success path. Now the error paths, which matter just as much. The Week 1 pytest lesson taught you to prove that your code fails when it should, using `pytest.raises` with `match`.

```python
def test_missing_feature_raises(clf):
    with pytest.raises(ValueError, match="missing required features"):
        clf.predict([{"temperature_2m_max": 18, "temperature_2m_min": 9}])   # no precipitation or wind_speed_10m_max


def test_missing_model_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="No model file"):
        WeatherClassifier(tmp_path / "does_not_exist.pkl")
```

`test_missing_feature_raises` confirms that incomplete input produces a clear `ValueError` rather than a confusing failure inside the pipeline. `test_missing_model_file_raises` confirms that pointing the component at a missing file gives the helpful `FileNotFoundError` from `__init__`. Both use `match` so the test passes only when the *right* error is raised, not just any error.

## Running the Tests

Run `pytest` from the project root:

```bash
pytest -v
```

```text
tests/test_classifier.py::test_good_day_predicted_good PASSED
tests/test_classifier.py::test_bad_day_predicted_skip PASSED
tests/test_classifier.py::test_probability_is_between_zero_and_one PASSED
tests/test_classifier.py::test_one_prediction_per_day_in_order PASSED
tests/test_classifier.py::test_empty_list_returns_empty PASSED
tests/test_classifier.py::test_missing_feature_raises PASSED
tests/test_classifier.py::test_missing_model_file_raises PASSED

7 passed
```

Now confirm the tests can actually fail, which is the habit from Week 1. Temporarily break something in `classifier.py`, such as returning `"skip"` for every day, and rerun. `test_good_day_predicted_good` should turn red. Then undo the change. A test that cannot fail is not protecting anything.

## The Script That Uses the Component

Finally, a script that uses the real saved model, the one you trained on the full dataset. It loads the component and prints a small report. The work goes inside a `main()` function under the `if __name__ == "__main__":` guard, so importing this file does not run it, exactly as in Week 1.

```python
# predict_weather.py
"""Classify a few sample days using the saved weather model."""

from weather_model import WeatherClassifier

SAMPLE_DAYS = [
    {"temperature_2m_max": 18, "temperature_2m_min": 10, "precipitation_sum": 0.0, "wind_speed_10m_max": 12},
    {"temperature_2m_max": 22, "temperature_2m_min": 13, "precipitation_sum": 9.0, "wind_speed_10m_max": 14},
    {"temperature_2m_max": 25, "temperature_2m_min": 15, "precipitation_sum": 0.0, "wind_speed_10m_max": 33},
]


def main() -> None:
    """Load the component and print a prediction for each sample day."""
    classifier = WeatherClassifier("models/weather_classifier.pkl")
    for day, result in zip(SAMPLE_DAYS, classifier.predict(SAMPLE_DAYS)):
        print(f"{day['temperature_2m_max']:.0f}C, {day['precipitation_sum']:.0f}mm rain, "
              f"{day['wind_speed_10m_max']:.0f} km/h wind -> {result.label} ({result.probability:.2f})")


if __name__ == "__main__":
    main()
```

Running `python predict_weather.py` prints:

```text
18C, 0mm rain, 12 km/h wind -> good (0.97)
22C, 9mm rain, 14 km/h wind -> skip (0.01)
25C, 0mm rain, 33 km/h wind -> skip (0.33)
```

## Where This Leads

The `weather_model` package you just built is the component the rest of the course was pointing at. In Week 10, a pipeline will `from weather_model import WeatherClassifier`, load the saved model once, and call `predict()` on batches of real weather records pulled from a cloud database, recording the labels and confidence scores. Because you packaged and tested the component this week, that pipeline can depend on it without knowing anything about `joblib`, scaling, or probability columns.

## Key Takeaways

A package is a directory with an `__init__.py` that defines a public entry point, so callers depend on `weather_model` rather than on your internal file names. An empty `conftest.py` at the project root lets pytest import your package, the same fix you used in Week 1. The test suite covers the success path (correct labels, valid probabilities, one result per day) and the error paths (missing features, missing model file), using fixtures for setup and `pytest.raises(..., match=...)` for the failures. A `predict_weather.py` script under a `__main__` guard uses the component the way any caller would. Together, these turn a trained model into a component a pipeline can rely on.

## Check for Understanding

1. Why put `from weather_model.classifier import WeatherClassifier` in `weather_model/__init__.py`?

    a. It makes predictions faster
    b. It lets callers write `from weather_model import WeatherClassifier`, so the package's public interface stays stable even if you reorganize the internal files
    c. It is required for the package to import
    d. It prevents circular imports

    <details>
    <summary>Show Answer</summary>
    b -- the `__init__.py` defines the public entry point. Callers depend on `weather_model` itself, so you can move the class between files later without breaking their code.
    </details>

2. You run `pytest` from your project root and get `ModuleNotFoundError: No module named 'weather_model'`. What fixes it?

    a. Reinstalling scikit-learn
    b. Adding an empty `conftest.py` at the project root, which lets pytest add the root to the module search path
    c. Renaming the tests
    d. Moving the tests inside `weather_model/`

    <details>
    <summary>Show Answer</summary>
    b -- without it, pytest searches from the `tests/` directory, where `weather_model` is not visible. An empty `conftest.py` at the root makes the package importable, the same fix as in Week 1.
    </details>

3. Why does the test suite build a model in a fixture with `tmp_path` instead of loading a committed `.pkl` file?

    a. Committed files cannot be loaded in tests
    b. It keeps the tests self-contained and fast, and each run starts from a clean temporary directory rather than depending on a file on disk
    c. `tmp_path` trains the model automatically
    d. It is the only way to test a class

    <details>
    <summary>Show Answer</summary>
    b -- building a tiny model in a fixture and saving it to `tmp_path` means the tests do not depend on any external file and do not leave anything behind, which makes them reliable and repeatable.
    </details>

4. Why do the error-path tests use `pytest.raises(SomeError, match="...")` rather than `pytest.raises(SomeError)` alone?

    a. `match` makes the test run faster
    b. `match` checks the error message, so the test passes only when the specific expected error is raised, not any error of that type caused by an unrelated mistake
    c. It is required syntax
    d. Without `match`, the test is skipped

    <details>
    <summary>Show Answer</summary>
    b -- `match` confirms the error is the one you meant. Without it, an unrelated `ValueError` from a typo in the test setup would still make the test pass, giving false confidence.
    </details>
