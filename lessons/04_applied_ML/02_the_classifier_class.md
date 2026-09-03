# Building the WeatherClassifier Class

This lesson builds the `WeatherClassifier` class one piece at a time. It uses every tool from Week 1: a class with `__init__`, a dataclass, type hints, docstrings, and error handling. By the end you will have a component that loads a saved model and turns raw weather dictionaries into clear predictions.

## First, a Model to Load

The component loads a saved pipeline, so we need one on disk. This is the same training-and-saving code from the Week 3 deployment lesson, gathered into a small script. Run it once to produce `models/weather_classifier.pkl`.

```python
import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

os.makedirs("models", exist_ok=True)

df = pd.read_csv("weather_classification.csv")
FEATURES = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]
X, y = df[FEATURES], df["good_for_running"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = Pipeline([
    ("scaler", StandardScaler()),
    ("logreg", LogisticRegression(max_iter=1000)),
])
model.fit(X_train, y_train)
joblib.dump(model, "models/weather_classifier.pkl")
print("Saved models/weather_classifier.pkl")
```

In the assignment you will use the model you trained and saved in Week 3 instead of retraining here.

## The Prediction Result

Before the class, we define what a prediction *is*. A prediction has two parts: a label ("good" or "skip") and a probability (how confident the model is that the day is good). We could return these as a tuple or a dictionary, but a small dataclass is clearer and self-documenting, exactly as you learned in Week 1.

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

Now a caller can write `result.label` and `result.probability`, which reads far better than `result[0]` and `result[1]`, and the dataclass documents what each value means.

## Loading the Model in `__init__`

The class loads the saved pipeline once, when the object is created. `__init__` is the right place for that.

```python
from pathlib import Path
import joblib

FEATURES = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]


class WeatherClassifier:
    """Loads a saved weather pipeline once and predicts on many days."""

    def __init__(self, model_path: str | Path):
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"No model file at {model_path}. Train and save a model first."
            )
        self.model = joblib.load(model_path)
        self.features = FEATURES
```

Two design choices are worth noticing. First, `__init__` checks that the file exists before trying to load it, and raises a clear `FileNotFoundError` with a helpful message if it does not. Without this check, a missing file produces a confusing low-level error from deep inside `joblib`. Catching the problem early, with a message that says what to do, is part of building a component other people can use. Second, the loaded model is stored on `self`, so every later call to `predict()` reuses it. The slow disk load happens once.

## The `predict()` Method

Now the method that does the work. It takes a list of day dictionaries and returns a list of `Prediction` objects, one per day.

```python
import pandas as pd

    def predict(self, days: list[dict]) -> list[Prediction]:
        """Predict whether each day is good for running.

        Args:
            days: A list of dictionaries, each with the keys temperature_2m_max, temperature_2m_min,
                precipitation, and wind_speed_10m_max.

        Returns:
            One Prediction per input day, in the same order.
        """
        if not days:
            return []

        frame = pd.DataFrame(days)
        missing = [f for f in self.features if f not in frame.columns]
        if missing:
            raise ValueError(f"missing required features: {missing}")

        X = frame[self.features]
        labels = self.model.predict(X)
        probabilities = self.model.predict_proba(X)[:, 1]

        return [
            Prediction("good" if int(label) == 1 else "skip", float(prob))
            for label, prob in zip(labels, probabilities)
        ]
```

Read what this method handles for the caller:

- **Empty input.** If `days` is empty, it returns an empty list rather than failing.
- **Column order.** It selects `self.features` in the correct order, so a caller can pass the keys in any order and still get correct results. This matters, because a model silently produces wrong answers if features arrive in the wrong order.
- **Missing features.** If a required feature is absent, it raises a clear `ValueError` naming what is missing, rather than letting the pipeline fail with an obscure message.
- **The `1`-means-good convention.** It converts the model's `0` and `1` into the words "good" and "skip," so the caller never has to remember the encoding.
- **The probability column.** It pulls the probability of "good" out of column 1 and returns it as a plain float.

Every one of these is a detail the loose Week 3 script pushed onto its callers. The component absorbs them.

## The Full Class

Putting it together, here is the whole component:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd

FEATURES = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]


@dataclass
class Prediction:
    """The model's verdict for a single day."""
    label: str          # "good" or "skip"
    probability: float  # probability the day is good for running


class WeatherClassifier:
    """Loads a saved weather pipeline once and predicts on many days."""

    def __init__(self, model_path: str | Path):
        """Load the saved pipeline from disk.

        Args:
            model_path: Path to a .pkl file saved with joblib.

        Raises:
            FileNotFoundError: If no file exists at model_path.
        """
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"No model file at {model_path}. Train and save a model first."
            )
        self.model = joblib.load(model_path)
        self.features = FEATURES

    def predict(self, days: list[dict]) -> list[Prediction]:
        """Predict whether each day is good for running.

        Args:
            days: A list of dictionaries, each with the four feature keys.

        Returns:
            One Prediction per input day, in the same order.

        Raises:
            ValueError: If any required feature is missing.
        """
        if not days:
            return []

        frame = pd.DataFrame(days)
        missing = [f for f in self.features if f not in frame.columns]
        if missing:
            raise ValueError(f"missing required features: {missing}")

        X = frame[self.features]
        labels = self.model.predict(X)
        probabilities = self.model.predict_proba(X)[:, 1]

        return [
            Prediction("good" if int(label) == 1 else "skip", float(prob))
            for label, prob in zip(labels, probabilities)
        ]
```

> `from __future__ import annotations` at the top lets you write `str | Path` in the type hints on any supported version of Python. The line `label: str` and `probability: float` in the dataclass are the annotations that make it a dataclass, exactly as in Week 1.

## Using the Component

Now using the model takes three lines:

```python
classifier = WeatherClassifier("models/weather_classifier.pkl")

results = classifier.predict([
    {"temperature_2m_max": 18, "temperature_2m_min": 10, "precipitation_sum": 0.0, "wind_speed_10m_max": 12},
    {"temperature_2m_max": 22, "temperature_2m_min": 13, "precipitation_sum": 9.0, "wind_speed_10m_max": 14},
    {"temperature_2m_max": 25, "temperature_2m_min": 15, "precipitation_sum": 0.0, "wind_speed_10m_max": 33},
])

for result in results:
    print(f"{result.label:5s}  ({result.probability:.2f})")
```

```text
good   (0.97)
skip   (0.01)
skip   (0.33)
```

The caller never touches `joblib`, never builds a DataFrame, and never thinks about column 1. It creates the classifier, calls `predict()`, and reads the results. That is what a component is for.

## Key Takeaways

The `WeatherClassifier` class loads the saved pipeline once in `__init__`, checking first that the file exists and raising a clear error if it does not. Its `predict()` method takes plain dictionaries, validates them, selects the features in the correct order, runs the model, and returns readable `Prediction` dataclasses. Type hints and docstrings make the interface self-documenting. Every messy detail from the Week 3 script is now hidden inside the component, so callers depend only on `predict()`. Next lesson we package this class and write the tests that prove it works.

## Check for Understanding

1. Why load the model in `__init__` rather than inside `predict()`?

    a. `predict()` cannot load files
    b. Loading a `.pkl` from disk is slow, and loading it once in `__init__` lets every later `predict()` call reuse the already-loaded model
    c. `__init__` runs faster than other methods
    d. It is required by joblib

    <details>
    <summary>Show Answer</summary>
    b -- the disk load is the slow part. Doing it once in `__init__` and reusing the model in `predict()` avoids reloading the file for every prediction.
    </details>

2. Why does `predict()` select `self.features` in a fixed order instead of using the columns as they arrive?

    a. To make the code shorter
    b. Because a model produces silently wrong predictions if the features are passed in a different order than it was trained on
    c. Because pandas requires it
    d. It does not matter; any order works

    <details>
    <summary>Show Answer</summary>
    b -- the model expects features in a specific order. Selecting them explicitly means the caller can pass keys in any order and still get correct results, and a missing feature is caught rather than silently misaligned.
    </details>

3. Why return a `Prediction` dataclass instead of a tuple `(label, probability)`?

    a. Dataclasses are faster
    b. `result.label` and `result.probability` are clearer and self-documenting, and the dataclass records what each value means
    c. Tuples cannot hold a string and a float
    d. joblib requires a dataclass

    <details>
    <summary>Show Answer</summary>
    b -- a dataclass gives each value a name, so callers read `result.label` instead of `result[0]`, and the class documents the meaning of each field.
    </details>

4. What does raising `FileNotFoundError` with a helpful message in `__init__` accomplish?

    a. It makes the model load faster
    b. It replaces a confusing low-level error from joblib with a clear message that tells the user what went wrong and what to do
    c. It prevents the model from ever failing
    d. It is required to load a pipeline

    <details>
    <summary>Show Answer</summary>
    b -- checking for the file first lets the component fail early with a clear, actionable message, which is part of making a component that other people can use safely.
    </details>
