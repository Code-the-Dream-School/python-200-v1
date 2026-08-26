# ROC Curves and AUC

## The Threshold Problem

Every classifier you have built so far does the same thing at the end: it outputs a probability, then compares that probability to 0.5. If the probability is above 0.5, it predicts the positive class. Below 0.5, negative.

This feels natural, but 0.5 is an arbitrary choice. It is not something the model learned — it is something *we* imposed after the fact. And depending on what kinds of errors matter most in your application, a different threshold might serve you much better.

Consider a concrete example. Suppose you are building a classifier that looks at daily weather data and predicts whether tomorrow is a good day for an outdoor run — a binary problem where "1" means good conditions and "0" means skip it. Your classifier outputs probabilities like 0.43, 0.71, 0.58, and so on. At a threshold of 0.5:

- A day with probability 0.48 gets labeled "bad" — even though the model thinks it is almost a coin flip.
- A day with probability 0.51 gets labeled "good" — for almost the same reason.

Is that really what you want? If you are more worried about recommending a run on a genuinely bad day (false positive) than about being overly cautious (false negative), you might want a higher threshold — say, 0.65. The model would only call a day "good" when it is quite confident. You would get fewer false positives, at the cost of missing some genuinely good days.

There is no single right threshold. The right choice depends on the costs and consequences of each error type in your specific situation. But this creates a problem: how do you compare two models if each one's "best" threshold might be different?

The ROC curve was designed to solve exactly this problem.

## Building Intuition: TPR and FPR

Before we look at the curve itself, we need two rates that describe a classifier's behavior at any given threshold.

**True Positive Rate (TPR)**, also called *recall* or *sensitivity*: of all the days that were truly good for running, what fraction did the model correctly identify?

```
TPR = TP / (TP + FN)
```

**False Positive Rate (FPR)**: of all the days that were truly bad for running, what fraction did the model incorrectly label as good?

```
FPR = FP / (FP + TN)
```

You already know TPR from the week 3 evaluation lesson — it is recall. FPR is the mirror image: it tells you how often the classifier raises a false alarm.

At a very low threshold (say, 0.1), the model calls almost everything "good." TPR will be very high — it catches nearly all the real good days. But FPR will also be very high — it misidentifies most bad days as good. Slide the threshold up toward 1.0 and the pattern reverses: TPR falls (the model becomes choosy, and misses real good days) while FPR also falls (fewer false alarms). Every threshold value produces one (FPR, TPR) pair.

The ROC curve plots those pairs across every possible threshold.

## The ROC Curve

The ROC curve (Receiver Operating Characteristic) plots FPR on the x-axis and TPR on the y-axis, sweeping the threshold from 0 to 1. Each point on the curve is one threshold. The curve as a whole tells you about the classifier's behavior at every operating point — not just the one you happen to have chosen.

Two reference points anchor the curve:

- **Bottom-left (0, 0)**: the threshold is 1.0. The model predicts negative for everything. TPR = 0 (misses all good days). FPR = 0 (no false alarms, because no positives at all).
- **Top-right (1, 1)**: the threshold is 0.0. The model predicts positive for everything. TPR = 1 (catches all good days). FPR = 1 (also flags every bad day).

A random classifier — one whose predictions are no better than a coin flip — would produce a diagonal line from (0,0) to (1,1). Every classifier you actually want to use should curve above that diagonal. The further it bows toward the top-left corner (TPR = 1, FPR = 0), the better it discriminates between the two classes.

Let's build the weather classifier and plot its ROC curve. First, the data:

```python
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, roc_auc_score, RocCurveDisplay

# Fetch one year of daily weather data — Charlotte, NC
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
        "wind_speed_10m_max",
    ],
    "timezone": "America/New_York",
}
response = requests.get(url, params=params)
response.raise_for_status()
data = response.json()

df = pd.DataFrame(data["daily"])
df["date"] = pd.to_datetime(df["time"])
df = df.drop("time", axis=1)
print(df.head())
print(f"\n{len(df)} days loaded")
```

The dataset has four numeric features for each day: the maximum temperature, the minimum temperature, total precipitation, and maximum wind speed. All values use metric units: temperature in °C, precipitation in mm, wind speed in km/h.

### Engineering Labels

The dataset contains no labels — we need to create them. This is called *label engineering* or *rule-based labeling*, and it is a real technique used in industry when ground-truth labels are unavailable or expensive. We define "good for running" using domain knowledge:

```python
def label_running_day(row):
    """Return 1 if conditions are good for an outdoor run, 0 otherwise."""
    temp_ok    = 7 <= row["temperature_2m_max"] <= 26   # 45–79°F
    above_freeze = row["temperature_2m_min"] >= 0        # above freezing at dawn
    dry        = row["precipitation_sum"] < 3.0          # light rain or less
    not_windy  = row["wind_speed_10m_max"] < 30          # under 30 km/h
    return int(temp_ok and above_freeze and dry and not_windy)

df["good_for_running"] = df.apply(label_running_day, axis=1)

print(df["good_for_running"].value_counts())
print(f"\nFraction of good days: {df['good_for_running'].mean():.2f}")
```

These thresholds are a deliberate design choice, not ground truth. In a real project, you might validate them against survey data ("did runners actually go out on those days?") or adjust them based on feedback. For this course, they give us a clean, interpretable label that is directly tied to the numeric features — which is what we want for a classifier tutorial.

### Training a Classifier

```python
FEATURES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "wind_speed_10m_max",
]

X = df[FEATURES]
y = df["good_for_running"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

clf = LogisticRegression(max_iter=1000, random_state=42)
clf.fit(X_train_scaled, y_train)
```

### Plotting the ROC Curve

`roc_curve` takes the true labels and the predicted *probabilities* (not hard predictions) and returns the FPR and TPR values at each threshold:

```python
y_probs = clf.predict_proba(X_test_scaled)[:, 1]  # probability of "good for running"

fpr, tpr, thresholds = roc_curve(y_test, y_probs)

fig, ax = plt.subplots(figsize=(6, 5))
RocCurveDisplay(fpr=fpr, tpr=tpr).plot(ax=ax, name="Logistic Regression")
ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Random classifier")
ax.set_title("ROC Curve — Weather Classifier")
ax.legend()
plt.tight_layout()
plt.savefig("outputs/weather_roc.png")
plt.show()
```

The curve should bow noticeably toward the top-left corner, confirming that the classifier is significantly better than random.

## AUC: A Single Summary Number

The curve is useful for visualizing the full tradeoff, but comparing two curves visually is subjective. AUC (Area Under the Curve) solves this by reducing the entire curve to one number: the area under the ROC curve, which ranges from 0.5 (random classifier) to 1.0 (perfect classifier).

Practically, AUC has a clean interpretation: it equals the probability that the classifier will assign a higher score to a randomly chosen positive example than to a randomly chosen negative one. A model with AUC 0.90 will correctly rank 90% of such pairs.

```python
auc = roc_auc_score(y_test, y_probs)
print(f"AUC: {auc:.3f}")
```

For the weather classifier, you should see an AUC somewhere in the range of 0.92–0.97 — the logistic regression finds the pattern easily because the label definition is directly tied to the numeric features.

## Choosing a Threshold

Once you have a trained model and its ROC curve, you can choose a threshold based on your requirements rather than defaulting to 0.5. The `thresholds` array returned by `roc_curve` aligns with the `fpr` and `tpr` arrays, so you can inspect the operating points:

```python
# Build a table of threshold choices
threshold_df = pd.DataFrame({
    "threshold": thresholds,
    "fpr":       fpr,
    "tpr":       tpr,
}).round(3)

# Find the threshold closest to a target TPR of 0.90
target_tpr = 0.90
idx = np.argmin(np.abs(threshold_df["tpr"] - target_tpr))
print(threshold_df.iloc[idx])
```

This is the kind of analysis you would actually do in production: "we need to catch at least 90% of good running days — what threshold achieves that, and what false-positive rate does it imply?"

## Comparing Two Models

AUC is most valuable when comparing models. Because it is threshold-independent, a higher AUC reliably indicates a better-discriminating model — regardless of where each model's default threshold happens to fall.

```python
from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_scaled, y_train)
knn_probs = knn.predict_proba(X_test_scaled)[:, 1]
knn_auc = roc_auc_score(y_test, knn_probs)

print(f"Logistic Regression AUC: {auc:.3f}")
print(f"KNN (k=5) AUC:           {knn_auc:.3f}")

# Overlay both curves
fig, ax = plt.subplots(figsize=(6, 5))
RocCurveDisplay(fpr=fpr, tpr=tpr).plot(ax=ax, name=f"Logistic Regression (AUC={auc:.2f})")
knn_fpr, knn_tpr, _ = roc_curve(y_test, knn_probs)
RocCurveDisplay(fpr=knn_fpr, tpr=knn_tpr).plot(ax=ax, name=f"KNN k=5 (AUC={knn_auc:.2f})")
ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Random")
ax.set_title("ROC Comparison — Weather Classifier")
ax.legend()
plt.tight_layout()
plt.savefig("outputs/weather_roc_comparison.png")
plt.show()
```

## When to Use AUC vs. F1

AUC and F1 answer different questions:

- **AUC** measures *discrimination ability* — how well the classifier separates positives from negatives across all thresholds. It is the right metric when you do not yet know what threshold you will use in production, or when you want a threshold-independent comparison between models.

- **F1** measures *performance at a specific threshold* — how good the model's actual predictions are when it uses a fixed cutoff. It is the right metric when you have already committed to a threshold and want to know how the classifier performs at that operating point.

In practice, use AUC during model selection and development. Once you have chosen a model and a threshold, evaluate with precision, recall, and F1 at that operating point.

## Check for Understanding

1. A classifier has AUC = 0.5. What does this tell you about its predictions?

    - A. It is a perfect classifier
    - B. Its predictions are no better than random
    - C. It always predicts the positive class
    - D. It has high recall but low precision

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. AUC = 0.5 means the classifier performs at chance — the ROC curve lies along the diagonal.
    </details>

2. You need a classifier that catches at least 95% of "good for running" days, even if that means some false alarms. Which metric should you optimize when selecting the threshold?

    - A. AUC
    - B. Precision
    - C. Accuracy
    - D. True Positive Rate (recall)

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: D. You want high TPR/recall, meaning the model rarely misses a true positive. Setting a lower threshold increases recall at the cost of more false positives.
    </details>

3. Two classifiers both achieve 85% accuracy. Classifier A has AUC 0.91, Classifier B has AUC 0.74. What can you conclude?

    - A. Classifier B is better because accuracy is higher
    - B. Classifier A is better at separating positives from negatives across all thresholds
    - C. Both classifiers are equally good
    - D. Neither classifier is reliable

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. AUC measures discrimination ability independent of threshold. Classifier A is significantly better at ranking positive examples above negative ones, even though both achieve the same accuracy at their default threshold.
    </details>

## Lesson Wrap-Up

The ROC curve reveals how a classifier behaves across every possible decision threshold, not just the default 0.5. AUC summarizes that behavior in a single number — the probability that the model ranks a positive example above a negative one — and is the standard metric for model comparison when you have not yet committed to a threshold. Together, they give you a much clearer picture of model quality than accuracy alone.

In the next lesson, you will use these tools to evaluate models during hyperparameter tuning — searching systematically for the best classifier configuration using cross-validation.
