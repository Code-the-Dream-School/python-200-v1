# Week 2 Assignments

This week's assignments cover the Week 2 material:

- The scikit-learn `create → fit → predict` API
- Linear regression: fitting, evaluating, and interpreting models
- Train/test splits and generalization
- Multiple regression with numeric and binary features

As with Week 1, the warmup exercises are meant to build muscle memory for the core mechanics, so try to work through them without AI assistance. The mini-project applies these tools to real weather data in a more open-ended way. It uses the same daily weather that you will build a classifier from in Week 3.

---

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_02/`. Inside it, create two files and an outputs directory:

1. `warmup_02.py` — for the warmup exercises
2. `project_02.py` — for the mini-project
3. `outputs/` — for any plots or data files your code generates

When finished, commit and open a PR as described in the [assignments README](README.md).

**Primary submission**: A link to your open GitHub PR.

---

# Part 1: Warmup Exercises

Put all warmup exercises in a single file: `warmup_02.py`. Use comments to mark each section and question (for example `# --- scikit-learn API ---` and `# Q1`). Use `print()` to display all outputs.

## The scikit-learn API

### scikit-learn Question 1

The core pattern in scikit-learn is `create → fit → predict`. Practice it here with a small weather example: a day's low temperature versus its high temperature.

Use exactly as written:

```python
import numpy as np
from sklearn.linear_model import LinearRegression

temp_min = np.array([1, 4, 8, 12, 16, 20]).reshape(-1, 1)
temp_max = np.array([8, 10, 15, 18, 23, 27])
```

Create a `LinearRegression` model, fit it to this data, and then predict the high for a day with a low of 6 degrees and a day with a low of 18 degrees. Print the slope (`model.coef_[0]`), the intercept (`model.intercept_`), and the two predictions. Label each printed value.

### scikit-learn Question 2

scikit-learn requires the feature array `X` to be 2D even when you only have one feature. Start with this 1D array:

```python
x = np.array([10, 20, 30, 40, 50])
```

Print its shape. Use `.reshape(-1, 1)` to convert it to a 2D array and print the new shape. Add a comment explaining, in your own words, why scikit-learn needs `X` to be 2D.

## Linear Regression

The questions below all use the same small synthetic weather dataset: 120 days, each with a low temperature, a rain flag (0 = dry, 1 = rainy), and a high temperature as the target. Generate it once and reuse the variables throughout.

Use exactly as written:

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

rng = np.random.default_rng(42)
num_days  = 120
temp_min  = rng.uniform(-5, 22, num_days)
is_rainy  = rng.integers(0, 2, num_days).astype(float)
temp_max  = 1.0 * temp_min + 6 - 4 * is_rainy + rng.normal(0, 2, num_days)
```

### Linear Regression Question 1

Before fitting anything, look at the data. Create a scatter plot of `temp_min` on the x-axis and `temp_max` on the y-axis. Color the points by rain status by passing `c=is_rainy` and `cmap="coolwarm"` to `plt.scatter()`. Add the title `"Daily High vs Low"`, label both axes, and save to `outputs/high_vs_low.png`.

Add a comment describing what you see. Are there two visible groups? What does that suggest about the `is_rainy` variable?

### Linear Regression Question 2

Split the data into training and test sets using `temp_min` as the only feature, an 80/20 split, and `random_state=42`. Reshape `temp_min` to a 2D array before using it as `X`. Print the shapes of all four arrays.

### Linear Regression Question 3

Fit a `LinearRegression` model to your training data from Question 2. Print the slope and intercept. Then predict on the test set and print:

- RMSE: `np.sqrt(mean_squared_error(y_test, y_pred))`
- R² on the test set: `model.score(X_test, y_test)`

Add a comment interpreting the slope in plain English. What does it mean for the daily high?

### Linear Regression Question 4

Now add `is_rainy` as a second feature and fit a new model.

```python
X_full = np.column_stack([temp_min, is_rainy])
```

Split (80/20, `random_state=42`), fit, and print the test R². Compare it to the R² from Question 3. Does adding the rain flag help? Print both coefficients:

```python
print("temp_min coefficient:", model_full.coef_[0])
print("is_rainy coefficient:", model_full.coef_[1])
```

Add a comment interpreting the `is_rainy` coefficient. What does it represent in practical terms?

### Linear Regression Question 5

A *predicted vs actual plot* is a standard tool for evaluating regression models. Each test observation becomes a dot: the model's prediction goes on the x-axis, and the true value goes on the y-axis. A perfect model would place every point on the diagonal line where predicted equals actual.

Using the two-feature model from Question 4, create this plot for the test set. Add a diagonal reference line, the title `"Predicted vs Actual"`, labeled axes, and save to `outputs/predicted_vs_actual_warmup.png`.

Add a comment: what does it mean when a point falls above the diagonal? What about below?

---

# Part 2: Mini-Project — Predicting the Daily High

In this project you will download one year of real daily weather for a city of your choice and build a regression model that predicts the daily high temperature from other measurements of the same day. This is a teaching task: the point is to practice the full regression workflow on real, slightly messy data. It also uses the exact dataset you will reuse in Week 3, where the task changes from predicting the high to classifying whether a day is good for a run.

Put all code in `project_02.py` and save any figures to `outputs/`.

## Task 1: Fetch the Data

Use the free Open-Meteo historical API, which requires no key. The example below pulls one year of daily data for Charlotte, NC. Change the latitude and longitude to your own city.

Example — adapt the latitude, longitude, and dates to your city:

```python
import requests
import pandas as pd

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
df = pd.DataFrame(response.json()["daily"])
df["date"] = pd.to_datetime(df["time"])
df = df.drop("time", axis=1)
```

Print the shape of the dataset and the first five rows. Add a comment noting which city you chose.

## Task 2: Look at the Features

You are predicting `temperature_2m_max` (the daily high). Before modeling, look at the data.

1. Print `df.describe()` and confirm there are no missing values. If there are, decide how to handle them and explain your choice in a comment.
2. Print the correlation of each numeric column with `temperature_2m_max`, sorted. Which feature relates most strongly to the daily high?
3. Create at least one plot that helps you understand the data (for example, a histogram of the daily high, or a scatter plot of low versus high). Save it to `outputs/` and add a comment describing what you see.

## Task 3: Engineer a Feature

Add a binary `is_summer` column: 1 if the month is June, July, or August, and 0 otherwise. You can get the month from `df["date"].dt.month`.

Print the number of summer and non-summer days, and add a comment: do you expect `is_summer` to help predict the daily high, and why?

## Task 4: Baseline Model

Build the simplest useful model: use `temperature_2m_min` alone to predict `temperature_2m_max`. Split into training and test sets (80/20, `random_state=42`), fit a `LinearRegression` model, and print the slope, RMSE, and R² on the test set.

Add a comment: the RMSE is in degrees Celsius. In plain English, how far off is a typical prediction?

## Task 5: Full Model

Now build a model using four features: `temperature_2m_min`, `precipitation_sum`, `wind_speed_10m_max`, and `is_summer`.

```python
feature_cols = ["temperature_2m_min", "precipitation_sum",
                "wind_speed_10m_max", "is_summer"]
X = df[feature_cols].values
y = df["temperature_2m_max"].values
```

Split (80/20, `random_state=42`), fit a `LinearRegression` model, and print both train R² and test R², plus RMSE on the test set. Compare the test R² to your baseline from Task 4. How much does adding features help?

Print each feature name with its coefficient:

```python
for name, coef in zip(feature_cols, model.coef_):
    print(f"{name:22s}: {coef:+.3f}")
```

Add a comment interpreting the coefficients. Which features raise the predicted high, and which lower it? Are any signs surprising? Then compare train R² to test R². Are they close, or is there a gap, and what does that tell you?

## Task 6: Evaluate and Summarize

Create a *predicted vs actual plot* for your full model on the test set. Add a diagonal reference line, the title `"Predicted vs Actual (Full Model)"`, labeled axes, and save to `outputs/predicted_vs_actual_high.png`. Add a comment: does the model struggle more at the high end, the low end, or is the error roughly even across the range?

Then write a plain-language summary in comments covering:

- The size of the dataset and the test set
- The RMSE and R² of your full model, and what a typical error of that size means on a temperature scale
- Which feature has the largest effect on the predicted high, and in which direction
- One result that surprised you

---

# Optional Extensions

## Extension A (Optional): A Second City

Pull the same year of data for a second city with a very different climate. Fit the same full model and compare the RMSE and R² between the two cities. Add a comment on any difference you see and a possible reason for it.

## Extension B (Optional): More Years

Expand the training data to three years instead of one. Does more data change the test R² or RMSE? Is the change large or small? Add a comment with your finding.

## Extension C (Optional): Seasonality

Replace `is_summer` with the month number (1–12) as a numeric feature, then try it as twelve separate one-hot columns instead. Which representation predicts the daily high better, and why might that be? Add a comment with your finding.

Good luck. This is the same dataset you will classify in Week 3, so keep your city in mind.

---

<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

### Required Deliverables/Tasks

**General grading notes:**

- **Mini-project numbers vary by student.** The student chooses their own city and year, so exact slopes, RMSE, R², and coefficients will differ. Do not fail a student for numbers that differ from any reference. Grade whether the workflow is correct and the interpretation is reasonable.
- **File paths and figure names are conventions, not pass/fail.** The reviewer cannot see the filesystem. Do not fail a student for saving a plot under a different name or path.
- **Sample values are examples.** `Example — adapt to your own layout`: the latitude/longitude/dates in Task 1, and the city choice. `Use exactly as written`: the warmup setup blocks that are labeled "Use exactly as written" (the `temp_min`/`is_rainy`/`temp_max` generator and the Q1 arrays), because later warmup questions depend on those values.

**Part 1 — `warmup_02.py`:**

- **scikit-learn Q1** — a `LinearRegression` fit on the given `temp_min`/`temp_max` arrays; printed slope, intercept, and predictions for lows of 6 and 18, each labeled.
- **scikit-learn Q2** — the 1D array's shape printed, reshaped to 2D with `.reshape(-1, 1)`, the new shape printed, and a comment on why `X` must be 2D.
- **Linear Regression Q1** — a scatter of `temp_min` vs `temp_max` colored by `is_rainy`, titled and axis-labeled, saved to `outputs/`; a comment on the visible groups.
- **Linear Regression Q2** — an 80/20 split on `temp_min` alone (reshaped to 2D), `random_state=42`; shapes of all four arrays printed.
- **Linear Regression Q3** — a fitted model with slope and intercept printed; test-set RMSE and R² printed; a comment interpreting the slope.
- **Linear Regression Q4** — a two-feature model (`temp_min`, `is_rainy`); test R² compared to Q3; both coefficients printed; a comment interpreting the `is_rainy` coefficient.
- **Linear Regression Q5** — a predicted-vs-actual plot for the two-feature model with a diagonal line, titled and labeled, saved to `outputs/`; a comment on what points above/below the diagonal mean.

**Part 2 — `project_02.py`:**

- **Task 1** — daily weather fetched from Open-Meteo (any city/year); shape and first rows printed; a comment naming the city.
- **Task 2** — `describe()` and a missing-value check; per-feature correlation with the daily high, sorted; at least one plot saved with a comment.
- **Task 3** — an `is_summer` binary column derived from the month; counts printed; a comment on the expected effect.
- **Task 4** — a baseline model on `temperature_2m_min` alone; slope, RMSE, and test R² printed; a comment interpreting RMSE in degrees.
- **Task 5** — a four-feature model; train and test R² plus test RMSE printed; each feature's coefficient printed; a comment interpreting the coefficients and the train/test gap.
- **Task 6** — a predicted-vs-actual plot for the full model saved to `outputs/`, plus a plain-language summary covering dataset size, RMSE/R² meaning, the largest-effect feature, and one surprise.

### Optional Deliverables/Tasks

**Do not fail a student for omitting any of these.** They are marked "(Optional)".

- **Extension A (Optional)** — a second city, same model, RMSE/R² compared with a comment.
- **Extension B (Optional)** — three years of data, change in test R²/RMSE noted.
- **Extension C (Optional)** — month as a numeric feature versus one-hot columns, with a comment on which predicts better.

</details>
