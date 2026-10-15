# Assignment 2 Answer Key: Supervised ML — Regression

**Mentor note:** This key covers the Week 2 warmups (the scikit-learn `create → fit → predict` API and linear regression) and the mini-project that predicts a daily high temperature from live weather data. Objective tasks have one expected result. Subjective tasks list what a good answer contains.

There are two kinds of numbers in this assignment, and it is important to keep them separate.

- The **warmups** use fixed arrays and a fixed random generator (`np.random.default_rng(42)`). Their numbers *are* reproducible, so the expected values below are the values a correct submission should produce. `numpy` generates the same sequence across versions for this seed, so small differences usually mean a code error, not version drift.
- The **mini-project** downloads live data from Open-Meteo. The student chooses the city and the year, so exact slopes, RMSE, R², and coefficients will differ from one student to the next. Do not fail a student for numbers that differ from any reference. Grade whether the workflow is correct and the interpretation is reasonable.

File paths and figure names are conventions, not pass/fail. The reviewer cannot see the filesystem, so do not fail a student for saving a plot under a different name or path. Plots vary in styling. Check the required elements, not exact pixels.

---

## Expected File Setup

The assignment lives in `assignments_02/`:

```
assignments_02/
├── warmup_02.py                  # all warmup exercises
├── project_02.py                 # mini-project
└── outputs/                      # plots and any data files
```

The work is submitted as a PR. Warmups use comment markers per section and question (for example `# --- scikit-learn API ---` and `# Q1`) and `print()` for output. Students are asked to work the warmups without AI assistance.

---

# Part 1: Warmup Exercises (`warmup_02.py`)

## The scikit-learn API

### scikit-learn Q1 — **Objective**

The task is a `create → fit → predict` cycle on the fixed low/high arrays, followed by two predictions.

```python
temp_min = np.array([1, 4, 8, 12, 16, 20]).reshape(-1, 1)
temp_max = np.array([8, 10, 15, 18, 23, 27])
model = LinearRegression().fit(temp_min, temp_max)
print("Slope:", model.coef_[0])
print("Intercept:", model.intercept_)
print("Low 6:", model.predict([[6]])[0])
print("Low 18:", model.predict([[18]])[0])
```

Expected values (reproducible):

- Slope ≈ `1.02`, intercept ≈ `6.50`.
- Prediction for a low of 6 ≈ `12.6` degrees.
- Prediction for a low of 18 ≈ `24.8` degrees.

Key checks: the model is created, fit, and used to predict. `temp_min` is reshaped to 2D `(-1, 1)`. Each printed value is labeled. Predictions use a 2D input such as `[[6]]`.

### scikit-learn Q2 — **Objective + Subjective**

`x.shape` is `(5,)`. After `x.reshape(-1, 1)` the shape is `(5, 1)`. Both shapes are printed.

The comment should explain that scikit-learn expects `X` as a 2D array of shape `(n_samples, n_features)`. Each row is one sample and each column is one feature, so a single feature must still be a column rather than a flat 1D array. A 1D array raises an error when passed to `.fit()` or `.predict()`.

## Linear Regression

All five questions use the same synthetic dataset built with `np.random.default_rng(42)`. The data-generating rule is `temp_max = 1.0 * temp_min + 6 - 4 * is_rainy + noise`, so the true slope is about 1.0 and rainy days are built to be about 4 degrees cooler. Good interpretations should land near these true values.

### Linear Regression Q1 — **Objective (elements) + Subjective**

- A scatter plot of `temp_min` on the x-axis and `temp_max` on the y-axis, with `c=is_rainy` and `cmap="coolwarm"`.
- Title `"Daily High vs Low"`, both axes labeled, saved to `outputs/high_vs_low.png`.
- Comment: the student should notice **two visible bands**. Rainy days form a lower band and dry days form a higher band at the same low temperature. This suggests `is_rainy` carries real information about the high and is worth adding as a feature.

### Linear Regression Q2 — **Objective**

`train_test_split(X, y, test_size=0.2, random_state=42)` with `temp_min` reshaped to 2D as the only feature. Expected shapes:

- `X_train` = `(96, 1)`
- `X_test` = `(24, 1)`
- `y_train` = `(96,)`
- `y_test` = `(24,)`

### Linear Regression Q3 — **Objective + Subjective**

One-feature model on `temp_min`. Reproducible expected values:

- Slope ≈ `0.94`, intercept ≈ `4.58`.
- RMSE ≈ `2.5` degrees (`np.sqrt(mean_squared_error(y_test, y_pred))`).
- Test R² ≈ `0.89` (`model.score(X_test, y_test)`).

Slope interpretation: the predicted daily high rises by about one degree for each additional degree of the daily low. Any interpretation near "one degree of high per degree of low" is correct.

### Linear Regression Q4 — **Objective + Subjective**

Two-feature model built from `np.column_stack([temp_min, is_rainy])`, same 80/20 split and `random_state=42`. Reproducible expected values:

- Test R² ≈ `0.95`, up from about `0.89` in Q3. Adding the rain flag **helps**.
- `temp_min` coefficient ≈ `0.98`.
- `is_rainy` coefficient ≈ `-2.9` (negative; anywhere in roughly `-2` to `-4` is reasonable).

`is_rainy` coefficient interpretation: a rainy day is predicted to be about 3 degrees cooler than a dry day with the same low temperature, holding the low constant. Accept any answer that reads the negative sign as "rain lowers the predicted high" and connects the size to a few degrees.

### Linear Regression Q5 — **Objective (elements) + Subjective**

- A predicted-vs-actual scatter for the **two-feature** model on the test set: predictions on the x-axis, true values on the y-axis.
- A diagonal reference line where predicted equals actual, title `"Predicted vs Actual"`, both axes labeled, saved to `outputs/predicted_vs_actual_warmup.png`.
- The points should fall close to the diagonal, because R² is high.
- Comment: a point **above** the diagonal means the true high is greater than the prediction, so the model **under**-predicted that day. A point **below** the diagonal means the model **over**-predicted.

---

# Part 2: Mini-Project — Predicting the Daily High (`project_02.py`)

**Overall check:** the student downloads one year of daily weather for a city of their choice, predicts `temperature_2m_max` from other same-day measurements, and runs the full regression workflow. Because the city and year are the student's choice, exact numbers vary. The ranges and reasoning below are what matter. Numbers are in degrees Celsius.

### Task 1: Fetch the Data — **Objective (approach) + Subjective**

- Data is fetched from the Open-Meteo historical API (any city, any one-year range). The four daily fields are `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, and `wind_speed_10m_max`.
- The shape and the first five rows are printed. A one-year pull is about 365 rows and 5 columns (the four daily fields plus a date).
- A comment names the chosen city. Remind the student that they will reuse this city in Week 3.

### Task 2: Look at the Features — **Objective (approach) + Subjective**

- `df.describe()` is printed and the student confirms there are no missing values. If any exist, a comment explains how they were handled.
- The correlation of each numeric column with `temperature_2m_max` is printed, sorted. Expected pattern: `temperature_2m_min` has the **strongest** positive correlation with the daily high, usually well above 0.8. `precipitation_sum` and `wind_speed_10m_max` are weaker and often slightly negative.
- At least one plot is saved to `outputs/` with a comment describing what it shows. Any reasonable choice is fine, such as a histogram of the daily high or a scatter of low versus high.

### Task 3: Engineer a Feature — **Objective (approach) + Subjective**

- An `is_summer` binary column is added: 1 for June, July, or August, and 0 otherwise, derived from `df["date"].dt.month`.
- The counts of summer and non-summer days are printed. For a full year expect roughly 92 summer days and about 273 non-summer days in the Northern Hemisphere. A Southern-Hemisphere city will not match this, which is acceptable and worth noticing.
- Comment: the student states whether they expect `is_summer` to help and why. A good answer expects summer days to be warmer, so the feature should raise the predicted high.

### Task 4: Baseline Model — **Objective (approach) + Subjective**

- A `LinearRegression` model on `temperature_2m_min` alone, 80/20 split, `random_state=42`. Slope, RMSE, and test R² are printed.
- Expected pattern: a positive slope near 1, a strong R² (commonly 0.7 to 0.95 depending on the city's climate), and RMSE of a few degrees Celsius.
- Comment: RMSE is read in degrees. A good answer states that a typical prediction is off by about that many degrees. For example, an RMSE of 2.5 means predictions are typically off by a little more than 2 degrees.

### Task 5: Full Model — **Objective (approach) + Subjective**

- A four-feature model on `temperature_2m_min`, `precipitation_sum`, `wind_speed_10m_max`, and `is_summer`, same split and `random_state=42`. Train R², test R², and test RMSE are printed.
- The test R² should be **at least as high as the baseline** and usually a little higher. Adding features typically helps, though the gain over a strong low-temperature baseline is often small.
- Each feature name is printed with its coefficient using the loop given in the assignment.
- Comment on coefficients: `temperature_2m_min` and `is_summer` usually have **positive** coefficients that raise the predicted high. `precipitation_sum` and `wind_speed_10m_max` are usually **negative**, because rainy and windy days tend to be cooler. Signs may vary by city, and a student who notices and reasons about a surprising sign should be credited.
- Comment on the train/test gap: the student compares train R² and test R². For linear regression on this data the gap is usually small, which indicates the model generalizes well and is not overfitting.

### Task 6: Evaluate and Summarize — **Objective (elements) + Subjective**

- A predicted-vs-actual plot for the **full** model on the test set, with a diagonal reference line, title `"Predicted vs Actual (Full Model)"`, both axes labeled, saved to `outputs/predicted_vs_actual_high.png`.
- Comment: the student states where the error is largest, such as the high end, the low end, or evenly spread. Any reading supported by the plot is acceptable.
- A plain-language summary in comments covering four points: the dataset size and the test-set size, the RMSE and R² of the full model and what a typical error of that size means on a temperature scale, which feature has the largest effect on the predicted high and in which direction, and one result that surprised the student.

---

# Optional Extensions

Do not fail a student for omitting any of these. They are marked "(Optional)".

- **Extension A (Optional):** a second city with a different climate, the same full model, RMSE and R² compared with a comment. A city with a large seasonal swing often shows a different RMSE than a mild coastal city.
- **Extension B (Optional):** three years of training data instead of one, with the change in test R² or RMSE noted. The change is often small once one year already covers the seasonal cycle.
- **Extension C (Optional):** the month as a single numeric feature versus twelve one-hot columns, with a comment on which predicts better and why. One-hot months usually fit better, because temperature does not rise in a straight line from January to December.

---

## Running and Verification

- The warmups run with `python warmup_02.py` and print each labeled value. The `outputs/` directory should contain `high_vs_low.png` and `predicted_vs_actual_warmup.png`.
- The mini-project runs with `python project_02.py` and requires `requests` for the API call. The `outputs/` directory should contain the exploratory plot and `predicted_vs_actual_high.png`.
- For the warmups, confirm the reproducible numbers above. For the mini-project, confirm the workflow and the interpretation rather than exact values, because the live data varies by city and year.
