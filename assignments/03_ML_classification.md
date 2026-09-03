# Week 3 Assignments

This week's assignments cover the Week 3 material:

- Preprocessing in a `Pipeline`: scaling and one-hot encoding with a `ColumnTransformer`
- k-Nearest Neighbors and choosing `k` with cross-validation
- Logistic Regression, its coefficients, and its probabilities
- Evaluating classifiers with accuracy, precision, recall, F1, and the confusion matrix
- Saving and loading a trained model with `joblib`

The warmup exercises build muscle memory for the core mechanics, so try to work through them without AI assistance. The mini-project asks you to build, evaluate, and **save** a real weather classifier. The model you save this week is the one you will wrap into a reusable component next week, so keep your files.

---

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_03/`. Inside it, build this structure:

```text
assignments_03/
├── warmup_03.py                 <- Part 1: the warmup exercises
├── weather_classification.csv   <- copied from the course repo (see below)
├── train_classifier.py          <- Part 2: fetch, build, evaluate, save
├── predict.py                   <- Part 2: load the saved model and predict
├── models/                      <- your saved .pkl and metadata.json go here
└── outputs/                     <- any plots your code saves
```

Copy `weather_classification.csv` from the course repo at `lessons/03_ML_classification/resources/weather_classification.csv` into your `assignments_03/` folder before you start. The warmups use it.

Install this week's new package if you have not already (it installs with scikit-learn, so you likely have it):

```bash
uv pip install scikit-learn joblib
```

When finished, commit and open a PR as described in the [assignments README](README.md).

**Primary submission**: A link to your open GitHub PR. Make sure your saved model files in `models/` are committed.

---

# Part 1: Warmup Exercises

Put all warmup exercises in a single file: `warmup_03.py`. Use comments to mark each section and question (for example `# --- KNN ---` and `# Q1`). Use `print()` to display outputs and save any figures to `outputs/`.

Run this setup block at the top of `warmup_03.py`.

Use exactly as written:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, ConfusionMatrixDisplay, classification_report,
)
import joblib

df = pd.read_csv("weather_classification.csv")
numeric = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]
X = df[numeric]
y = df["good_for_running"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

## Preprocessing

### Preprocessing Question 1

Fit a `StandardScaler` on `X_train` only, then transform both `X_train` and `X_test`. Print the mean of each column of the scaled training data (they should all be very close to 0). Add a comment explaining, in one sentence, why you fit the scaler on `X_train` only.

### Preprocessing Question 2

The `season` column in the dataset is categorical. One-hot encode it with `OneHotEncoder(sparse_output=False)` and print the resulting array's shape and the category names from `encoder.get_feature_names_out()`. Add a comment: how many columns did the single `season` column become, and why is that number what it is?

### Preprocessing Question 3

Build a `ColumnTransformer` that applies a `StandardScaler` to the four numeric columns and a `OneHotEncoder` to `season`. Wrap it with a `LogisticRegression` in a `Pipeline`. Fit the pipeline on the training data (include `season` in your feature columns for this question) and print its test accuracy. Add a comment: what does the pipeline do automatically that you would otherwise have to do by hand?

## KNN

### KNN Question 1

Build a `Pipeline` of `StandardScaler` and `KNeighborsClassifier(n_neighbors=5)`. Fit it on the training data and print the test accuracy and the full classification report.

### KNN Question 2

Loop over `k` values `[1, 3, 5, 7, 9, 11, 15, 21]`. For each, build the scaled pipeline and compute the mean 5-fold cross-validation accuracy on the **training** data. Print each `k` with its mean CV score. Add a comment naming the `k` you would choose and why.

### KNN Question 3

Fit KNN once *without* scaling (on raw `X_train`) and once *with* scaling, both using `n_neighbors=5`. Print both test accuracies. Add a comment: did scaling help, and why would scaling matter for a distance-based model?

## Logistic Regression

### Logistic Regression Question 1

Build a `Pipeline` of `StandardScaler` and `LogisticRegression(max_iter=1000)`. Fit it and print the test accuracy, precision, recall, and F1 (for the "good" class).

### Logistic Regression Question 2

Print each feature name alongside its coefficient from the fitted logistic regression (use `pipeline.named_steps["..."].coef_[0]`). Add a comment: which features push most strongly toward "skip," and does that match your intuition about running weather?

### Logistic Regression Question 3

Use `predict_proba` to print the probability of "good" for the first five test days, rounded to two decimals. Add a comment: what does a probability near 0.5 tell you about the model's confidence for that day?

## Evaluation

### Evaluation Question 1

For your logistic regression pipeline, build a confusion matrix on the test set and display it with `ConfusionMatrixDisplay`, using `display_labels=["skip", "good"]`. Save the figure to `outputs/logreg_confusion_matrix.png`. Add a comment: how many false positives and how many false negatives did the model make, and which kind of error would matter more for a running app?

## joblib

### joblib Question 1

Take your fitted logistic regression pipeline and save it to `models/warmup_model.pkl` with `joblib.dump`. Load it back with `joblib.load` and confirm it produces identical predictions:

```python
loaded = joblib.load("models/warmup_model.pkl")
assert (loaded.predict(X_test) == pipeline.predict(X_test)).all()
print("Predictions match.")
```

Add a comment: what would go wrong if you had saved only the `LogisticRegression` step without the scaler, then called `.predict()` on raw data?

---

# Part 2: Mini-Project — Build and Deploy a Weather Classifier

You will build a classifier that predicts whether a day is good for running, evaluate it, and save it to disk so it can be used later. In Week 4 you will wrap this saved model into a reusable component, and in Week 10 a cloud pipeline will load it. This is the beginning of the end-to-end pipeline the course is building toward.

Split your work across two files: `train_classifier.py` (fetch, label, build, evaluate, save) and `predict.py` (load and predict). Save any plots to `outputs/`.

## File 1: `train_classifier.py`

### Task 1: Fetch the Data

Use the free Open-Meteo historical API (no key required) to download one year of daily weather for a city of your choice. Use these four daily variables: `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, and `wind_speed_10m_max_10m_max`.

Example — adapt the latitude, longitude, and dates to your city:

```python
import requests
import pandas as pd

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 35.23,
    "longitude": -80.84,
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "wind_speed_10m_max_10m_max",
    ],
    "timezone": "America/New_York",
}
response = requests.get(url, params=params)
response.raise_for_status()
df = pd.DataFrame(response.json()["daily"])
df["date"] = pd.to_datetime(df["time"])
df = df.drop("time", axis=1)
```

Print the shape and the first few rows, and add a comment noting which city you chose.

### Task 2: Engineer the Label

Create a `good_for_running` column that is 1 when a day is good and 0 otherwise. A day is good when the high is between 7 and 26 degrees, the low is at least 0, precipitation is under 3 mm, and the maximum wind is under 30 km/h. You may adjust these thresholds for your climate, but document any change in a comment.

Print the class balance (how many good days and how many skip days). Add a comment: what fraction of days are good, and does that seem reasonable for your city's climate? If your data is very imbalanced, note which metrics will matter most because of it.

### Task 3: Build and Evaluate a KNN Classifier

Split the data into training and test sets (80/20, `random_state=42`, `stratify` on the label). Build a `Pipeline` of `StandardScaler` and `KNeighborsClassifier`. Use 5-fold cross-validation on the training data to choose `k` from at least five values, then fit your chosen model and print its test accuracy and full classification report.

### Task 4: Build and Evaluate a Logistic Regression Classifier

Build a `Pipeline` of `StandardScaler` and `LogisticRegression(max_iter=1000)`. Fit it and print its test accuracy, precision, recall, F1, and classification report. Then print each feature's coefficient and add a comment interpreting them: which conditions most strongly push a day toward "skip"?

### Task 5: Compare and Choose

Compare your two classifiers. In a comment, answer:

- Which model had higher accuracy on your data?
- For a running app, is accuracy the metric you care about most, or would you weigh precision or recall more heavily? Explain in terms of false positives (sent out on a bad day) and false negatives (missed a good day).
- Which model will you deploy, and why? Consider not only the scores but also model size, prediction speed, interpretability, and whether you want probability confidence scores. Either choice can be correct if you justify it.

### Task 6: Save the Model

Save your chosen fitted pipeline to `models/weather_classifier.pkl` with `joblib.dump`. Save a metadata file to `models/weather_classifier_metadata.json` containing at least: the Python and scikit-learn versions, the feature names in order, the label rule you used, your city, and the test accuracy and F1 of the saved model. Print a confirmation message when both files are written.

## File 2: `predict.py`

This script simulates using the model in production. It must contain **no training code**: no `fit`, no cross-validation, no data fetching from the API.

### Task 7: Load and Predict

Load the pipeline from `models/weather_classifier.pkl` and the metadata from the JSON file. Print the model's key metadata (city, features, test accuracy). Then build a small DataFrame of at least four hypothetical days covering a clearly good day, a clearly bad day, and at least one borderline day, using the feature names from the metadata so the columns match. For each day, print the four inputs, the predicted label (good or skip), and the model's confidence (the probability of "good").

### Task 8: Reflect

At the bottom of `predict.py`, in a comment block, answer:

1. Pick your borderline day. What probability did the model give it? Would you call the model confident or uncertain, and how would you handle a day where it predicts 0.52?
2. `predict.py` has no training code. What would break if someone ran `predict.py` before `train_classifier.py` had ever been run? How could you make the error message more helpful?
3. In Week 10 this model will run inside a cloud pipeline that classifies each day's weather automatically. Name one thing about your current `predict.py` that would need to change to support that.

---

# Optional Extensions

## Extension A (Optional): Add Season as a Feature (Low)

Add a `season` column derived from the month, and use a `ColumnTransformer` to scale the numeric features and one-hot encode `season` inside your pipeline. Does adding season change your test scores? Add a comment with what you found, and a possible reason.

## Extension B (Optional): A Second City (Moderate)

Train your classifier on one city and evaluate it on a different city's data with a very different climate. Does accuracy drop? Add a comment explaining why a model trained on one climate might not transfer to another.

## Extension C (Optional): Tune Regularization (Moderate)

For your logistic regression pipeline, use cross-validation to compare several values of `C` (for example `0.01, 0.1, 1.0, 10.0, 100.0`). Does the best `C` improve your F1 over the default? Add a comment with your finding.

Good luck. Keep your saved model files — you will reuse them in Week 4.

---

<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

### Required Deliverables/Tasks

**General grading notes:**

- **Mini-project numbers vary by student.** The student chooses their own city and year, so class balance, accuracy, precision, recall, F1, and coefficients will differ. Do not fail a student for numbers that differ from any reference. Grade whether the workflow is correct and the interpretation is reasonable.
- **Either model may be deployed.** In Task 5, both KNN and logistic regression are defensible choices for deployment. Do not fail a student for choosing either one, as long as they justify it.
- **File paths and figure names are conventions, not pass/fail.** The reviewer cannot see the filesystem. Do not fail a student for a differently named plot or a different directory, as long as the described file is produced.
- **Sample values are examples.** `Example — adapt to your own layout`: the latitude/longitude/dates in Task 1 and the city choice. `Use exactly as written`: the warmup setup block, because the later warmup questions depend on those variable names.

**Part 1 — `warmup_03.py`** (uses the provided `weather_classification.csv`):

- **Preprocessing Q1** — a `StandardScaler` fit on `X_train` only and applied to both sets; scaled-train column means printed (near 0); a comment on why the scaler is fit on training data only.
- **Preprocessing Q2** — `season` one-hot encoded; the resulting shape and category names printed; a comment on the number of new columns.
- **Preprocessing Q3** — a `ColumnTransformer` (scale numeric, one-hot `season`) inside a `Pipeline` with logistic regression, fit and test accuracy printed; a comment on what the pipeline automates.
- **KNN Q1** — a scaled KNN pipeline (`n_neighbors=5`); test accuracy and classification report printed.
- **KNN Q2** — cross-validation over the listed `k` values with mean scores printed; a comment choosing a `k`.
- **KNN Q3** — unscaled vs scaled KNN accuracy printed; a comment on whether scaling helped and why it matters for a distance-based model.
- **Logistic Regression Q1** — a scaled logistic regression pipeline; accuracy, precision, recall, F1 printed.
- **Logistic Regression Q2** — each feature's coefficient printed; a comment interpreting which features push toward "skip."
- **Logistic Regression Q3** — `predict_proba` probabilities for the first five test days printed; a comment on what a probability near 0.5 means.
- **Evaluation Q1** — a confusion matrix displayed and saved to `outputs/`; a comment on the counts of false positives and false negatives and which matters more.
- **joblib Q1** — the pipeline saved and reloaded, with an assertion that predictions match; a comment on why saving only the classifier (without the scaler) would fail.

**Part 2 — `train_classifier.py`:**

- **Task 1** — daily weather fetched from Open-Meteo (any city/year); shape and first rows printed; a comment naming the city.
- **Task 2** — a `good_for_running` label engineered from the thresholds; class balance printed; a comment on the fraction of good days.
- **Task 3** — a scaled KNN pipeline with `k` chosen by cross-validation; test accuracy and classification report printed.
- **Task 4** — a scaled logistic regression pipeline; accuracy/precision/recall/F1 and classification report printed; coefficients printed and interpreted in a comment.
- **Task 5** — a written comparison covering which model scored higher, the false-positive vs false-negative trade-off for a running app, and a justified deployment choice.
- **Task 6** — the chosen pipeline saved to `models/weather_classifier.pkl` and a metadata JSON saved with versions, feature names, label rule, city, and test scores; a confirmation printed.

**Part 2 — `predict.py`:**

- **Task 7** — loads the saved pipeline and metadata (no training code), prints key metadata, and predicts label and confidence for at least four hypothetical days including a borderline one.
- **Task 8** — a reflection comment block answering the three questions (borderline probability and how to handle 0.52; what breaks if `predict.py` runs before training and how to improve the error; one change needed for the Week 10 pipeline).

### Optional Deliverables/Tasks

**Do not fail a student for omitting any of these.** They are marked "(Optional)".

- **Extension A (Optional)** — `season` added via a `ColumnTransformer`, with a comment on whether it changed the scores.
- **Extension B (Optional)** — train on one city, evaluate on another, with a comment on transfer across climates.
- **Extension C (Optional)** — cross-validated comparison of several `C` values, with a comment on whether the best `C` improved F1.

</details>
