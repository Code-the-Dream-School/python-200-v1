# Week 2 Mentor Summary: Supervised Machine Learning — Regression

**Lesson files:** `lessons/02_ML_intro.md` (overview) and three lessons in `lessons/02_ML_intro/`
**Assignment file:** `assignments/02_ML_intro.md`
**Answer key:** `mentor-guidebook/answer-key/assignment_02_key.md`
**Slides:** `mentor-guidebook/slides/02_ML_intro.pdf`

**Learning objective:** Students learn the main types of machine learning and the scikit-learn `create → fit → predict` pattern. They train linear regression models that predict a day's high temperature, evaluate them on a held-out test set with RMSE and R², and interpret the coefficients of a model with several features.

**Where this fits:** Week 1 introduced the daily weather record and the columnar Open-Meteo response. This week, students fetch one year of real daily weather from Open-Meteo for a city they choose. Week 3 uses the same API and the same four daily variables to build a classifier, and it reuses the train/test split from this week. This is the first week of machine learning, so Week 2 code does not use the Week 1 `weatherkit` package.

---

## Lesson Overview

The first lesson is conceptual. The second introduces the scikit-learn API, and the third covers regression in detail with weather data.

| Lesson | What students learn |
|---|---|
| **1. Introduction to Machine Learning** | How AI, machine learning, deep learning, generative AI, and large language models relate to one another. Supervised learning (regression and classification), unsupervised learning (clustering and dimensionality reduction), and reinforcement learning. Why simple classical models are often the right choice. There is no code in this lesson. |
| **2. Introduction to scikit-learn** | The `create → fit → predict` pattern, shown with a small example that predicts cupcake sales from temperature. Why `X` must be a 2D array, and `.reshape(-1, 1)`. A K-Means clustering demo on 150 synthetic points from `make_blobs`. |
| **3. Linear Regression** | A 500-day synthetic weather dataset with `temp_max` as the target. Correlation as a first feature check (`temp_min` is 0.96). An 80/20 `train_test_split` with `random_state=42`. RMSE and R². Adding features raises the test R² from about 0.92 to 0.94, and then to 0.96 with `is_summer`. An overfitting demo in which a degree-10 polynomial scores a test R² of -2.16. |

---

## Assignment Deliverables

**Setup:** Students work in `assignments_02/` with two files and an `outputs/` folder for plots. The code uses `scikit-learn`, `matplotlib`, and `pandas`, and the mini-project also needs `requests` for the API call.

**Grading:** The warmup uses fixed arrays and `np.random.default_rng(42)`, so its numbers are reproducible, and the answer key lists them. The mini-project uses live data for a city and year that each student chooses, so its numbers differ for every student. For the mini-project, grade the workflow and the interpretation, not the numbers. Plot file names are conventions and are not pass/fail.

| Part | File | What students do | Concepts practiced |
|---|---|---|---|
| Warmup, scikit-learn | `warmup_02.py` | Fits a model on six fixed low and high temperatures, predicts two days, and reshapes a 1D array to 2D. | `create → fit → predict`, 2D input |
| Warmup, Linear Regression | `warmup_02.py` | Five questions on 120 synthetic days with a rain flag: a scatter plot, an 80/20 split, a one-feature model, a two-feature model, and a predicted-vs-actual plot. | Train/test split, RMSE, R², coefficients |
| Project, Tasks 1–3 | `project_02.py` | Fetches one year of daily weather from Open-Meteo, checks for missing values and correlations, saves one plot, and adds a binary `is_summer` column. | API requests, feature engineering |
| Project, Tasks 4–5 | `project_02.py` | Builds a baseline model on `temperature_2m_min` alone, then a four-feature model. Prints train R², test R², test RMSE, and each coefficient. | Multiple regression, the train/test gap |
| Project, Task 6 | `project_02.py`, `outputs/` | Saves a predicted-vs-actual plot for the full model and writes a plain-language summary in comments. | Communicating results |

**Optional:** Extension A (a second city), Extension B (three years of data), and Extension C (the month as a number or as twelve one-hot columns). These are marked "(Optional)" and are not graded.

**Submission:** A link to an open pull request in the student's `python200-homework` repository.

---

## Key Concepts

These short explanations cover the ideas students ask about most this week. Expand any one you need.

<details>
<summary><strong>Why we evaluate on a test set</strong></summary>

A model can score well on its training data because it has memorized that data. The test set tells you how the model performs on days it has never seen. The lesson compares this to an exam with new questions.

`train_test_split(X, y, test_size=0.2, random_state=42)` keeps 20% of the rows aside before training. The `random_state` makes the split the same on every run, which is why the warmup numbers are reproducible.

The main check is the gap between train R² and test R². In the lesson's overfitting demo, a straight line scores 0.66 on training data and 0.67 on test data. A degree-10 polynomial on the same 30 points scores 0.76 on training data but -2.16 on test data. The more flexible model followed the noise.

The answer key says the gap is usually small for linear regression on the weather data in Task 5. That is the expected result. Students should report the small gap as evidence that the model generalizes.

</details>

<details>
<summary><strong>RMSE and R²: what each number tells you</strong></summary>

**RMSE** (root mean squared error) is the typical size of a prediction error, in the target's own units. Squaring the errors keeps positive and negative errors from cancelling, and it penalizes large errors more. The square root returns the result to degrees Celsius. In the lesson, the one-feature model has an RMSE of about 2.3, so its predictions are typically off by a little more than 2 degrees.

**R²** compares the model with a baseline that always predicts the mean: R² = 1 − (model MSE / baseline MSE). A value of 1.0 is perfect, and 0.0 is no better than the mean. R² is a ratio and not a squared value, so it can be negative on test data when the model does worse than the mean.

With one feature, R² is close to the square of the correlation. The lesson shows this: a correlation of 0.96 squared is about 0.92. In code, `model.score(X_test, y_test)` returns the same value as `r2_score(y_test, y_pred)`.

</details>

<details>
<summary><strong>Reading coefficients in a model with several features</strong></summary>

Each coefficient is the change in the predicted high for a one-unit change in that feature, **with the other features held constant**. In the warmup, the `is_rainy` coefficient is about -2.9. A rainy day is therefore predicted to be about 3 degrees cooler than a dry day with the same low. The data was generated with a true effect of -4, plus random noise.

For a binary feature, the coefficient is the shift in the prediction when the value goes from 0 to 1. In the lesson, the `is_summer` coefficient is about 3.0.

The lesson makes an important point here. On its own, `is_summer` correlates with `temp_max` at only about 0.19. In the full model it is still useful, because `temp_min` already carries most of the seasonal signal. Once the model holds `temp_min` constant, the extra warmth of summer appears. Correlation compares only two columns at a time, while a coefficient accounts for the other features.

</details>

---

## FAQs and Common Trouble Spots

**1. "I get an error saying scikit-learn expected a 2D array."**
scikit-learn requires `X` to have the shape `(n_samples, n_features)`, even with one feature. Use `.reshape(-1, 1)` on a 1D NumPy array, or select columns with double brackets, as in `df[["temp_min"]]`. The same rule applies to `predict()`, so a single day must be written as `[[6]]`.

**2. "My warmup numbers do not match the answer key."**
The warmup numbers should match closely. Check that the student copied the setup blocks labeled "Use exactly as written" without changes and generated the data only once. Creating the generator again or reordering the `rng` calls changes every value. Also check for `test_size=0.2` and `random_state=42`. The expected Linear Regression Q2 shapes are `(96, 1)`, `(24, 1)`, `(96,)`, and `(24,)`.

**3. "My Lesson 3 numbers are slightly different from the text," or "Where is `weather_daily.csv`?"**
Lesson 3 no longer loads a file. It builds its 500-day dataset with a short NumPy generator that uses `np.random.default_rng(4)`, and the numbers in the text come from that code. If a student's numbers differ, they probably changed the seed, a parameter, or the order of the `rng` calls. Small differences can also come from a different scikit-learn or NumPy version. An older version of the lesson loaded `resources/weather_daily.csv`, which was never in the repository. The assignment does not use this dataset. The warmup generates its own data, and the mini-project downloads data from Open-Meteo.

**4. "My city's summer counts look wrong."**
For a full year, a city in the Northern Hemisphere has about 92 summer days. In the Southern Hemisphere, June to August is winter, so `is_summer` marks cold days. The answer key accepts this result. It is a good opening to discuss how a feature's meaning depends on the data.

**5. "One of my coefficients has the 'wrong' sign."**
Precipitation and wind are usually negative, and `temperature_2m_min` and `is_summer` are usually positive. Signs can vary by city, and the answer key says to give credit to a student who notices a surprising sign and reasons about it.

**6. "Adding features barely improved my R²."**
This result is normal. The daily low is a strong predictor alone, often with an R² from 0.7 to 0.95. The answer key expects the full model to be at least as good as the baseline, and usually only a little better.

**7. "Which axis is which on the predicted-vs-actual plot?"**
The assignment puts predictions on the x-axis and true values on the y-axis. A point above the diagonal means the model predicted too low for that day. A point below the diagonal means it predicted too high.
