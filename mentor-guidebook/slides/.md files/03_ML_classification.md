---
marp: true
theme: default
paginate: true
---

# Week 3 — Classification & Model Deployment

Predicting whether a day is good for running, then saving the model.

---

## Classification vs regression

- Regression predicts a continuous number.
- Classification predicts a category.
- Last week we predicted the high temperature.
- This week we predict a label: good or skip.

---

## The task this week

- Each day is labeled good for running or skip.
- Good means mild, dry, and not too windy.
- The label is 1 for good and 0 for skip.
- About half the days are good.

---

## The four features

- `temperature_2m_max`, the daily high.
- `temperature_2m_min`, the daily low.
- `precipitation_sum`, total rain in mm.
- `wind_speed_10m_max`, the maximum wind.

---

## Why we scale features

- Some features have much larger ranges than others.
- A distance-based model lets the large ones dominate.
- Scaling puts every feature on comparable footing.
- `StandardScaler` gives each feature mean 0, std 1.

---

## Scale on the training set only

- Fit the scaler on the training data alone.
- Then apply it to both train and test.
- Fitting on all the data leaks the test set.
- Leakage makes the scores look better than they are.

---

## One-hot encoding

- `season` is a category, not a number.
- Numbering the seasons invents a false order.
- One-hot makes one column per season.
- Each row has a 1 in its season's column.

---

## The Pipeline

- A pipeline chains preprocessing and the model.
- It fits the scaler on training data automatically.
- It applies the same steps at prediction time.
- It becomes one object to save and load.

---

## ColumnTransformer

```python
preprocess = ColumnTransformer([
    ("num", StandardScaler(), numeric),
    ("cat", OneHotEncoder(), ["season"]),
])
```

- Numeric columns get scaled.
- The `season` column gets one-hot encoded.

---

## Building the pipeline

```python
model = Pipeline([
    ("preprocess", preprocess),
    ("classifier", LogisticRegression(max_iter=1000)),
])
model.fit(X_train, y_train)
```

- Preprocessing and the model travel together.

---

## KNN: the idea

- KNN classifies a new day by similarity.
- It finds the k most similar past days.
- Those neighbors vote on the label.
- The majority label wins.

---

## KNN and scaling

- KNN measures distance across all features.
- Without scaling, rain barely counts.
- Scaling lets every feature count fairly.
- Accuracy rose from about 0.925 to 0.958.

---

## Choosing k

- k is the number of neighbors that vote.
- Small k is sensitive to noise.
- Large k drifts toward the common class.
- Use cross-validation to choose k.

---

## Logistic Regression: the idea

- It computes a weighted sum of the features.
- The sigmoid turns that sum into a probability.
- Above 0.5 predicts good, below predicts skip.
- It draws one straight boundary between classes.

---

## Reading the coefficients

- One weight per feature, on scaled inputs.
- A negative weight pushes toward skip.
- Rain and wind had large negative weights.
- Temperature weights were small on this data.

---

## Probabilities as confidence

- Logistic regression gives a probability per day.
- 0.97 is a confident good.
- 0.52 is barely leaning toward good.
- These confidence scores are useful later.

---

## Evaluation: accuracy is not enough

- Accuracy is the fraction of predictions correct.
- It hides what kind of mistakes were made.
- Two models can match on accuracy yet differ.
- We need precision and recall too.

---

## The rapid-test intuition

- A medical test is a real classifier.
- It is sometimes right and sometimes wrong.
- The mistakes come in two different kinds.
- The same idea applies to weather.

---

## Confusion matrix, in words

- True positive: good day called good.
- False positive: bad day called good.
- False negative: good day called skip.
- True negative: bad day called skip.

---

## Precision and recall

- Precision: of days called good, how many were.
- Recall: of truly good days, how many were caught.
- A false positive sends you out in bad weather.
- A false negative makes you miss a good day.

---

## Deploy Logistic Regression, not KNN

- KNN scored higher, about 0.96 vs 0.87.
- Logistic regression gives probability scores.
- Its saved file is tiny and its weights explain it.
- KNN must ship and search its whole training set.

---

## Saving with joblib

```python
joblib.dump(model, "models/weather_classifier.pkl")
clf = joblib.load("models/weather_classifier.pkl")
```

- Save the whole pipeline, not just the classifier.
- The scaler is saved with the model.

---

## Save a metadata file too

- The `.pkl` is a binary blob.
- Record the library versions used.
- Record the feature names in order.
- Record the label rule and the scores.

---

## Optional: PCA

- PCA compresses many features into a few.
- It keeps the strongest shared patterns.
- We use it to visualize high-dimensional data.
- Week 5 uses it on language-model embeddings.

---

## Looking ahead to Week 4

- You saved a trained model to disk.
- Next week you wrap it in a reusable component.
- It gets a clean `predict()` method and tests.
- Week 10 loads it inside a cloud pipeline.
