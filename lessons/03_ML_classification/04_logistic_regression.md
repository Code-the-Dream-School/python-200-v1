# Logistic Regression

Logistic Regression sounds like something from a math textbook, but it is one of the most approachable and useful classifiers you will learn. Many data scientists and ML engineers start with it because it is simple, interpretable, and surprisingly effective. The goal of this lesson is to explain how it works and to build a second weather classifier with it, so you can compare it to KNN.

## What Problem Does Logistic Regression Solve?

Logistic Regression is a *binary classifier*. It sorts examples into one of two groups: yes or no, spam or not spam, good for running or not. What makes it special is that it does not just answer "yes" or "no." It produces a **probability**, which makes its predictions more informative and easier to act on.

## The Big Idea

At its heart, logistic regression asks: how strongly do the input features suggest that this example belongs to class 1 rather than class 0?

To answer, it starts exactly like linear regression. It multiplies each feature by a learned weight, adds the results together, and produces a single score:

```text
z = b0 + b1*x1 + b2*x2 + ...
```

If this were ordinary linear regression, the model would output that number directly. But a raw score like 4.3 or -2.8 does not tell us "good" or "skip," and it is not a probability. So logistic regression passes the score through one more transformation that turns any number into a probability between 0 and 1. That transformation is the *sigmoid function*.

## The Sigmoid Function

![Sigmoid graph](<resources/Sigmoid graph.png>)

The sigmoid is a smooth, S-shaped curve. Its behavior is simple:

- Large negative scores are squeezed toward 0.
- Large positive scores are pushed toward 1.
- Scores near zero land near 0.5.

The formula is: ![Formula](resources/Formula.png)

You do not need to memorize it. What matters is the behavior. If the weighted sum of features is very negative, the sigmoid returns a probability near 0. If it is very positive, the probability is near 1. A probability of 0.52 means "a near toss-up, leaning slightly toward class 1," while 0.97 means "almost certain." This is what makes logistic regression valuable: you get a measure of confidence, not just a hard label.

## From Probability to Decision

To make a final prediction, logistic regression compares the probability to a threshold, usually 0.5:

- probability greater than 0.5 means class 1 (good for running)
- probability less than 0.5 means class 0 (skip)

Because the score is a weighted sum of the features, the boundary where the probability equals 0.5 is a straight line in two dimensions, a flat plane in three, and a flat surface in higher dimensions. Adding features shifts and tilts that boundary, but it never bends it. This is the key difference from KNN. Where KNN decides locally by looking at nearby points, logistic regression draws **one straight boundary** across the whole feature space. That makes it easy to interpret: a positive weight means the feature pushes the prediction toward "good," a negative weight pushes it toward "skip," and the size of the weight tells you how much.

## Building the Model

We use the same weather data and the same pipeline structure as before, swapping the classifier. The scaler still matters, because logistic regression adjusts weights based on the numeric values of the features, and features on larger scales would otherwise dominate the learning.

```python
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv("resources/weather_classification.csv")
features = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]
X = df[features]
y = df["good_for_running"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = Pipeline([
    ("scaler", StandardScaler()),
    ("logreg", LogisticRegression(max_iter=1000)),
])
model.fit(X_train, y_train)
```

`max_iter=1000` gives the optimizer enough steps to settle on its weights. The learning itself happens inside `.fit()`: the model starts with arbitrary weights, checks how wrong its predictions are, and adjusts the weights to reduce that error, repeating until the weights stop changing much. The function it minimizes is called *cross-entropy loss*, which is the classification counterpart to the RMSE you used in regression. You will meet cross-entropy again in the AI lessons.

## Evaluating the Model

```python
y_pred = model.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=["skip", "good"]))
```

```text
[[50  9]
 [ 7 54]]
              precision    recall  f1-score   support

        skip       0.88      0.85      0.86        59
        good       0.86      0.89      0.87        61

    accuracy                           0.87       120
   macro avg       0.87      0.87      0.87       120
weighted avg       0.87      0.87      0.87       120
```

Accuracy is about 0.87, with precision and recall both near 0.87 as well. The confusion matrix shows 9 bad days labeled good (false positives) and 7 good days labeled skip (false negatives). A quick cross-validation confirms the result is not a lucky split:

```python
cv = cross_val_score(model, X_train, y_train, cv=5)
print(f"CV mean: {cv.mean():.3f}   std: {cv.std():.3f}")
```

The fold scores cluster around 0.88 with a small standard deviation, consistent with the test result.

## Interpreting the Coefficients

This is where logistic regression earns its reputation. Because it learns one weight per feature, you can read those weights to see *what the model learned*.

```python
logreg = model.named_steps["logreg"]
for name, coef in zip(features, logreg.coef_[0]):
    print(f"{name:20s}: {coef:+.2f}")
```

```text
temperature_2m_max  : -0.12
temperature_2m_min  : +0.26
precipitation_sum   : -1.89
wind_speed_10m_max  : -2.44
```

The coefficients apply to the *scaled* features, so they are directly comparable to each other. Two things stand out. First, precipitation and wind speed have large negative coefficients, which means more rain and more wind both push a day strongly toward "skip." Second, the two temperature coefficients are small. That is not because temperature does not matter, but because most days in this data already sit in the comfortable temperature range, so temperature rarely decides the outcome. Rain and wind are the usual deal-breakers, and the model discovered that on its own. This kind of readable explanation is one of logistic regression's greatest strengths.

## Getting Probabilities

Unlike KNN's simple vote, logistic regression gives a smooth probability for every prediction:

```python
probabilities = model.predict_proba(X_test)[:, 1]   # probability of "good"
print(probabilities[:5].round(3))
```

`predict_proba` returns two columns, one per class. Column 1 is the probability of "good." These probabilities are useful confidence scores. A prediction of 0.97 is a confident "good," while 0.52 is barely leaning that way. In Week 10 you will carry these confidence scores through a cloud pipeline.

## When to Use Logistic Regression

Logistic Regression works well when the relationship between the features and the outcome is roughly linear, when you want a model that is fast to train and cheap to run, and when you want to explain *why* the model made a decision. Its main limitation is the flip side of its strength: because it can only draw a straight boundary, it struggles when the two classes are separated by a curved or irregular region, unless you add engineered features to help.

### A note on regularization

You may see logistic regression written with a `C` parameter, as in `LogisticRegression(C=1.0)`. `C` controls *regularization*, which discourages the model from assigning very large weights to any single feature. Large weights make a model over-reliant on one signal and sensitive to noise. Regularization keeps the weights contained and the model more stable. The direction of `C` is counterintuitive: a small `C` applies strong regularization, and a large `C` applies almost none. The default of `C=1.0` is a reasonable starting point. `C` is a *hyperparameter*, meaning a setting you choose rather than a weight the model learns, much like `k` in KNN.

## KNN or Logistic Regression?

You now have two classifiers for the same problem. On this data:

- **KNN** reached about 0.96 accuracy.
- **Logistic Regression** reached about 0.87 accuracy.

KNN did better here, and the reason is instructive. The "good for running" region is a box in feature space: a day is good when the temperature is in range *and* rain is low *and* wind is low. That box has corners, and a single straight boundary cannot trace them, so logistic regression makes more mistakes near the edges. KNN, deciding locally, follows the box more closely.

So why would anyone deploy logistic regression here? Because accuracy is not the only thing that matters when a model has to run in production, which is the subject of the next lesson. Logistic regression produces the smooth probabilities we want as confidence scores, its coefficients explain its decisions, and the saved model is tiny: it stores a handful of numbers rather than the entire training set. KNN, by contrast, must carry all of its training data into the deployment and search through it for every prediction. When two models are close enough, these practical differences often decide which one you ship. You will weigh exactly this trade-off in the deployment lesson and the assignment.

## Key Takeaways

Logistic regression turns a linear score into a probability with the sigmoid function, then thresholds that probability to make a binary decision. It draws one straight boundary between the classes, which makes it fast and interpretable but less able to capture irregular regions than KNN. Its coefficients tell you which features drive the decision, and here they revealed that rain and wind matter most. It produces probabilities you can use as confidence scores. On this dataset KNN scored higher, but logistic regression's interpretability, probabilities, and small size make it a strong candidate for deployment, which we turn to next.

## Check for Understanding

1. What does the sigmoid function do in logistic regression?

    a. It scales the features
    b. It converts the linear score into a probability between 0 and 1
    c. It selects the most important features
    d. It draws multiple decision boundaries

    <details>
    <summary>Show Answer</summary>
    b -- the sigmoid maps any real-valued score to a probability between 0 and 1, which is then thresholded to make a decision.
    </details>

2. On the weather data, precipitation and wind speed had large negative coefficients while the temperature coefficients were small. Why?

    a. Temperature was measured incorrectly
    b. Most days already sat in the comfortable temperature range, so rain and wind were the features that usually decided the outcome
    c. Logistic regression ignores temperature
    d. The features were not scaled

    <details>
    <summary>Show Answer</summary>
    b -- because temperature rarely fell outside the comfortable range in this data, it seldom decided the label, so the model leaned on rain and wind, which are the usual deal-breakers.
    </details>

3. Why did KNN outperform logistic regression on this dataset?

    a. KNN always outperforms logistic regression
    b. The "good" region is a box with corners, and logistic regression can only draw one straight boundary, while KNN follows the box locally
    c. Logistic regression was not trained long enough
    d. KNN used more features

    <details>
    <summary>Show Answer</summary>
    b -- the class boundary here is irregular. A single straight surface cannot trace it exactly, so logistic regression makes more errors near the edges, while KNN's local voting handles the shape better.
    </details>

4. Given that KNN scored higher, why might you still deploy logistic regression?

    a. It is the only model that can be saved
    b. It produces smooth probability confidence scores, its coefficients are interpretable, and the saved model is tiny, while KNN must ship and search its whole training set
    c. It is always more accurate in production
    d. It does not need scaling

    <details>
    <summary>Show Answer</summary>
    b -- accuracy is not the only consideration. Logistic regression's probabilities, interpretability, and small size are real advantages when a model has to run in a pipeline, which can outweigh a modest accuracy gap.
    </details>
