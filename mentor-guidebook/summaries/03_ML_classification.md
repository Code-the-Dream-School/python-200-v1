# Week 3 Mentor Summary: Classification and Model Deployment

**Lesson files:** `lessons/03_ML_classification.md` (overview) and six lessons in `lessons/03_ML_classification/`
**Assignment file:** `assignments/03_ML_classification.md`
**Answer key:** `mentor-guidebook/answer-key/assignment_03_key.md`
**Slides:** `mentor-guidebook/slides/03_ML_classification.pdf`

**Learning objective:** Students build two classifiers, k-Nearest Neighbors (KNN) and logistic regression, that predict whether a day is good for running. They prepare the data inside a scikit-learn `Pipeline`, evaluate the models with a confusion matrix, precision, recall, and F1, and save the chosen model to disk with `joblib`.

**Where this fits:** Week 2 covered regression on the same weather data. Students reuse the model they save this week in Week 4, when they wrap it in a class. A cloud pipeline loads it again in Weeks 10 and 11. Students need to keep their `models/` folder.

---

## Lesson Overview

All lessons use a fixed dataset of 600 days, `weather_classification.csv`, with about half good days and half skip days. A day's label follows the rule from Week 1. A day is good when the high is between 7 and 26 °C, the low is at least 0 °C, rain is under 3 mm, and wind is under 30 km/h.

| Lesson | What students learn |
|---|---|
| **1. Preprocessing in a Pipeline** | Numeric and categorical features. `StandardScaler` (z-scores) and why to fit it on the training data only (**data leakage**). `OneHotEncoder` for `season`, and why the seasons are not numbered 1 to 4. A little feature engineering: extracting `season` from the date. A `ColumnTransformer` that sends numeric and categorical columns to different transformers, inside a `Pipeline` that behaves like one model. |
| **2. Evaluating Classifiers** | The confusion matrix (TP, FP, FN, TN), taught with a rapid medical test as the example. Accuracy, precision, recall, and F1, and why accuracy misleads on imbalanced data. What a false positive and a false negative mean for a running app. `classification_report`. |
| **3. k-Nearest Neighbors** | KNN classifies a day by a vote of its `k` most similar days. Scaling raises accuracy from about 0.925 to 0.958, because without it precipitation barely counts in the distance. 5-fold cross-validation, and choosing `k` without touching the test set. |
| **4. Logistic Regression** | A weighted sum of features passed through the sigmoid to give a probability, then a 0.5 threshold. One straight decision boundary. Reading the coefficients: rain and wind push strongly toward "skip." `predict_proba` gives confidence scores. A short note on the regularization parameter `C`. It compares KNN (about 0.96 accuracy) with logistic regression (about 0.87). |
| **5. Model Deployment with joblib** | Train once, predict many times. `joblib.dump` and `joblib.load`. Save the **whole pipeline**, not just the classifier. A metadata JSON file with library versions, feature order, and scores. A training script and a separate prediction script with no training code. The course deploys logistic regression, even though KNN scored higher. |
| **6. (Optional) PCA** | Dimensionality reduction on the digits dataset, from 64 pixel features down to 2 for plotting. `explained_variance_ratio_`. Students use PCA again in Week 5 to plot language-model embeddings. Not needed for the assignment. |

---

## Assignment Deliverables

**Setup:** Students work in `assignments_03/` and copy `weather_classification.csv` from the course repository into it. They need `scikit-learn` and `joblib`, which installs with scikit-learn.

**Grading:** The warmup uses the fixed dataset with `random_state=42`, so its numbers are reproducible, and the answer key lists them. The mini-project uses live weather data for a city each student chooses, so its numbers differ for every student. For the mini-project, grade the workflow and the reasoning, not the numbers.

| Part | File | What students do | Concepts practiced |
|---|---|---|---|
| Warmup | `warmup_03.py` | Eleven short exercises on the fixed dataset: scaling, one-hot encoding, a `ColumnTransformer` pipeline, KNN with cross-validation, scaled and unscaled KNN, logistic regression metrics, coefficients, and probabilities, a saved confusion matrix plot, and a `joblib` save-and-reload check. | Everything in Lessons 1–5 |
| Project, Tasks 1–2 | `train_classifier.py` | Fetches one year of daily weather for their city from Open-Meteo, and builds the `good_for_running` label from the threshold rule. Students may adjust the thresholds for their climate if they document the change. | API requests, feature engineering |
| Project, Tasks 3–5 | `train_classifier.py` | Builds a KNN pipeline (choosing `k` by cross-validation) and a logistic regression pipeline, compares them, and writes a justified deployment choice. **Either model is an acceptable choice.** | Cross-validation, evaluation metrics, trade-offs |
| Project, Task 6 | `models/` | Saves the chosen pipeline as `weather_classifier.pkl`, plus a metadata JSON file. | `joblib`, metadata |
| Project, Tasks 7–8 | `predict.py` | Loads the model with no training code, predicts at least four made-up days (including a borderline day), and answers three reflection questions. | Separating training from prediction |

**Optional:** Extension A (add `season`), Extension B (test the model on a second city), and Extension C (tune `C`). These are marked "(Optional)" and are not graded.

**Submission:** A pull request from the student's branch into `main` in their `python200-homework` repository. The `models/` files need to be committed.

---

## Key Concepts

These short explanations cover the ideas students ask about most this week. Expand any one you need.

<details>
<summary><strong>Data leakage, and why the Pipeline prevents it</strong></summary>

A scaler learns two numbers from data: the mean and the standard deviation of each feature. If you fit it on the whole dataset, those numbers include the test set. The model has then "seen" the test data indirectly, and its test score is better than it would be on truly new data. This is data leakage.

The fix is to fit the scaler on the training data only, and then apply that same scaler to the test data. A `Pipeline` does this automatically. `pipeline.fit(X_train, y_train)` fits the scaler and the model on the training data, and `pipeline.predict(X_test)` reuses the fitted scaler. The pipeline also matters for cross-validation, because it refits the scaler inside each fold.

If a student scales everything with `fit_transform(X)` before splitting, their scores will look a little too good. This is the most common way to break the "honest evaluation" idea.

</details>

<details>
<summary><strong>Precision or recall: which one matters?</strong></summary>

Both are about the "good" class, but they ask different questions:

- **Precision:** of the days the model called good, how many really were good? Low precision means the app sends people out in bad weather (false positives).
- **Recall:** of the days that really were good, how many did the model find? Low recall means people miss good days (false negatives).

Raising one usually lowers the other, so the right choice depends on which mistake costs more. The assignment accepts either position if the student explains it. Most students say false positives are worse for a running app.

The lesson's warning example is useful in sessions. If only 2 of 100 people have an illness, a model that always says "negative" is 98% accurate but has a recall of 0. That is why F1, which stays low unless precision and recall are both high, is often a better summary than accuracy.

</details>

<details>
<summary><strong>Why the course deploys logistic regression when KNN scored higher</strong></summary>

This is the question mentors hear most this week. On the lesson data, KNN reaches about 0.96 accuracy and logistic regression about 0.87.

**Why KNN wins on accuracy:** The good days form a box in feature space: the temperature is in range, *and* the rain is low, *and* the wind is low. Logistic regression can draw only one straight boundary, so it cannot follow the corners of the box. KNN decides by looking at nearby days, so it follows the box closely.

**Why logistic regression is still deployed:**

- It gives smooth probabilities, which the Week 10 pipeline stores as confidence scores.
- Its saved file is tiny, a few numbers. KNN has to store its entire training set and search through it for every prediction.
- Its coefficients explain its decisions.

When two models are close enough, these practical differences decide which one ships. In the assignment, either model is acceptable if the student justifies the choice with more than the accuracy score.

</details>

---

## FAQs and Common Trouble Spots

**1. "My warmup numbers do not match the answer key."**
The warmup numbers should match exactly, because the setup block fixes `random_state=42`. Ask whether the student changed the setup block, fit a scaler on the wrong data, or used a different list of `k` values. The assignment's `k` list (`[1, 3, 5, 7, 9, 11, 15, 21]`) is slightly different from the lesson's list, so grade against the assignment. Mini-project numbers are expected to differ.

**2. "My city's data is very lopsided. Almost every day is a skip day."**
This happens in very hot or very cold climates. Students may adjust the thresholds for their climate if they document the change in a comment. With imbalanced data, encourage them to look at precision, recall, and F1 rather than accuracy, as Task 2 asks.

**3. "`predict.py` gives strange results, or I see `UserWarning: X does not have valid feature names`."**
The model was trained on a DataFrame with the four features in a specific order. The prediction script needs to build its DataFrame with the same column names in the same order. Task 7 asks students to use `metadata["features"]` for this. The warning usually means that the student passed a NumPy array or a list instead of a DataFrame.

**4. "I saved my model, but the predictions on raw data are wrong."**
Check whether the student saved the whole `Pipeline` or only the classifier step. A classifier saved without its scaler produces wrong predictions on raw inputs, with no error. The fix is to `joblib.dump` the full pipeline.

**5. "The model says a freezing day is good for running."**
This is a known limitation, and the deployment lesson mentions it. The training data has very few cold days, and a single straight boundary cannot learn the lower temperature cutoff from so few examples. It is a good opening for a discussion: a model only knows the data it was trained on. It also prepares students for the Week 10 reflection question about using a model on a different city.

**6. "Should I commit the `.pkl` file to GitHub?"**
Yes, for this course. Week 4 reuses `models/weather_classifier.pkl` and the metadata file. In large projects, teams often store big model files outside Git, but these files are small.
