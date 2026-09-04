# k-Nearest Neighbors (KNN)

In this lesson you will build your first classifier, using the *k-Nearest Neighbors* (KNN) algorithm. KNN is one of the simplest classifiers, which makes it a good place to see the core ideas of classification, scaling, and evaluation in action before we move to more involved models.

- [IBM overview article](https://www.ibm.com/think/topics/knn)
- [IBM video (10 minutes)](https://www.youtube.com/watch?v=b6uHw7QW_n4)

## The Intuition Behind KNN

Suppose you want to know whether today is good for a run, and you have records of many past days, each already labeled "good" or "skip." A natural strategy is to find the past days that were most *similar* to today, and see how they were labeled.

![KNN proximity](resources/knn_proximity_image.png)
*Image credit: GeeksforGeeks*

That is exactly how KNN works. To classify a new day, it finds the `k` closest days in the training data, looks at their labels, and lets them vote. The majority label wins. You choose `k`, which can be as small as 1 or as large as 20 or more. There is no real training phase. KNN simply stores the training data and compares each new point to it.

For example, with `k = 5`, if the five most similar past days were labeled good, good, good, skip, good, then KNN predicts "good" by a vote of four to one.

## The Weather Dataset

We will use a dataset of 600 days. Each day has four numeric measurements and a label:

- `temperature_2m_max` -- daily high temperature in degrees Celsius
- `temperature_2m_min` -- daily low temperature in degrees Celsius
- `precipitation_sum` -- total precipitation in millimeters
- `wind_speed_10m_max` -- maximum wind speed in km/h
- `good_for_running` -- 1 if the day is good for a run, 0 if not

The label was defined the same way as the `RunningConditions` rule from Week 1: a day is good if it is mild (a high between 7 and 26 degrees), not freezing overnight, dry (little precipitation), and not too windy. About half the days are good, so the classes are well balanced.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)

df = pd.read_csv("resources/weather_classification.csv")

features = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]
X = df[features]
y = df["good_for_running"]

print(X.shape)
print(y.value_counts())
```

You will see 600 rows, four features, and roughly 305 good days to 295 skip days.

## Train / Test Split

We hold out 20 percent of the data as a test set, and we stratify on the label so that both sets keep the same balance of good and skip days.

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(X_train.shape, X_test.shape)
```

## Why Scaling Matters Here

KNN decides which days are "closest" by measuring distance across all four features at once. Look at the ranges of our features. Temperature runs from below zero to the mid-thirties, wind speed runs up to the mid-forties, and precipitation is usually a small number of millimeters. Precipitation has the smallest range, so in a raw distance calculation it barely counts, even though a rainy day is exactly the kind of day you want to skip.

As you saw in the preprocessing lesson, the fix is to standardize the features so they are on comparable scales. Let us measure the difference directly. First, KNN on the raw, unscaled features:

```python
knn_unscaled = KNeighborsClassifier(n_neighbors=5)
knn_unscaled.fit(X_train, y_train)
print("Unscaled accuracy:", accuracy_score(y_test, knn_unscaled.predict(X_test)))
```

Now KNN with scaling, built as a `Pipeline` so the scaler is fit on the training data only:

```python
knn_scaled = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5)),
])
knn_scaled.fit(X_train, y_train)
print("Scaled accuracy:  ", accuracy_score(y_test, knn_scaled.predict(X_test)))
```

```text
Unscaled accuracy: 0.925
Scaled accuracy:   0.958
```

Scaling raised accuracy from about 0.925 to about 0.958. That improvement comes almost entirely from letting precipitation and the other smaller-range features count fairly in the distance. This is the preprocessing lesson made concrete: for a distance-based model, scaling is not optional bookkeeping. It changes the predictions.

From here on we use the scaled pipeline.

## Reading the Results

The classification report gives the full picture for both classes:

```python
y_pred = knn_scaled.predict(X_test)
print(classification_report(y_test, y_pred, target_names=["skip", "good"]))
```

```text
              precision    recall  f1-score   support

        skip       1.00      0.92      0.96        59
        good       0.92      1.00      0.96        61

    accuracy                           0.96       120
   macro avg       0.96      0.96      0.96       120
weighted avg       0.96      0.96      0.96       120
```

The model does well on both classes. Recall for "good" is very high, meaning it catches nearly every good running day. Precision for "good" is a little lower, meaning it occasionally labels a bad day as good. These are the false positives and false negatives from the evaluation lesson, now attached to a real model.

## A More Reliable Estimate: Cross-Validation

Those numbers came from one particular train/test split. A different split might tell a slightly different story, especially with only 120 test days. Rather than trust a single split, we can use *cross-validation*.

Cross-validation divides the training data into several equal groups called *folds*, usually five. It trains on four folds and evaluates on the fifth, then repeats so that each fold is held out once, and averages the scores. Because every training example is used for evaluation at some point, the averaged score is more stable than any single split. The standard deviation across folds tells you how consistent the result is. The test set is never touched during this process.

```python
knn = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5)),
])
cv_scores = cross_val_score(knn, X_train, y_train, cv=5)
print(cv_scores)
print(f"Mean: {cv_scores.mean():.3f}")
print(f"Std:  {cv_scores.std():.3f}")
```

You will see five fold scores clustered around 0.93, with a low standard deviation. Building the model as a pipeline matters here: cross-validation refits the scaler on each fold's training portion, so there is no leakage across folds.

## Choosing k

The one setting you control in KNN is `k`, the number of neighbors that vote. It matters more than you might expect.

- A very small `k`, such as `k = 1`, decides based on a single nearest neighbor. One unusual or mislabeled day can flip the prediction. The model is sensitive to noise, which is a form of overfitting.
- A very large `k` averages over so many neighbors that local detail is lost, and the model drifts toward always predicting the more common class. This is underfitting.

We use cross-validation to compare values of `k` without touching the test set:

```python
for k in [1, 3, 5, 7, 9, 11, 15, 19, 25]:
    knn = Pipeline([
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(n_neighbors=k)),
    ])
    scores = cross_val_score(knn, X_train, y_train, cv=5)
    print(f"k={k:2d}:  mean={scores.mean():.3f}  std={scores.std():.3f}")
```

```text
k= 1:  mean=0.925  std=0.018
k= 3:  mean=0.921  std=0.028
k= 5:  mean=0.929  std=0.027
k= 7:  mean=0.940  std=0.026
k= 9:  mean=0.935  std=0.018
k=11:  mean=0.942  std=0.021
k=15:  mean=0.938  std=0.017
k=19:  mean=0.929  std=0.017
k=25:  mean=0.923  std=0.028
```

The best cross-validation score is around `k = 11`. The very small values do slightly worse, and the largest values start to fall off as the model underfits. Once you have chosen `k`, you fit on the full training set and evaluate on the test set exactly once:

```python
best_k = 11
final_model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=best_k)),
])
final_model.fit(X_train, y_train)
print("Final test accuracy:", accuracy_score(y_test, final_model.predict(X_test)))
```

The test-set score at the end is the number you report. It is uncontaminated because you used the test set only once, after all the choices were made.

## The Confusion Matrix

The confusion matrix shows exactly where the model is making mistakes:

```python
cm = confusion_matrix(y_test, final_model.predict(X_test))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["skip", "good"])
disp.plot(colorbar=False)
plt.title("KNN Confusion Matrix")
plt.show()
```

The diagonal cells are correct predictions. The off-diagonal cells tell you the pattern of errors: how many bad days were labeled good (false positives) and how many good days were labeled skip (false negatives). On this dataset the numbers are small, but reading the matrix is a habit worth keeping, because on messier problems the off-diagonal cells are where the interesting analysis lives.

## Key Takeaways

KNN classifies a new point by finding the `k` most similar training points and letting them vote. Because it works by distance, it is sensitive to feature scale, so scaling made a real difference here (accuracy rose from about 0.925 to about 0.958). Cross-validation gives a more reliable estimate than a single split and lets you choose `k` without touching the test set. KNN is transparent and effective, but it has trade-offs: it stores the entire training set and searches through it for every prediction, which makes it slower and heavier at prediction time than the model you will meet next.

## Check for Understanding

1. How does KNN classify a new data point?

    a. It fits a line through the training data
    b. It finds the k most similar training points and takes a majority vote of their labels
    c. It builds a tree of decision rules
    d. It averages the labels of all training points

    <details>
    <summary>Show Answer</summary>
    b -- KNN finds the k nearest neighbors in the training data and lets their labels vote on the prediction.
    </details>

2. Why did scaling improve KNN's accuracy on the weather data?

    a. Scaling adds more training data
    b. KNN measures distance, and without scaling the small-range features like precipitation barely counted; scaling lets every feature count fairly
    c. Scaling changes the labels
    d. KNN requires scaling to run at all

    <details>
    <summary>Show Answer</summary>
    b -- distance is dominated by large-range features unless the features are standardized. Scaling let precipitation and the other features contribute fairly, which changed the predictions.
    </details>

3. Why is cross-validation more reliable than a single train/test split for choosing k?

    a. It uses the test set more times
    b. It evaluates on several different held-out folds and averages the results, so the estimate does not depend on one lucky or unlucky split
    c. It removes the need to scale
    d. It guarantees higher accuracy

    <details>
    <summary>Show Answer</summary>
    b -- averaging over folds gives a more stable estimate, and the standard deviation shows how consistent the result is. The test set stays untouched.
    </details>

4. What is the risk of choosing k = 1?

    a. The model runs too slowly
    b. A single unusual or mislabeled neighbor can flip the prediction, so the model is sensitive to noise (overfitting)
    c. The model always predicts the majority class
    d. The model cannot be evaluated

    <details>
    <summary>Show Answer</summary>
    b -- with k = 1 the prediction depends entirely on the single closest point, which makes the model fragile to noise and outliers. Larger k values smooth this out, up to a point.
    </details>
