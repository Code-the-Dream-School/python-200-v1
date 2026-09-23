# From Notebook to Component

At the end of Week 3 you had a trained pipeline saved to `weather_classifier.pkl`. That file is genuinely useful, but it is not yet something a team can build on. This lesson explains the gap between a saved model and a reusable component, and it frames the work of the week.

## A Saved Model Is Not Yet Reusable

Here is the prediction code from the Week 3 deployment lesson, the code any script would need in order to use the saved model:

```python
import joblib
import json
import pandas as pd

clf = joblib.load("models/weather_classifier.pkl")
with open("models/weather_classifier_metadata.json") as f:
    metadata = json.load(f)

new_days = pd.DataFrame(
    [{"temperature_2m_max": 18, "temperature_2m_min": 10, "precipitation_sum": 0.0, "wind_speed_10m_max": 12}]
)[metadata["features"]]

preds = clf.predict(new_days)
probs = clf.predict_proba(new_days)[:, 1]
label = "good" if preds[0] == 1 else "skip"
print(label, probs[0])
```

Read it as a caller would. To make one prediction, a script has to know the exact file path, load the model with `joblib`, load the metadata separately, build a DataFrame with the columns in the right order, call `predict` and `predict_proba` separately, remember that `1` means "good," and pull the probability out of column 1. That is a lot of detail, and every script that wants a prediction has to repeat all of it correctly.

Now imagine something changes. You retrain with a fifth feature, or you rename the model file, or you switch the label encoding. Every script that copied this code breaks, and you have to find and fix each one. The mechanics of using the model are spread across the whole codebase.

## What a Component Gives You

A **component** hides those mechanics behind a simple interface. Instead of the block above, a caller should be able to write this:

```python
from weather_model import WeatherClassifier

classifier = WeatherClassifier("models/weather_classifier.pkl")
result = classifier.predict([
    {"temperature_2m_max": 18, "temperature_2m_min": 10, "precipitation_sum": 0.0, "wind_speed_10m_max": 12}
])
print(result[0].label, result[0].probability)
```

The caller loads the model once, then calls `predict()` with plain dictionaries and reads back a clear result. It does not know that a `joblib` file, a scaler, a probability column, or a `1`-means-good convention exist. All of that is inside the component. If the internals change, the component changes in one place, and every caller keeps working as long as `predict()` still behaves the same way.

This is the same idea you met in Week 1. The `RunningConditions` class held its thresholds and applied them through one method, so callers did not thread four values through every call. In the Week 1 classes lesson we even said that in Week 4 you would write a `WeatherClassifier` that loads a model once in `__init__` and exposes a `predict()` method. This is that week.

## Load Once, Predict Many Times

There is a practical reason to load the model in `__init__` rather than inside `predict()`. Loading a `.pkl` file from disk is slow compared to making a prediction. If a pipeline classifies thousands of days, you want to pay the loading cost once, not once per day.

A class makes this natural. The `__init__` method runs when you create the object, so it is the right place to load the model. The `predict()` method then reuses the already-loaded model for every call. This is the same "configure once, apply many times" shape that most useful classes have, which you first saw with `RunningConditions`.

```python
classifier = WeatherClassifier("models/weather_classifier.pkl")  # loads the file once

for day in one_years_worth_of_days:      # thousands of predictions
    result = classifier.predict([day])   # reuses the loaded model each time
```

## Refactoring, and Why Tests Make It Safe

Turning the Week 3 script into a component is a **refactor**: you are changing the structure of the code while keeping its behavior the same. The predictions the component makes should be identical to the predictions the loose script made. Only the shape of the code changes.

Refactoring is exactly where tests earn their place, which is the point the Week 1 pytest lesson made in advance. Without tests, the only way to check a refactor is to run it and read the output, which catches obvious breakage and misses subtle breakage, such as features passed in the wrong order. With tests, you write down what "correct" means once, and then you can restructure the code freely and re-run the tests to confirm nothing changed.

This week you will write tests that pin down the component's behavior: that a clearly good day is labeled good, that a rainy day is labeled skip, that the probability is always between 0 and 1, and that bad input raises a clear error rather than a confusing one. Once those tests pass, the component is safe to hand to a teammate or drop into a pipeline.

## What You Will Build

By the end of the week you will have this project, which is the layout the Week 1 modules lesson showed you:

```text
assignments_04/
├── weather_model/            <- the component: importable library code
│   ├── __init__.py           <- the public entry point
│   └── classifier.py         <- the WeatherClassifier class
├── tests/
│   └── test_classifier.py    <- pytest tests for predictions and errors
├── models/
│   └── weather_classifier.pkl
├── conftest.py               <- makes the package importable under pytest
└── predict_weather.py        <- a script that uses the component
```

The next lesson builds the `WeatherClassifier` class. The lesson after that packages it, tests it, and writes the script that uses it.

## Key Takeaways

A saved `.pkl` model is useful but awkward to reuse, because every caller has to repeat the mechanics of loading it, preparing input, and interpreting output. A component hides those mechanics behind a simple `predict()` method, so callers depend on the interface rather than the internals. Loading the model once in `__init__` and reusing it in `predict()` is both natural and efficient. Turning the Week 3 script into a component is a refactor, and the tests you write are what make that refactor safe.
