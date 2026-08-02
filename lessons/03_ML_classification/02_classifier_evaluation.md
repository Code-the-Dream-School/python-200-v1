# Understanding Classification Metrics 
Before we begin to work with real classifiers, we should discuss how we will *evaluate* their performance -- how good is a classifier? We will use a simple real-life example to introduce the key concepts of classifier evaluation, a rapid Covid test.

![Covid test output: image from shutterstock](resources/covid_test.jpg)

A Covid test is a *real-life classifier*. It takes an input (a biological sample), processes it internally via a biochemical reaction, and outputs a prediction that falls into one of two categories: 'positive' or 'negative'. Also, like any classifier from ML, it sometimes gets things right and sometimes gets things wrong. This makes it an instructive way to learn about how to evaluate classifier errors.

While Covid tests are not implementing ML algorithms, we can use them to help us understand different metrics for evaluating classifier performance. Then, when we use scikit-learn to build classifiers, we will evaluate them using *these exact same metrics*.

If you prefer a video explanation, this short 10-minute walkthrough does a good job explaining the confusion matrix, precision, recall, and F1 score using simple examples. It matches the concepts we introduce in this lesson and reinforces them visually:
[Evaluating a classifier](https://www.youtube.com/watch?v=-ORE0pp9QNk)

## From test results to the confusion matrix
To evaluate a classifier, we need to have a ground-truth. Let's imagine 100 patients come to a clinic with signs of illness and that we know that

- 30 patients actually have Covid (they are Covid positive)
- 70 patients do NOT have Covid (they are Covid negative)

These are the true labels. Let's also say that they are all given a rapid Covid test, and we want to know how "good" the test is (using different measures of performance). Suppose the rapid Covid test produces the following predictions:

- Of the 30 people who have Covid:

  - 24 test positive (true positives)
  - 6 test negative (misses, or false negatives)

- Of the 70 people who do *not* have Covid:
  - 10 test positive (false alarms)
  - 60 test negative (true negatives)

To clearly evaluate the Covid test, we can organize the results in a small table called a *confusion matrix*. The rows represent the actual condition, and the columns represent the *prediction*. This gives us a clean way to see all four possibilities in one place: correct positives, correct negatives, false positives, and false negatives.

![Confusion matrix](resources/confusion_matrix.jpg)

It is called a confusion matrix because while the numbers along the main diagonal represent correct predictions, the numbers off the diagonal show how "confused" the classifier is, revealing the pattern of errors.

We use abbreviations below for some of these numbers:

  - TP = True Positive  = 24
  - FN = False Negative = 6
  - FP = False Positive = 10
  - TN = True Negative  = 60

Also, we will denote the total number of tests given as `N` (which in this case is 100).

All of the metrics we use to evaluate a classifier come from the above numbers. It is really important to understand this deceptively simple representation of the performance of the classifier.

We will look at four metrics commonly used to evaluate classifier performance: accuracy, precision, recall, and F1 (which is a combination of precision and recall).

### Accuracy
Accuracy is the total percentage of predictions that the test made that were correct. It is calculated by dividing the number of correct predictions by the total number of tests:

```
accuracy = (TP + TN) / N
accuracy = (24 + 60) / 100
accuracy = 84 percent
```

Accuracy is the first thing most people want to know about a classifier: "Out of all the cases, how many did it get right?"

This is helpful because it gives one simple overall number. However, accuracy has well-known limitations: for one, it does not tell us what *kinds* of mistakes the test made.

Two classifiers can have the same accuracy but one might have lots of false positives, another might have lots of false negatives. It would be useful to have measures that can distinguish such cases.

For disease detectors (like Covid tests), we tend to want our tests to have low *false positive* rates. It would be bad if the test frequently told people they had Covid when they really did not, causing unnecessary stress and medical treatment. Is there some metric that summarizes this measure? It turns out there is, it is called the *precision*. Let's look at that next.

### Precision 
Precision focuses on cases when the test says someone has Covid (the left column of the confusion matrix). A test with low precision produces many false positives, which can cause unnecessary worry, extra doctor visits, or unneeded medication.

We can think of this as a "trustworthiness" metric. [The boy who cried wolf](https://en.wikipedia.org/wiki/The_Boy_Who_Cried_Wolf) would have a very low precision score. 

A test with high precision, on the other hand, is very trustworthy: when it says someone has Covid, it is usually right. You can calculate it solely from the elements along the left column of the confusion matrix:

```
precision = TP / (TP + FP)
precision = 24 / (24 + 10)
precision = 24 / 34
precision = 70.6 percent
```

### Recall (aka Sensitivity)
We've discussed how trustworthy the test is when it says someone has Covid. But there is another way to look at things. If someone has Covid, how likely is the test to actually detect it, how *sensitive* is the test to actual cases of Covid? 

Sensitivity focuses on the people who actually have Covid: the top row of the confusion matrix. It asks: "Out of all the people who truly have Covid, what proportion did the test catch?" A super-sensitive test will correctly identify all of them (no *false negatives*). 

That is, recall measures the proportion of false negatives (or *misses*) among those that actually are positive: what proportion slipped through the cracks? 

Calculating recall from the confusion matrix cells can be done using the elements from the top row of the confusion matrix:
```
recall = TP / (TP + FN)
recall = 24 / (24 + 6)
recall = 24 / 30
recall = 80 percent
```

### F1 Score: A balanced metric
Precision highlights false positives, and recall highlights false negatives. Is there a metric that gives us a sense for the classifier performance generally? Isn't that *accuracy*? 

Accuracy may seem like a great measure at first: just count how often the classifier is correct. But there are problems with this measure. One, as we saw above, it hides the pattern of errors (it won't tell you if your classifier gets more false positives or false negatives). 

Another problem with accuracy, not mentioned above, is that it can be very misleading when one category is much more common than the other, that is, when you have an *imbalanced* data set. For example, if only 2 out of 100 people have Covid then your dataset is extremely imbalanced. A classifier that simply predicts negative for everyone would be right 98% of the time -- an impressive accuracy number! However, it completely fails to detect any of the real Covid cases (*zero* recall/sensitivity). In other words, overall accuracy can look great even when the classifier is doing a terrible job at the task you actually care about!

This is why there is an alternative to accuracy called the *F1 score*. It is a weighted sum of precision and recall, and will be high if both are high, and low if *one* of them is low. So you can't "cheat" the measure by having high precision and low recall (or vice versa). For those that like math, it is the harmonic mean of the precision and recall: you don't need to worry about the details, but this is a measure that is dominated by the *smaller* of the two numbers.

For those that want the math, F1 is a function of both precision and recall: 
   
$$
    F1 = 2\frac{\text{precision} \cdot  \text{recall}}{\text{precision}+\text{recall}}
$$

## Metrics in scikit-learn
Later in this lesson when we look at actual classification algorithms like K-nearest neighbor, we will evaluate classifiers using the *same metrics*:

- confusion matrix  
- precision  
- recall  
- accuracy  
- F1

These are all built into scikit-learn! To illustrate how this works, in scikit-learn we can construct these metrics using synthetic data from our Covid example above. First, we can create a list of the actual covid cases (positive and negative), and the predicted cases from the confusion matrix above:

```python
# actual values: 100 people: 30 have covid, 70 do not
y_true =  ['covid +']*30 + ['covid -']*70
# predicted values:
# for positive cases: predictions: 24 tp, 6 fn
# for negative cases: predictions 10 fp, 60 tn
y_pred =  ['covid +']*24 + ['covid -']*6 + ['covid +']*10 + ['covid -']*60
```

Then, let's import the metrics that we need from scikit-learn:

```python
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import classification_report
```

### Confusion matrix
In scikit learn, the actual and predicted outputs (y values) are used to evaluate classifier output. For instance, to create the confusion matrix from our synthetic Covid data:

```python
labels = ['covid +', 'covid -']
positive_label = 'covid +'
cm = confusion_matrix(y_true, y_pred, labels=labels)
print(cm)
```

This will give:

    [[24  6]
    [10 60]]

Which is the confusion matrix we already have from above!

You can visualize this in a color-coded way using the built-in confusion-matrix display function:

```python
disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                              display_labels=labels)
disp.plot(colorbar=False)
plt.title("COVID Test Confusion Matrix")
plt.show()
```

### Metrics
Given the ground truth data, and predictions, we can also calculate the four metrics using scikit-learn functions we imported.

```python
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, pos_label=positive_label)
recall = recall_score(y_true, y_pred, pos_label=positive_label)
f1 = f1_score(y_true, y_pred, pos_label=positive_label)

print("Accuracy:", accuracy)
print("Precision (covid+):", precision)
print("Recall (covid+):", recall)
print("F1 score (covid+):", f1)
```
This will print out the same values we calculated by hand above! We already understand what these numbers mean. Now scikit-learn just saves us the arithmetic.

We are leaving one important detail out: we have only calculated precision, recall, and F1 for the `covid+` case. We'll get to that last piece of the classification evaluation puzzle next.

## Multi-Class Classification: The Final Piece of the Puzzle
So far, to simplify our analysis, we have focused only on *one* category in our example: `covid +`, and evaluated how our classifier did on that one category. However, as we saw last week, most machine learning classifiers have multiple categories, for instance, they might be shown a picture and classify what type of animal it is (out of hundreds), or what digit it is (out of ten).

With *multiple categories* instead of calculating precision/recall/F1 for just one label, you calculate *all the metrics for each category*.

This creates a natural question: How do we summarize the classifier's performance across *all* classes? The answer is that you take an average. There are two standard ways this is done in scikit-learn. One, the *macro average*, in which each class contributes equally to the mean, no matter how many examples it has. Secondly, the *weighted average*, in which classes with more data count more heavily toward the average.

In other words, in multi-class classification, you end up with *multiple* precision/recall/F1 scores (one for each category), so you need to average them to get a single summary of classifier performance.

### Back to Covid: The classification report
Technically, even our Covid test has two classes (`covid +` and `covid -`). To simplify, we only focused on `covid +`. However, `covid -` is also important: we could ask of everyone who is covid negative, how likely is the test to correctly identify them? This would be a *recall* measure for the `covid -` category (which could be calculated by looking along the bottom row of our confusion matrix).

To get a full summary of a classifier's performance, for each category, and an average score across all categories, scikit-learn produces what is known as a `classification_report`. For our example:

```python
print(classification_report(y_true, y_pred))
```

Which outputs:

```
            precision    recall  f1-score   support #how many samples

covid +       0.71      0.80      0.75        30
covid -       0.91      0.86      0.88        70

accuracy                          0.84        100
macro avg     0.81      0.83      0.82        100
weighted avg  0.85      0.84      0.84        100
```

At the top, we see one row of metrics for `covid +` and another for `covid -`. We calculated the `covid +` metrics above for precision, recall, and F1.

Below that, scikit-learn lists the aggregate metrics:
- *accuracy*: a single overall metric of proportion correct
- *macro avg* and *weighted avg*: the two multi-class summary measures we just discussed.

Those bottom rows are exactly the multi-class averages we just discussed. For disease detection, our focus is often mainly on the positive row of these outputs. But once you work with multi-class problems where all outcomes are equally important (like animals, or clothing categories) these averages become essential for understanding overall classifier performance. We will typically rely on the macro-average F1 score as our main summary metric for multi-class classification problems (the weighted average can hide poor performance on rare classes).

### Key takeaways
We used a Covid test as our running example because it acts like a simple real-life classifier. It makes the same kinds of mistakes machine-learning classifiers make, and it lets us introduce the core ideas without extra complexity.

The confusion matrix is the foundation of everything. It shows all four types of outcomes -- true positives, false positives, false negatives, and true negatives -- and every evaluation metric is derived from these numbers.

Each metric we examined tells us something different:

- Accuracy gives an overall sense of correctness, but it can hide important problems, especially when classes are imbalanced or when one type of error matters more than another.
- Precision tells us how trustworthy the positive predictions are (how often the classifier tests "positive" when it shouldn't).
- Recall tells you the proportion of real cases the classifier actually catches (how often it misses people who should have been positive).
- F1 combines precision and recall into a single score so that a model cannot hide a weakness in one area behind strength in the other.

There is no single best metric for every situation, but F1 is often a good balanced choice. Finally, scikit-learn can compute all of these metrics for any classifier you build, both for individual classes and averaged across classes. These tools will help you evaluate whether a model is actually "good" for the task you care about.