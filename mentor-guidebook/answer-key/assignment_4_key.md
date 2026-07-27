# Assignment 4 Answer Key: Applied ML

**Mentor note:** This key covers Week 4 warmups (ROC/AUC, GridSearchCV, joblib) and the weather-classifier mini-project (train + predict scripts). The warmups use a fixed synthetic dataset (`make_classification`, `random_state=42`), so their numbers are reproducible and given below. The mini-project pulls live data from the Open-Meteo API for a student-chosen city, so numbers vary widely — grade the workflow and reasoning, not specific values. This project's model gets reused in a later week, so the two-file train/predict split and the saved `.pkl` + metadata are the important deliverables.

---

## Expected File Setup

Assignment lives in `assignments_04/`:

```
assignments_04/
├── warmup_04.py                 # all warmup exercises
├── train_weather_classifier.py  # trains + saves the model
├── predict_weather.py           # loads model, predicts (NO training code)
├── models/                      # weather_classifier.pkl + metadata.json + warmup_model.pkl
└── outputs/                     # plots
```

Submitted as a PR link. The setup block creates `outputs/` and `models/` and builds the synthetic dataset once at the top of `warmup_04.py`.

---

# Part 1: Warmup Exercises (`warmup_04.py`)

## ROC and AUC

### ROC Q1 — **Objective + Subjective**
`LogisticRegression(max_iter=1000, random_state=42)` on raw train; `KNeighborsClassifier(n_neighbors=5)` on scaled train. Uses `.predict_proba(...)[:, 1]` for AUC via `roc_auc_score`. Both AUCs are high (~0.93–0.96); **logistic regression is typically slightly higher**. Comment: higher AUC = better at separating the two classes across *all* thresholds, independent of any single cutoff.
- Common error: passing `.predict()` labels instead of `.predict_proba()[:, 1]` probabilities to `roc_auc_score`.

### ROC Q2 — **Objective (elements) + Subjective**
Both ROC curves on one axes, each labeled with model name + AUC, random-classifier diagonal drawn, saved to `outputs/roc_comparison.png`. Comment: at TPR=0.80, whichever curve sits higher/left has the lower FPR (usually LR) — meaning to catch 80% of positives, that model produces fewer false alarms.

### ROC Q3 — **Objective + Subjective**
Loops thresholds from `roc_curve`, computes F1 at each via `y_pred = (y_probs_lr >= threshold).astype(int)`, prints threshold/TPR/FPR/F1 at the max-F1 point. Optimal threshold is usually **near but not exactly 0.5** (often ~0.4–0.6). Comment: you'd choose a threshold **below 0.5** when catching positives matters more than avoiding false alarms (e.g. disease screening, fraud) — lowering the threshold raises recall.

## GridSearchCV

### GridSearch Q1 — **Objective + Subjective**
`Pipeline([StandardScaler, LogisticRegression(max_iter=1000)])`, `GridSearchCV(cv=5, scoring="roc_auc")` over C `[0.001, 0.01, 0.1, 1.0, 10.0, 100.0]`. Prints best C, best CV AUC, test AUC. Best C is often **0.1 or 1.0**; test AUC ~0.95. Comment: whether it matches the default C=1.0 and that the test-AUC change is usually **small** (the model isn't very sensitive to C here).

### GridSearch Q2 — **Objective + Subjective**
Same pipeline with `DecisionTreeClassifier(random_state=42)`, search `max_depth` `[2, 3, 5, 8, None]`. Prints best depth, best CV AUC, test AUC. Best depth is usually **moderate (3–5)**; tree AUC (~0.88–0.92) is **lower than logistic regression's**. Comment: should pick LR to develop further and note AUC isn't the only consideration (interpretability, speed, calibration, etc.).

### GridSearch Q3 — **Objective (approach) + Subjective**
Reads `cv_results_`, prints mean and std of CV AUC per parameter value, sorted best to worst. Comment: identifies two params with similar means but different stds and picks the **lower-std (more stable)** one, with reasoning — consistency across folds means more reliable generalization.

## joblib

### joblib Q1 — **Objective + Subjective**
`joblib.dump` the best LR pipeline to `models/warmup_model.pkl`, reload with `joblib.load`, assert predictions match, print success. The provided assert should pass. Comment: if you saved only the LR model **without the scaler** and predicted on unscaled `X_test`, predictions would be **wrong/garbage** — the model expects scaled inputs, so the missing preprocessing step breaks it. (This is the key argument for saving the whole pipeline.)

### joblib Q2 — **Objective + Subjective**
Loads the model fresh, predicts on the three hand-crafted rows, prints predicted class + probability for each. Comment on the all-zeros row: it sits at roughly the "average" of the standardized feature space, so its prediction is near the decision boundary / uncertain — a reasonable answer explains the *reasoning* (predicting near 0.5, or whichever class the boundary favors) rather than a specific label.

---

# Part 2: Mini-Project — Weather Classifier

**Overall check:** clean separation between `train_weather_classifier.py` (all training, saves model + metadata) and `predict_weather.py` (loads and predicts, **no training code**). The saved `.pkl` and metadata JSON are the deliverables that get reused later. City choice and thresholds are the student's — grade the workflow.

## File 1: `train_weather_classifier.py`

### Step 1: Fetch Data — **Objective (approach)**
- Calls the Open-Meteo archive API for one year of daily data with the four required variables, builds a DataFrame, parses the date. `response.raise_for_status()` present is a plus.
- Prints a dataset summary. City can be anything; lat/long are the only changes from the example.

### Step 2: Engineer Labels — **Objective (approach) + Subjective**
- Builds a binary "good for running" label from the four features (starter thresholds given, adjustments allowed if documented in comments).
- Prints class distribution and comments on the fraction of good days — should be a **sensible fraction (not ~0% or ~100%)** and consistent with the chosen city's climate. A label that produces almost no positives (or all positives) suggests thresholds need adjusting.
- Correct label logic uses **AND** across conditions (all must be satisfied), e.g. temp in range AND low precip AND low wind.

### Step 3: Train and Tune — **Objective (approach)**
- 80/20 split, `stratify` on label.
- `GridSearchCV` over a `Pipeline(StandardScaler, LogisticRegression)`, ≥5 C values, `cv=5`, `scoring="roc_auc"`.
- Prints best C, best CV AUC, full test classification report, test AUC.
- ROC curve for best estimator saved to `outputs/weather_roc.png`. AUC is usually high (~0.9+) because labels are a deterministic function of the features — the model is essentially rediscovering the thresholds.

### Step 4: Reflect on Evaluation — **Subjective**
4–6 sentence comment block. Good answers:
- Interpret the AUC honestly — often note it's **high because labels are rule-derived from the same features** (so near-perfect separation is expected, not impressive).
- Identify which error (FP vs FN) is more common from the report and connect it to the app: over-recommending running (FP) vs under-recommending (FN), and which is worse for a user.
- Take a position on threshold: keep 0.5 or adjust, with a reason tied to the app's goal.

### Step 5: Save the Model — **Objective (contents)**
- `joblib.dump` best pipeline to `models/weather_classifier.pkl`.
- Metadata JSON at `models/weather_classifier_metadata.json` containing **all** of: Python version, scikit-learn version, ordered feature names, best hyperparameters, test AUC, city lat/long, and a description of the label thresholds.
- Prints confirmation. Missing metadata fields are the most common gap here — check all seven are present.

## File 2: `predict_weather.py`

### Task 1: Load and Verify — **Objective (approach)**
Loads the pipeline and metadata; prints key metadata (city, features, test AUC). **No training/fitting/API code** — if `fit`, `GridSearchCV`, or API calls appear here, that's a miss.

### Task 2: Predict on New Data — **Objective (approach)**
- DataFrame of ≥5 hypothetical days spanning clearly good, clearly bad, and ≥1 borderline case.
- Uses the **feature names from metadata** so columns match the training order exactly.
- For each day prints the four inputs, predicted label (good/skip), and probability of "good."
- Predictions should be sane: an ideal mild/dry/calm day → good with high confidence; a freezing/stormy day → skip with high confidence.

### Task 3: Reflect — **Subjective**
Comment block answering three questions:
1. Borderline case — reports its probability and describes it as uncertain if near 0.5; a reasonable strategy for a 0.52 day (e.g. show "maybe," defer to user, widen with more data).
2. What breaks if `predict_weather.py` runs first: the `.pkl`/metadata don't exist → `FileNotFoundError`. Good answers suggest a clearer message (e.g. "model not found — run train_weather_classifier.py first").
3. Production daily-forecast use: would swap hand-built rows for a **forecast API call** (forecast endpoint instead of archive), map the response to the same feature columns, and run daily (scheduling). Description only — no implementation required.

## Optional Extensions (A/B/C) — **Not required**
If attempted: Extension A compares two cities' class balance and AUC; B adds derived features (`temp_range`, month, lagged precip) and compares AUC, updating metadata; C expands to multiple years and comments on whether more data helped. Grade lightly — these are bonus and open-ended.
