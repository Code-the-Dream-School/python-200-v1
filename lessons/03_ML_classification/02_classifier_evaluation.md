# Evaluating Classifiers

Before we build classifiers, we need to agree on how to judge them. How do you tell whether a classifier is any good, or whether one classifier is better than another? Accuracy alone is not enough, and this lesson explains why. We will use a familiar real-world classifier to introduce the ideas, and then connect them to the weather classifier you will build next.

If you prefer a video, this 10-minute walkthrough covers the confusion matrix, precision, recall, and F1 with simple examples: [Evaluating a classifier](https://www.youtube.com/watch?v=-ORE0pp9QNk).

## A Familiar Classifier: A Rapid Test

A rapid medical test is a real-life classifier. It takes an input (a sample), processes it, and outputs one of two categories: positive or negative. Like any classifier, it is sometimes right and sometimes wrong. Because the outcomes are easy to reason about, it is a good way to learn the metrics we will later apply to a machine learning model.

![A rapid test: image from Shutterstock](resources/covid_test.jpg)

Imagine 100 patients come to a clinic, and we know the truth about each one:

- 30 patients actually have the illness (they are truly positive).
- 70 patients do not (they are truly negative).

Each patient takes the rapid test. Suppose the test produces these results:

- Of the 30 who have the illness: 24 test positive (correct) and 6 test negative (missed).
- Of the 70 who do not: 10 test positive (false alarms) and 60 test negative (correct).

## The Confusion Matrix

We can organize those four numbers into a small table called a *confusion matrix*. The rows are the true condition, and the columns are the prediction.

![Confusion matrix](resources/confusion_matrix.jpg)

The numbers on the main diagonal are correct predictions. The numbers off the diagonal are the mistakes, which is where the "confusion" is. There are four cells, and every metric comes from them:

- **TP** = True Positive = 24 (had it, test said positive)
- **FN** = False Negative = 6 (had it, test said negative -- a miss)
- **FP** = False Positive = 10 (did not have it, test said positive -- a false alarm)
- **TN** = True Negative = 60 (did not have it, test said negative)

We will call the total number of cases `N`, which is 100 here.

## The Four Metrics

### Accuracy

Accuracy is the fraction of all predictions that were correct.

```text
accuracy = (TP + TN) / N
accuracy = (24 + 60) / 100
accuracy = 0.84
```

Accuracy is the first thing most people ask about: out of all the cases, how many did the classifier get right? It gives one simple number, but it has a serious weakness. It does not tell you what *kind* of mistakes the classifier made. Two classifiers can have the same accuracy while one produces many false alarms and the other misses many real cases. We need metrics that tell those cases apart.

### Precision

Precision looks only at the cases the classifier called positive, which is the left column of the confusion matrix. Of everything it flagged as positive, how many really were positive?

```text
precision = TP / (TP + FP)
precision = 24 / (24 + 10)
precision = 0.71
```

Precision is a measure of trustworthiness. When precision is low, the classifier cries "positive" too often and produces many false alarms. When precision is high, a positive prediction is usually right.

### Recall

Recall looks only at the cases that are truly positive, which is the top row of the confusion matrix. Of all the real positives, how many did the classifier catch?

```text
recall = TP / (TP + FN)
recall = 24 / (24 + 6)
recall = 0.80
```

Recall is a measure of how many real cases slip through. A classifier with low recall misses many true positives. A super-sensitive classifier catches nearly all of them and has few false negatives.

Precision and recall pull in different directions. You can raise recall by flagging more cases as positive, but that usually adds false alarms and lowers precision. Which one matters more depends on the cost of each kind of mistake.

### F1 Score

We want a single number that stays low if *either* precision or recall is low, so that a classifier cannot look good by being strong in one and weak in the other. That number is the *F1 score*. It combines precision and recall:

$$
F1 = 2 \cdot \frac{\text{precision} \cdot \text{recall}}{\text{precision} + \text{recall}}
$$

F1 is dominated by the smaller of the two values, so a classifier only gets a high F1 when precision and recall are *both* high. This is why F1 is often a better overall summary than accuracy, especially when one class is much rarer than the other.

> **Why accuracy can mislead.** Suppose only 2 of 100 people have the illness. A lazy classifier that always predicts "negative" is right 98 percent of the time, which is a wonderful-looking accuracy. But its recall is 0: it catches none of the real cases. On imbalanced data, accuracy hides this failure and F1 exposes it.

## Bringing It Back to Weather

Next lesson you will build a classifier that predicts whether a day is **good for running**. The same four metrics apply, and the two kinds of mistake have real, different costs:

- A **false positive** means the model labels a bad day as good. The app tells you to go run, and you head out into cold rain and high wind.
- A **false negative** means the model labels a good day as bad. The app tells you to skip, and you miss a perfect morning.

Neither mistake is catastrophic, but they are not equal, and which one you care about more shapes which metric you optimize. If you never want to be sent out in bad weather, you care about precision on the "good" class. If you never want to miss a good day, you care about recall. This is the judgment the metrics let you make.

## Computing the Metrics in scikit-learn

scikit-learn computes all of these for you. To see it, we can recreate the rapid-test example as lists of true and predicted labels.

```python
from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)
import matplotlib.pyplot as plt

# 30 truly positive, 70 truly negative
y_true = ["positive"] * 30 + ["negative"] * 70
# predictions: 24 TP, 6 FN, then 10 FP, 60 TN
y_pred = ["positive"] * 24 + ["negative"] * 6 + ["positive"] * 10 + ["negative"] * 60

labels = ["positive", "negative"]
cm = confusion_matrix(y_true, y_pred, labels=labels)
print(cm)

disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
disp.plot(colorbar=False)
plt.title("Rapid Test Confusion Matrix")
plt.show()
```

The printed matrix matches the numbers we worked out by hand:

```text
[[24  6]
 [10 60]]
```

The individual metrics also match:

```python
print("Accuracy: ", accuracy_score(y_true, y_pred))
print("Precision:", precision_score(y_true, y_pred, pos_label="positive"))
print("Recall:   ", recall_score(y_true, y_pred, pos_label="positive"))
print("F1:       ", f1_score(y_true, y_pred, pos_label="positive"))
```

```text
Accuracy:  0.84
Precision: 0.7058823529411765
Recall:    0.8
F1:        0.75
```

### The classification report

Rather than call each metric separately, `classification_report` gives you all of them for every class at once:

```python
print(classification_report(y_true, y_pred))
```

```text
              precision    recall  f1-score   support

    negative       0.91      0.86      0.88        70
    positive       0.71      0.80      0.75        30

    accuracy                           0.84       100
   macro avg       0.81      0.83      0.82       100
weighted avg       0.85      0.84      0.84       100
```

Each class gets its own row. There is a row for `positive` (the numbers we computed) and a row for `negative`. The `support` column is the number of true cases in each class. Below the class rows, the report gives the overall accuracy and two averages: the *macro average* treats each class equally, and the *weighted average* counts larger classes more heavily. For a binary problem like our weather classifier, you will usually look at the row for the class you care about (the "good" day) alongside the overall accuracy.

## Key Takeaways

The confusion matrix is the foundation. It shows true positives, false positives, false negatives, and true negatives, and every metric is built from those four numbers. Accuracy is the fraction correct, but it hides the pattern of errors and can be misleading on imbalanced data. Precision measures how trustworthy the positive predictions are. Recall measures how many real positives the classifier catches. F1 combines the two so a model cannot hide a weakness behind a strength. scikit-learn computes all of these with `confusion_matrix`, the individual metric functions, and `classification_report`. Next lesson you will use these exact tools to judge your first weather classifier.

## Check for Understanding

1. A classifier for a rare disease predicts "negative" for everyone and reaches 98% accuracy. What is wrong?

    a. Nothing; 98% is excellent
    b. Its recall on the positive class is 0 -- it catches none of the real cases, which accuracy hides
    c. Its precision is too high
    d. The confusion matrix cannot be computed

    <details>
    <summary>Show Answer</summary>
    b -- on imbalanced data, always predicting the majority class gives high accuracy while completely failing at the task. Recall and F1 reveal the failure.
    </details>

2. In the weather classifier, a *false positive* means:

    a. The model says a good day is bad, and you miss a nice morning
    b. The model says a bad day is good, and the app sends you out into bad weather
    c. The model refuses to make a prediction
    d. The model is overfitting

    <details>
    <summary>Show Answer</summary>
    b -- a false positive is predicting "good" when the day is actually bad. The cost is being sent out in poor conditions. A false negative is the opposite: predicting "bad" for a good day.
    </details>

3. Which metric would you focus on if you never want to be told to run on a genuinely bad day?

    a. Recall on the "good" class
    b. Precision on the "good" class
    c. Accuracy
    d. Support

    <details>
    <summary>Show Answer</summary>
    b -- precision on "good" measures how trustworthy a "good" prediction is. High precision means that when the app says "good," it is very likely right, so you are rarely sent out in bad weather.
    </details>

4. Why is F1 often more informative than accuracy?

    a. It is always higher than accuracy
    b. It stays low unless precision and recall are both high, so it cannot be fooled by a model that is strong in one and weak in the other
    c. It ignores false negatives
    d. It does not require a confusion matrix

    <details>
    <summary>Show Answer</summary>
    b -- F1 is dominated by the smaller of precision and recall, so a model must do well on both to score well. This makes it a more honest summary than accuracy, especially on imbalanced data.
    </details>
