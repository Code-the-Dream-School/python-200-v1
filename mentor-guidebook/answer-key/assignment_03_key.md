# Assignment 3 Answer Key: Classification and Model Deployment

**Mentor note:** This key covers the Week 3 warmups and the two-file mini-project. The warmups run on the fixed dataset `weather_classification.csv` (600 rows, 305 good / 295 skip) with `random_state=42`, so their numbers are reproducible and are given below. Grade them against these values. The mini-project fetches live Open-Meteo data for a city and year the student chooses, so its class balance, accuracy, precision, recall, F1, and coefficients will differ from student to student. Do not fail a student for numbers that differ from any reference. Grade whether the workflow is correct and the interpretation is reasonable.

**The one talking point mentors are asked about most:** "KNN scored higher, so why does the course deploy Logistic Regression?" The answer is a deliberate engineering trade-off, explained in the Task 5 notes below. Both models are defensible deployment choices in the project as long as the student justifies the choice. In the lessons the course itself deploys Logistic Regression, and mentors should be able to explain that reasoning.

**Two known issues in the assignment text mentors should know about:**

1. In Task 1, the variable name `wind_speed_10m_max_10m_max` is a typo with a duplicated suffix. The correct Open-Meteo daily variable is `wind_speed_10m_max`. A student who used `wind_speed_10m_max` (matching the lessons, the warmup setup block, and the metadata feature list) is correct. Do not penalize that. A student who copied the typo literally will have gotten an API error or a mismatched column name and had to correct it.
2. The warmup KNN Q2 `k` list is `[1, 3, 5, 7, 9, 11, 15, 21]`, which differs slightly from the lesson's list. Grade against the assignment's list, given below.

---

## Expected File Setup

Assignment lives in `assignments_03/`:

```
assignments_03/
├── warmup_03.py                 # Part 1: all warmup exercises
├── weather_classification.csv   # copied from the course repo
├── train_classifier.py          # Part 2: fetch, label, build, evaluate, save
├── predict.py                   # Part 2: load the saved model and predict
├── models/                      # saved .pkl and metadata.json
└── outputs/                     # saved plots
```

Submitted as a PR. The saved model files in `models/` must be committed, because Week 4 reuses them. The warmup setup block at the top of `warmup_03.py` must be used exactly as written, because the later warmup questions depend on those variable names (`df`, `X`, `y`, `X_train`, `X_test`, `y_train`, `y_test`, `numeric`). File paths and plot names are conventions, not pass/fail; the reviewer cannot see the filesystem, so grade whether the described file is produced.

**Reference values from the fixed warmup setup** (`train_test_split(..., test_size=0.2, random_state=42, stratify=y)`): the training set has 480 rows, the test set has 120 rows, and the test set holds 61 good days and 59 skip days.

---

# Part 1: Warmup Exercises (`warmup_03.py`)

## Preprocessing

### Preprocessing Q1 — **Objective + Subjective**
Fit `StandardScaler` on `X_train` only, transform both sets. The printed column means of the scaled training data are all very close to 0 (on the order of `1e-16`). The comment must state that the scaler is fit on the training data only to avoid **data leakage**: the scaler learns each feature's mean and standard deviation, and learning them from the test set would let the test data influence the model and make the evaluation look better than it truly is.

Reference:
```python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print(X_train_scaled.mean(axis=0))   # all ~0
```

### Preprocessing Q2 — **Objective + Subjective**
One-hot encode the `season` column with `OneHotEncoder(sparse_output=False)`. The printed array shape is `(600, 4)` (or `(480, 4)` if the student encoded only the training rows; either is acceptable as long as the second dimension is 4). `get_feature_names_out()` returns `['season_fall', 'season_spring', 'season_summer', 'season_winter']` (the encoder sorts categories alphabetically). The comment must state that the single `season` column became **4 columns because there are 4 distinct seasons**, and one-hot encoding creates one column per category.

### Preprocessing Q3 — **Objective + Subjective**
Build a `ColumnTransformer` that applies `StandardScaler` to the four numeric columns and `OneHotEncoder` to `season`, wrapped with `LogisticRegression` in a `Pipeline`. Fit on the training data (features include `season` here) and print test accuracy. Reference accuracy is **0.875**. The comment must state that the pipeline automatically **applies the correct preprocessing to the right columns and fits it on the training data only**, so the student does not have to scale, encode, and align columns by hand or track which transformer was fit on which data.

Reference:
```python
numeric = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]
preprocess = ColumnTransformer([
    ("num", StandardScaler(), numeric),
    ("cat", OneHotEncoder(), ["season"]),
])
pipe = Pipeline([("pre", preprocess), ("clf", LogisticRegression(max_iter=1000))])
```
Key check: numeric and categorical columns are routed to different transformers inside one `ColumnTransformer`, and the whole thing is one `Pipeline`.

## KNN

### KNN Q1 — **Objective**
A `Pipeline` of `StandardScaler` and `KNeighborsClassifier(n_neighbors=5)`, fit on the training data. Reference test accuracy is **0.958**. The classification report shows both classes near 0.96 f1-score (skip: precision ~1.00, recall ~0.92; good: precision ~0.92, recall ~1.00).

### KNN Q2 — **Objective + Subjective**
Loop over `k` in `[1, 3, 5, 7, 9, 11, 15, 21]`, computing the mean 5-fold cross-validation accuracy on the **training** data for each. Reference mean CV scores:

- k=1: 0.925
- k=3: 0.921
- k=5: 0.929
- k=7: 0.940
- k=9: 0.935
- k=11: 0.942
- k=15: 0.938
- k=21: 0.931

The comment must name a chosen `k` with a reason. **k=11** has the highest reference CV score and is the model answer, but any mid-range value (7 to 15) is defensible because the scores are close. A good answer avoids k=1 (too sensitive to noise) and the largest values (drift toward underfitting).

### KNN Q3 — **Objective + Subjective**
Fit KNN once without scaling on raw `X_train` and once with scaling, both `n_neighbors=5`. Reference accuracies: **unscaled 0.925, scaled 0.958**. The comment must state that scaling **helped**, and that scaling matters for a distance-based model because KNN measures distance across all features. Without scaling, the large-range features dominate the distance and the small-range feature `precipitation_sum` barely counts, even though rain is exactly what makes a day one to skip. Scaling lets every feature contribute fairly.

## Logistic Regression

### Logistic Regression Q1 — **Objective**
A `Pipeline` of `StandardScaler` and `LogisticRegression(max_iter=1000)`. Reference values for the "good" class: **accuracy 0.867, precision 0.857, recall 0.885, F1 0.871**.

### Logistic Regression Q2 — **Objective + Subjective**
Print each feature name with its coefficient from `pipeline.named_steps["..."].coef_[0]`. Reference coefficients (on the scaled features):

- `temperature_2m_max`: -0.12
- `temperature_2m_min`: +0.26
- `precipitation_sum`: -1.89
- `wind_speed_10m_max`: -2.44

The comment must identify that **precipitation and wind speed push most strongly toward "skip"** (they have the large negative coefficients). A good answer notes this matches intuition: rain and high wind are the usual reasons to skip a run, while the two temperature coefficients are small because most days already sit in a comfortable temperature range, so temperature rarely decides the outcome.

### Logistic Regression Q3 — **Objective + Subjective**
Use `predict_proba(X_test)[:, 1]` to print the probability of "good" for the first five test days, rounded to two decimals. Reference values: **0.04, 0.47, 0.25, 0.96, 0.61**. The comment must state that a probability near 0.5 means the model is **uncertain / not confident** for that day: the day sits close to the decision boundary, and a small change in the inputs could flip the prediction.

## Evaluation

### Evaluation Q1 — **Objective (elements) + Subjective**
Build a confusion matrix for the logistic regression pipeline on the test set and display it with `ConfusionMatrixDisplay(display_labels=["skip", "good"])`, saving the figure to `outputs/logreg_confusion_matrix.png`. Reference confusion matrix:

```
[[50  9]
 [ 7 54]]
```

With `display_labels=["skip", "good"]`, the off-diagonal cells are **9 false positives** (bad days labeled good) and **7 false negatives** (good days labeled skip). The comment must report counts consistent with the student's own matrix and take a position on which error matters more for a running app. Either position is acceptable if justified: a false positive sends the runner out into bad weather (favor precision on "good"), while a false negative makes them miss a good day (favor recall on "good"). Most students argue the false positive is worse.

Key check: the display labels are in the order `["skip", "good"]`, matching label 0 = skip, 1 = good.

## joblib

### joblib Q1 — **Objective + Subjective**
Save the fitted logistic regression pipeline to `models/warmup_model.pkl` with `joblib.dump`, reload it with `joblib.load`, and assert the predictions match. The assertion must pass and print the confirmation line.

```python
joblib.dump(pipeline, "models/warmup_model.pkl")
loaded = joblib.load("models/warmup_model.pkl")
assert (loaded.predict(X_test) == pipeline.predict(X_test)).all()
print("Predictions match.")
```

The comment must state that saving only the `LogisticRegression` step without the scaler would produce **silently wrong predictions on raw data**. The classifier learned its coefficients on scaled inputs, so calling `.predict()` on unscaled data feeds it numbers on the wrong scale. There is no error, just wrong answers, because the scaler's learned mean and standard deviation are gone. Saving the whole pipeline keeps the scaler with the model.

---

# Part 2: Mini-Project — Build and Deploy a Weather Classifier

**Overall check:** the student fetches real weather for a city of their choice, engineers the `good_for_running` label, builds and compares a KNN and a Logistic Regression classifier, chooses one, saves it with `joblib`, writes a metadata file, and then loads and predicts in a separate script with no training code. Numbers vary by city and year. Grade the workflow and the reasoning.

## File 1: `train_classifier.py`

### Task 1: Fetch the Data — **Objective (approach) + Subjective**
Daily weather is fetched from the Open-Meteo archive API for one year and one city, using the four daily variables `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, and `wind_speed_10m_max`. The shape and first few rows are printed, and a comment names the city. The latitude, longitude, and dates are examples to adapt, so any valid city and year is fine.

Note the assignment typo: the correct wind variable is `wind_speed_10m_max`, not `wind_speed_10m_max_10m_max`. A student who used the correct name is right. Key check: the request uses `raise_for_status()` or otherwise handles a failed request, and the resulting DataFrame has the four feature columns plus a date.

### Task 2: Engineer the Label — **Objective + Subjective**
A `good_for_running` column is created: 1 when the high is between 7 and 26 degrees, the low is at least 0, precipitation is under 3 mm, and maximum wind is under 30 km/h; 0 otherwise. Students may adjust thresholds for their climate if they document the change in a comment. The class balance is printed. The comment must state the fraction of good days and whether it seems reasonable for the city's climate. If the data is very imbalanced, the comment should note that precision, recall, and F1 matter more than accuracy, because accuracy can look high while the model fails on the rare class.

Reference label logic:
```python
df["good_for_running"] = (
    (df["temperature_2m_max"].between(7, 26))
    & (df["temperature_2m_min"] >= 0)
    & (df["precipitation_sum"] < 3)
    & (df["wind_speed_10m_max"] < 30)
).astype(int)
```

### Task 3: Build and Evaluate a KNN Classifier — **Objective (approach) + Subjective**
An 80/20 split with `random_state=42` and `stratify` on the label. A `Pipeline` of `StandardScaler` and `KNeighborsClassifier`. `k` is chosen by 5-fold cross-validation over at least five values on the training data. The chosen model is fit, and its test accuracy and full classification report are printed. Key check: `k` is selected using cross-validation on the training set, not by peeking at the test set, and the pipeline includes the scaler.

### Task 4: Build and Evaluate a Logistic Regression Classifier — **Objective (approach) + Subjective**
A `Pipeline` of `StandardScaler` and `LogisticRegression(max_iter=1000)`. Test accuracy, precision, recall, F1, and the classification report are printed. Each feature's coefficient is printed and interpreted in a comment. The interpretation must identify which conditions push a day toward "skip" (typically high precipitation and high wind, which have negative coefficients). The exact coefficients depend on the student's city and data.

Reference for reading coefficients:
```python
logreg = pipeline.named_steps["logreg"]
for name, coef in zip(FEATURES, logreg.coef_[0]):
    print(f"{name:20s}: {coef:+.2f}")
```

### Task 5: Compare and Choose — **Objective + Subjective**
A written comment comparing the two classifiers. It must cover three points:

1. **Which model scored higher accuracy** on the student's data.
2. **The false-positive vs false-negative trade-off** for a running app. A false positive means the app sends the runner out on a bad day. A false negative means the app tells the runner to skip a good day. The comment should say which error the student weighs more heavily and connect it to precision or recall. Either position is defensible.
3. **A justified deployment choice.** The student may deploy either model. The comment must justify the choice using more than the accuracy score: model size, prediction speed, interpretability, and whether probability confidence scores are wanted.

**Mentor talking point — why the course deploys Logistic Regression even though KNN scores higher.** In the lessons, KNN reaches about 0.96 accuracy and Logistic Regression about 0.87 on the fixed dataset. KNN wins on accuracy because the "good for running" region is a box in feature space (mild temperature *and* low rain *and* low wind), and a single straight boundary cannot trace the corners of that box, so Logistic Regression makes more errors near the edges. The course still deploys Logistic Regression for operational reasons:

- It produces smooth probability confidence scores, which the Week 10 cloud pipeline uses.
- Its saved file is tiny, because it stores a handful of coefficients. KNN must ship its entire training set and search through it for every prediction.
- Its coefficients are interpretable, so its decisions can be explained.

When two models are close enough, these practical differences decide which one ships. A student who deploys KNN is not wrong, but they should acknowledge these costs. A student who deploys Logistic Regression should name at least one of these operational advantages, not just say "it is simpler."

### Task 6: Save the Model — **Objective**
The chosen fitted pipeline is saved to `models/weather_classifier.pkl` with `joblib.dump`. A metadata file is saved to `models/weather_classifier_metadata.json` containing at least: the Python version, the scikit-learn version, the feature names in order, the label rule, the city, and the test accuracy and F1 of the saved model. A confirmation message is printed when both files are written.

Reference:
```python
joblib.dump(model, "models/weather_classifier.pkl")
metadata = {
    "python_version": sys.version,
    "sklearn_version": sklearn.__version__,
    "features": FEATURES,
    "label": "good_for_running",
    "label_rule": "...",
    "city": "...",
    "test_accuracy": round(acc, 3),
    "test_f1": round(f1, 3),
}
with open("models/weather_classifier_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
```
Key check: the saved object is the full `Pipeline` (scaler plus classifier), not a bare classifier, and the metadata feature order matches the columns the pipeline was trained on.

## File 2: `predict.py`

### Task 7: Load and Predict — **Objective (approach) + Subjective**
The script loads the pipeline from the `.pkl` and the metadata from the JSON, and contains **no training code**: no `fit`, no cross-validation, no API fetch. It prints key metadata (city, features, test accuracy). It builds a small DataFrame of at least four hypothetical days, including a clearly good day, a clearly bad day, and at least one borderline day, using the feature names from the metadata so the columns match. For each day it prints the four inputs, the predicted label (good or skip), and the confidence (the probability of "good" from `predict_proba`).

Key check: columns are built from `metadata["features"]` so column order matches the trained pipeline, and there is genuinely no training code in this file.

### Task 8: Reflect — **Subjective**
A comment block answering three questions:

1. **The borderline day's probability and how to handle 0.52.** A good answer states the probability, calls the model uncertain when it is near 0.5, and proposes a sensible way to handle a 0.52 day, such as treating it as "unsure" rather than a firm yes, checking a second source, or widening the threshold for a confident call.
2. **What breaks if `predict.py` runs before training, and how to improve the error.** The correct answer is that `joblib.load` (or opening the JSON) raises a `FileNotFoundError` because `models/weather_classifier.pkl` does not exist yet. A good improvement is to catch that error and print a clear message telling the user to run `train_classifier.py` first.
3. **One change needed for the Week 10 cloud pipeline.** Any reasonable answer is fine: reading new days from a database or API instead of a hardcoded DataFrame, writing predictions back to storage, wrapping the load-and-predict logic in a function or class, loading the model once instead of on every call, adding logging, or handling inputs far outside the training range.

---

# Optional Extensions

**Do not fail a student for omitting any of these.** They are marked "(Optional)".

- **Extension A (Optional)** — `season` is derived from the month and added via a `ColumnTransformer` that scales the numeric features and one-hot encodes `season` inside the pipeline, with a comment on whether it changed the scores. On the fixed dataset, adding season changes the score very little.
- **Extension B (Optional)** — the classifier is trained on one city and evaluated on a second city with a different climate, with a comment explaining why accuracy usually drops: a model learns the label boundary for the training city's climate, and a different climate shifts the distribution of temperature, rain, and wind.
- **Extension C (Optional)** — cross-validation compares several `C` values (for example 0.01, 0.1, 1.0, 10.0, 100.0), with a comment on whether the best `C` improved F1 over the default. On this well-behaved data the improvement is usually small.

---

# Running and Verifying

To verify a submission:

1. `warmup_03.py` runs top to bottom with `weather_classification.csv` in the same folder, prints the outputs described above, and saves `outputs/logreg_confusion_matrix.png` and `models/warmup_model.pkl`. The warmup numbers should match the reference values in this key because the setup block fixes `random_state=42`.
2. `train_classifier.py` fetches live data, prints the class balance and both models' scores, and writes `models/weather_classifier.pkl` and `models/weather_classifier_metadata.json`.
3. `predict.py` runs on its own, after training, with no network access and no training code, and prints predictions and confidences for the hypothetical days.

If the student's warmup numbers differ from the reference values, the most common cause is a changed `random_state`, a scaler fit on the wrong set, or a `k` chosen without cross-validation. The mini-project numbers are expected to differ by city and year, so grade its workflow and reasoning rather than its exact metrics.
