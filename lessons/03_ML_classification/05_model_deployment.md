# Model Deployment with joblib

Every script so far has followed the same pattern: load data, train a model, evaluate it, all in one run. That is fine for learning, but it is not how models are used in production, and this lesson closes that gap. It is the bridge to the rest of the course.

## Training Once, Predicting Many Times

In a real data pipeline, training and prediction are separated, sometimes by months:

- A model is trained offline, on historical data, now and then.
- The trained model is saved to disk.
- A separate script, the one that runs in production, loads the saved model and uses it to predict on new data.

This separation matters. The cost of training, which can be slow, is paid once. The cost of prediction, which is fast, is paid many times. A saved model can also be shared across scripts, moved to another machine, or rolled back to an earlier version if something goes wrong.

`joblib` is the standard library for saving and loading scikit-learn models. It installs with scikit-learn, so you already have it.

## Choosing Which Model to Deploy

You built two classifiers this week. KNN scored higher on accuracy (about 0.96 against 0.87), but we will deploy the **logistic regression pipeline**. This is a deliberate engineering decision, and the reasons are exactly the ones from the end of the logistic regression lesson:

- It produces smooth probability confidence scores, which the Week 10 pipeline uses.
- Its saved file is tiny, because it stores a handful of coefficients rather than the entire training set. KNN would have to carry all of its training data into the deployment and search through it for every prediction.
- Its coefficients are interpretable, so its decisions can be explained.

When two models are close enough, these practical differences decide which one ships. In a cloud pipeline that runs on a schedule, a small, fast, probabilistic model is worth a few points of accuracy. Recognizing that trade-off is part of the job.

## Saving a Model: joblib.dump

`joblib.dump` takes the object to save and the path to write it to.

```python
import joblib
import os

os.makedirs("models", exist_ok=True)

# `model` is the fitted logistic regression Pipeline from the last lesson
joblib.dump(model, "models/weather_classifier.pkl")
print("Model saved.")
```

The `.pkl` extension is conventional. It stands for "pickle," the underlying format. The file is a binary snapshot of the whole pipeline object: the scaler's learned mean and standard deviation, the classifier's coefficients, and the structure that connects them.

## Loading a Model: joblib.load

`joblib.load` takes the path and returns the original object, ready to use with no retraining:

```python
clf = joblib.load("models/weather_classifier.pkl")
print(type(clf))
```

It is good practice to confirm the loaded model behaves identically to the original before you rely on it:

```python
import numpy as np

assert np.array_equal(model.predict(X_test), clf.predict(X_test))
print("Loaded model matches the original.")
```

## Save the Whole Pipeline, Not Just the Model

This is a common and costly mistake. A trained logistic regression model knows its coefficients, but it does not know the scale of the data it was trained on. If you save only the classifier and later call `.predict()` on raw, unscaled data, the predictions will be wrong. They will be *silently* wrong, with no error, because the model simply computes with whatever numbers it receives.

The scaler is learned state too. It remembers the training set's mean and standard deviation for each feature, and those must be applied to any new data in exactly the same way. If you discard the scaler after training, you cannot reproduce that transformation.

Saving the full `Pipeline` solves this. The pipeline bundles the scaler and the model into one object. When you call `.predict()` on raw data, it applies the scaler first and then the model, in the same order they were trained. One file, no manual bookkeeping. This is the single most important reason we built the model as a pipeline in the first place.

## Saving Metadata Alongside the Model

A `.pkl` file is a binary blob. It does not, on its own, tell the next person what features it expects or what it was trained on. A small metadata file answers those questions.

There is also a versioning issue worth knowing: a serialized model is tied to the library versions that created it. A file made with one version of scikit-learn may fail to load in a very different one. In production this is handled by pinning exact versions. For now, recording the versions is enough.

```python
import json
import sys
import sklearn

FEATURES = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]

metadata = {
    "python_version": sys.version,
    "sklearn_version": sklearn.__version__,
    "features": FEATURES,
    "label": "good_for_running",
    "test_accuracy": 0.867,
    "test_f1": 0.871,
    "label_rule": {
        "temperature_2m_max": "7 to 26 C",
        "temperature_2m_min": ">= 0 C",
        "precipitation_sum": "< 3 mm",
        "wind_speed_10m_max": "< 30 km/h",
    },
}

with open("models/weather_classifier_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
print("Metadata saved.")
```

This records the three things anyone reusing the model needs: the library versions it requires, the features it expects and their order, and how it was trained.

## The Two-Script Pattern

In production the training code and the prediction code live in separate files. Here is the shape of both, which is exactly the structure you will build on in Week 4.

### Training script (run occasionally)

```python
import pandas as pd
import joblib
import json
import sys
import sklearn
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

os.makedirs("models", exist_ok=True)

df = pd.read_csv("resources/weather_classification.csv")
FEATURES = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]
X = df[FEATURES]
y = df["good_for_running"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = Pipeline([
    ("scaler", StandardScaler()),
    ("logreg", LogisticRegression(max_iter=1000)),
])
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
print(f"Test accuracy: {acc:.3f}   F1: {f1:.3f}")

joblib.dump(model, "models/weather_classifier.pkl")

metadata = {
    "python_version": sys.version,
    "sklearn_version": sklearn.__version__,
    "features": FEATURES,
    "label": "good_for_running",
    "test_accuracy": round(acc, 3),
    "test_f1": round(f1, 3),
}
with open("models/weather_classifier_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
print("Model and metadata saved to models/")
```

### Prediction script (run many times)

```python
import joblib
import json
import pandas as pd

clf = joblib.load("models/weather_classifier.pkl")
with open("models/weather_classifier_metadata.json") as f:
    metadata = json.load(f)

# Build new days using the exact feature names and order from the metadata
new_days = pd.DataFrame(
    [
        {"temperature_2m_max": 18, "temperature_2m_min": 10, "precipitation_sum": 0.0, "wind_speed_10m_max": 12},
        {"temperature_2m_max": 22, "temperature_2m_min": 13, "precipitation_sum": 9.0, "wind_speed_10m_max": 14},
        {"temperature_2m_max": 25, "temperature_2m_min": 15, "precipitation_sum": 0.0, "wind_speed_10m_max": 33},
    ]
)[metadata["features"]]

preds = clf.predict(new_days)
probs = clf.predict_proba(new_days)[:, 1]

for i, (pred, prob) in enumerate(zip(preds, probs)):
    label = "good for running" if pred == 1 else "skip"
    print(f"Day {i + 1}: {label}  (confidence: {prob:.2f})")
```

```text
Day 1: good for running  (confidence: 0.97)
Day 2: skip  (confidence: 0.01)
Day 3: skip  (confidence: 0.33)
```

Notice what the prediction script does *not* contain: no `StandardScaler`, no `fit`, no training data. It loads the file and calls `.predict()`. The pipeline applies the scaling automatically, using the statistics it learned during training. This is the payoff of saving the whole pipeline.

> **A limitation to keep in mind.** This model was trained on days that were mostly mild, so it has seen few very cold days. If you ask it about a day with a high of 3 degrees, it may confidently call it "good," because a single straight boundary cannot capture the lower temperature cutoff from so few cold examples. A model only knows the data it was trained on. Recording the training data in the metadata, and being cautious about inputs far outside that range, is part of using a model responsibly.

## Where This Leads

The `.pkl` file you can now produce is not just a homework artifact. It is the exact thing the rest of the course builds on:

- In **Week 4** you will wrap this saved model in a reusable class with a clean `predict()` method and a test suite, turning it into a component other code can import.
- In **Week 10** a cloud pipeline will load that component and run it on a schedule, predicting on new weather records and recording the confidence scores.

Everything downstream depends on the ability to train a model once, save it, and load it somewhere else. That is what you just learned.

## Check for Understanding

1. Why do we save the whole `Pipeline` instead of just the classifier?

    a. The pipeline file is smaller
    b. The pipeline includes the fitted scaler, so predictions on raw data are scaled correctly and automatically; saving only the classifier would produce silently wrong predictions on unscaled input
    c. scikit-learn cannot save a bare classifier
    d. It makes training faster

    <details>
    <summary>Show Answer</summary>
    b -- the classifier does not know the training data's scale. Without the scaler, raw inputs are computed as-is and the predictions are silently wrong. The pipeline carries the scaler with the model.
    </details>

2. The prediction script contains no `StandardScaler` and no training data. How does it produce correctly scaled predictions?

    a. It re-fits a scaler on the new data
    b. The saved pipeline already contains the fitted scaler, and calling `.predict()` applies it automatically before the model
    c. Logistic regression does not need scaling
    d. It cannot; the script is broken

    <details>
    <summary>Show Answer</summary>
    b -- the fitted scaler is part of the saved pipeline. When the loaded pipeline predicts, it applies that scaler first, using the statistics learned during training.
    </details>

3. Why deploy the logistic regression pipeline when KNN scored higher accuracy?

    a. Logistic regression is always more accurate in production
    b. It gives smooth probability confidence scores, saves to a tiny file, and is interpretable, while KNN must ship and search its entire training set; these operational advantages can outweigh a modest accuracy gap
    c. KNN cannot be saved with joblib
    d. Accuracy does not matter

    <details>
    <summary>Show Answer</summary>
    b -- for a scheduled cloud pipeline, a small, fast, probabilistic, interpretable model is often the better choice even at a small cost in accuracy. This is a real engineering trade-off.
    </details>

4. Why save a metadata file alongside the `.pkl`?

    a. It is required to load the model
    b. It records the library versions, the expected features and their order, and how the model was trained, which the binary `.pkl` does not convey on its own
    c. It makes predictions faster
    d. It replaces the need for the model file

    <details>
    <summary>Show Answer</summary>
    b -- the metadata answers the questions the binary file cannot: what versions it needs, what inputs it expects, and what it was trained on. This is what makes the model safe to reuse later.
    </details>
