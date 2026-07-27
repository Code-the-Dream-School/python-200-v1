# Assignment 1 Answer Key: Analysis Intro

**Mentor note:** This key covers the Week 1 warmups (Pandas, NumPy, Matplotlib, descriptive stats, hypothesis testing, correlation, pipelines) and the World Happiness mini-project. Use it to spot-check student code quickly. Objective tasks have one expected result; subjective tasks list what a good answer contains. Plots and random-draw outputs will vary slightly between students — check the method, not exact pixels or decimals.

---

## Expected File Setup

Student repo: public GitHub repo named `python200-homework`, with this assignment in `assignments_01/`:

```
assignments_01/
├── warmup_01.py          # all warmup exercises except the Prefect one
├── prefect_warmup.py     # Pipeline Q2 (Prefect version)
├── project_01.py         # mini-project
└── outputs/              # plots and data files
```

Submitted as a PR. Warmups should use comment markers per section (e.g. `# --- Pandas ---`, `# Pandas Q1`) and `print()` for all output. Comments explaining thought process are encouraged.

---

# Part 1: Warmup Exercises (`warmup_01.py`)

## Pandas Review

### Pandas Q1 — **Objective**
Print first 3 rows, shape, and dtypes.
```python
print(df.head(3))
print(f"Shape: {df.shape}")
print(df.dtypes)
```
Expected: shape `(5, 4)`; dtypes `name` object, `grade` int64, `city` object, `passed` bool.

### Pandas Q2 — **Objective**
```python
print(df[(df["passed"]) & (df["grade"] > 80)])
```
Expected rows: Alice (85), Carol (90), Eve (95). Bob passed but grade 72; David failed. Watch for `and` used instead of `&` (raises an error) or missing parentheses.

### Pandas Q3 — **Objective**
```python
df["grade_curved"] = df["grade"] + 5
```
Expected `grade_curved`: 90, 77, 95, 73, 100.

### Pandas Q4 — **Objective**
```python
df["name_upper"] = df["name"].str.upper()
print(df[["name", "name_upper"]])
```
Expected: ALICE, BOB, CAROL, DAVID, EVE. Must use `.str.upper()` (the `.str` accessor), not a Python loop.

### Pandas Q5 — **Objective**
```python
print(df.groupby("city")["grade"].mean())
```
Expected: Austin 83.5, Boston 87.5, Denver 68.0.

### Pandas Q6 — **Objective**
```python
df["city"] = df["city"].replace("Austin", "Houston")
print(df[["name", "city"]])
```
Expected: Bob and Eve now show Houston.

### Pandas Q7 — **Objective**
```python
print(df.sort_values("grade", ascending=False).head(3))
```
Expected top 3: Eve (95), Carol (90), Alice (85).

## NumPy Review

### NumPy Q1 — **Objective**
Shape `(5,)`, dtype `int64`, ndim `1`.

### NumPy Q2 — **Objective**
Shape `(3, 3)`, size `9`.

### NumPy Q3 — **Objective**
```python
print(arr[:2, :2])
```
Expected: `[[1 2] [4 5]]`.

### NumPy Q4 — **Objective**
```python
print(np.zeros((3, 4)))
print(np.ones((2, 5)))
```
Must use `np.zeros` / `np.ones` (the "built-in command"), not manual construction.

### NumPy Q5 — **Objective**
`np.arange(0, 50, 5)` → `[0 5 10 15 20 25 30 35 40 45]` (stops before 50). Shape `(10,)`, mean `22.5`, sum `225`, std `≈14.36`.

### NumPy Q6 — **Subjective (random)**
- Uses `np.random.normal(0, 1, 200)`.
- Printed mean should be close to 0 and std close to 1 (e.g. mean within ~±0.15, std ~0.9–1.1) — exact values vary.
- Not a correctness issue if values are off by a little; that's the nature of sampling.

## Matplotlib Review

For all plotting questions: check that the chart type, title, and axis labels match the request. Exact styling/colors are up to the student.

### Matplotlib Q1 — **Objective (elements)**
Line plot of x vs y; title `"Squares"`, xlabel `"x"`, ylabel `"y"`. Curve should be the upward parabola (0,1,4,9,16,25).

### Matplotlib Q2 — **Objective (elements)**
Bar plot; title `"Subject Scores"`; both axes labeled. Uses `plt.bar()`.

### Matplotlib Q3 — **Objective (elements)**
Two scatter series on one figure (`plt.scatter` called twice), different colors, a legend, both axes labeled.

### Matplotlib Q4 — **Objective (elements)**
`plt.subplots(1, 2)`; left = line (Q1 data), right = bar (Q2 data); a title on each subplot; `plt.tight_layout()` called before showing.

## Descriptive Statistics Review

### Descriptive Stats Q1 — **Objective**
For `[12, 15, 14, 10, 18, 22, 13, 16, 14, 15]`: mean `14.9`, median `14.5`, variance `9.29`, std `≈3.048`.
Note: `np.var`/`np.std` default to population (ddof=0), giving the values above. Sample versions (ddof=1) give variance `≈10.32`, std `≈3.21` — either is acceptable if labeled sensibly.

### Descriptive Stats Q2 — **Objective (elements, random)**
Histogram, 20 bins, of `np.random.normal(65, 10, 500)`; title `"Distribution of Scores"`; both axes labeled. Shape should look roughly bell-shaped/centered near 65.

### Descriptive Stats Q3 — **Objective (elements)**
Boxplot of the two groups; boxes labeled `"Group A"` / `"Group B"`; title `"Score Comparison"`. Group B clearly higher.

### Descriptive Stats Q4 — **Subjective**
Side-by-side boxplots labeled `"Normal"` / `"Exponential"`; title `"Distribution Comparison"`. Plus a comment answering skew/central tendency:
- Correct: the **exponential** distribution is more skewed (right-skewed).
- Correct: **median** is the better measure for the skewed (exponential) data; **mean** is fine for the normal data.
- A weak answer says one is "more spread out" without addressing skew, or picks mean for the skewed distribution without justification.

### Descriptive Stats Q5 — **Subjective**
Objective part: `data1` mean `13.6`, median `12`, mode `12`; `data2` mean `40`, median `12`, mode `12`.
Explanation comment for why mean/median differ in `data2`:
- Correct: `150` is an **outlier** that pulls the **mean** up sharply, while the **median** is resistant to outliers and stays at 12.
- A weak answer just restates the numbers without naming the outlier's effect, or claims the data is "wrong."

## Hypothesis Testing Review

### Hypothesis Q1 — **Objective**
```python
t, p = stats.ttest_ind(group_a, group_b)
```
Expected: t `≈ -6.9`, p `≈ 8e-06` (well below 0.05). Sign may be positive if groups are passed in the other order — fine.

### Hypothesis Q2 — **Objective**
An `if p < 0.05:` check that prints "statistically significant" (else not). Here it prints significant.

### Hypothesis Q3 — **Objective**
```python
t, p = stats.ttest_rel(before, after)
```
Uses `ttest_rel` (paired). Expected: t `≈ -10.6`, p `≈ 1.5e-05`. Significant.

### Hypothesis Q4 — **Objective**
```python
t, p = stats.ttest_1samp(scores, 70)
```
Expected: t `≈ 1.0`, p `≈ 0.35` (not significant). Mean of scores is `71.5`.

### Hypothesis Q5 — **Objective**
```python
t, p = stats.ttest_ind(group_a, group_b, alternative="less")
```
Uses the `alternative="less"` parameter. Expected p `≈ 4e-06` (significant; group_a < group_b). Roughly half the two-tailed p-value from Q1.

### Hypothesis Q6 — **Subjective**
Plain-language conclusion for Q1. A good answer:
- States group_b scored significantly **higher** than group_a (mentions direction).
- Says the difference is very unlikely to be due to chance / random variation.
- Avoids only saying "reject the null." Should sound like something you'd tell a non-statistician.

## Correlation Review

### Correlation Q1 — **Objective**
Perfect positive relationship. Matrix is all `1.0`; `[0,1]` value is `1.0`. Comment should predict correlation of **1.0** because y is exactly 2×x (perfectly linear).

### Correlation Q2 — **Objective**
```python
r, p = pearsonr(x, y)
```
Strong negative correlation: r `≈ -0.97`, p `≈ 5e-06`.

### Correlation Q3 — **Objective**
`df.corr()` returns a 3×3 matrix. height/weight strongly positive (`≈0.99`); age weakly correlated with both. Diagonal is 1.0.

### Correlation Q4 — **Objective (elements)**
Scatter plot; title `"Negative Correlation"`; both axes labeled. Points trend downward.

### Correlation Q5 — **Objective (elements)**
`sns.heatmap()` of the Q3 matrix with `annot=True`; title `"Correlation Heatmap"`.

## Pipelines

### Pipeline Q1 — **Objective**
Three chained functions plus `data_pipeline()`. Reference implementation:
```python
def create_series(arr):
    return pd.Series(arr, name="values")

def clean_data(series):
    return series.dropna()

def summarize_data(series):
    return {
        "mean": series.mean(),
        "median": series.median(),
        "std": series.std(),
        "mode": series.mode()[0],
    }

def data_pipeline(arr):
    s = create_series(arr)
    s = clean_data(s)
    return summarize_data(s)
```
After dropping the 3 NaNs, 9 values remain: `[12, 15, 14, 10, 18, 14, 16, 22, 13]`. Expected: mean `≈14.89`, median `14.0`, std `≈3.48` (pandas default ddof=1), mode `14.0`.

## Pipeline Q2 (`prefect_warmup.py`) — **Objective + Subjective**

Objective (structure):
- Same three functions decorated with `@task`.
- `data_pipeline`/`pipeline_flow` decorated with `@flow`, calling the three tasks in order and returning the summary dict.
- `if __name__ == "__main__": pipeline_flow()` block present.
- Summary values match Q1.

Subjective (the two comment questions):
1. Why Prefect is overkill here — good answers mention: the logic is trivial/fast, runs locally in milliseconds, no scheduling/retries/monitoring needed, so orchestration adds setup and overhead for no benefit.
2. When Prefect helps even with simple logic — good answers mention: scheduled/recurring runs, automatic retries on flaky I/O or API calls, observability/logging/dashboards, alerting on failure, running many pipelines, dependencies between tasks, running in production/cloud.

---

# Part 2: Mini-Project — World Happiness Pipeline (`project_01.py`)

**Overall check:** one `@flow` calling six `@task`s in order; `get_run_logger()` used instead of `print()`; runs top-to-bottom with `python project_01.py`; re-runnable (overwrites outputs cleanly). Outputs land in `assignments_01/outputs/`.

### Pre-preprocessing (inspecting raw data) — **Subjective**
Not a graded code deliverable, but the file-loading in Task 1 should reflect what they found. The key quirk: these CSVs are **semicolon-separated** and use a **comma as the decimal** separator (European format). A student who noticed this will pass `sep=";"` and `decimal=","` to `pd.read_csv()`. If they only used the filename and the data still loaded correctly, they may have gotten a comma-delimited variant — check that numeric columns are actually numeric (not strings).

### Task 1: Load Multiple Years — **Objective (approach)**
- Loops over the 10 file paths (2015–2024); **no copy-pasted block per year**.
- Passes the correct `pd.read_csv()` params discovered above (`sep`/`decimal` as needed).
- Adds a **`year` column** to each file's DataFrame before concatenating (this is the "something missing" — each row must know its year).
- Concatenates into one DataFrame and saves to `outputs/merged_happiness.csv`.
- Decorator has `retries=3, retry_delay_seconds=2`.
- Common miss: forgetting the year column, or hardcoding each file separately.

### Task 2: Descriptive Statistics — **Objective (approach)**
- Logs mean, median, std of `happiness_score`.
- Logs mean `happiness_score` grouped by `year` and grouped by `region`.
- Uses the logger, not `print`. Exact numbers depend on how they cleaned/merged; the grouping logic is what matters.

### Task 3: Visual Exploration — **Objective (elements)**
Four saved files in `outputs/`:
- `happiness_histogram.png` — histogram of all happiness scores.
- `happiness_by_year.png` — boxplot, one box per year.
- `gdp_vs_happiness.png` — scatter of GDP per capita vs happiness.
- `correlation_heatmap.png` — `sns.heatmap(..., annot=True)` of numeric columns.
- A log message after each save.

### Task 4: Hypothesis Testing — **Objective + Subjective**
- Independent t-test comparing 2019 vs 2020 happiness scores (`stats.ttest_ind`).
- Logs t-stat, p-value, mean for each group, and a plain-language interpretation at α=0.05.
- Interpretation should say what the result *means* (was there a real drop/change in happiness), not just "reject/fail to reject."
- Note: in this dataset the 2019→2020 difference is typically **not** significant — that's a fine and correct finding; don't penalize a "no significant change" conclusion.
- A second test of the student's choice is present and reasonable (e.g. two regions), with the test matching the question asked.

### Task 5: Correlation & Multiple Comparisons — **Objective (approach)**
- Loops over each numeric explanatory variable, computes `scipy.stats.pearsonr` vs happiness, logs r and p.
- Counts the tests and computes `adjusted_alpha = 0.05 / number_of_tests`.
- Logs which correlations are significant at 0.05 vs which survive the Bonferroni threshold.
- Concept check: student should apply the corrected (smaller) alpha and note that some weak correlations may drop out. GDP, social support, and health are usually the strongest and survive correction.

### Task 6: Summary Report — **Objective (contents)**
Separate `logger.info()` calls covering:
- Total number of countries and years in the merged dataset.
- Top 3 and bottom 3 regions by mean happiness.
- The pre/post-2020 t-test result in plain language.
- The variable most strongly correlated with happiness (after Bonferroni) — usually GDP per capita or social support.

### Running — **Objective**
- `if __name__ == "__main__": happiness_pipeline()` at the bottom.
- Runs cleanly end-to-end and is safely re-runnable.
