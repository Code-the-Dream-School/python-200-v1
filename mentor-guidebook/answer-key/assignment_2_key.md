# Assignment 2 Answer Key: ML Intro (Linear Regression)

**Mentor note:** This key covers Week 2 warmups (scikit-learn API, linear regression) and the Student Performance regression mini-project. Objective tasks have one expected result; subjective tasks list what a good answer contains. All warmups use a fixed `np.random.seed(42)` for the medical-costs data, so those numbers *are* reproducible — students who set the seed should get the values below. Plots vary in styling; check the required elements, not exact pixels.

---

## Expected File Setup

Assignment lives in `assignments_02/`:

```
assignments_02/
├── warmup_02.py                     # all warmup exercises
├── project_02.py                    # mini-project
├── student_performance_math.csv     # copied from course resources
└── outputs/                         # plots
```

Submitted as a PR. Warmups use comment markers per section and `print()` for output. Students are asked to work warmups without AI assistance.

---

# Part 1: Warmup Exercises (`warmup_02.py`)

## The scikit-learn API

### scikit-learn Q1 — **Objective**
`create → fit → predict` on years vs salary.
```python
model = LinearRegression().fit(years, salary)
print("Slope:", model.coef_[0])
print("Intercept:", model.intercept_)
print("4 yrs:", model.predict([[4]])[0])
print("8 yrs:", model.predict([[8]])[0])
```
Expected: slope `≈ 8188`, intercept `≈ 36547`. Prediction for 4 yrs `≈ 69300`, for 8 yrs `≈ 102100` (within rounding). Key check: `years` is reshaped to 2D `(-1, 1)` and predictions use a 2D input like `[[4]]`.

### scikit-learn Q2 — **Objective + Subjective**
`x.shape` is `(5,)`; after `x.reshape(-1, 1)` it's `(5, 1)`. Comment should explain that sklearn expects `X` as a 2D array of shape (n_samples, n_features) — each row is a sample, each column a feature — so even a single feature must be a column, not a flat 1D array.

### scikit-learn Q3 — **Objective (elements) + Subjective**
- `KMeans(n_clusters=3, random_state=42)`, fit on `X_clusters`, `labels = kmeans.predict(X_clusters)` (or `.labels_`).
- Prints `cluster_centers_` (3 rows, 2 cols) and `np.bincount(labels)` — three counts summing to 120 (roughly 40 each with this seed).
- Scatter plot colored by label, centers drawn as black X's, title + axis labels, saved to `outputs/kmeans_clusters.png`.
- Note: exact cluster *numbers* (which blob is 0/1/2) are arbitrary — don't expect a specific labeling.

## Linear Regression (medical costs, `np.random.seed(42)`)

Data-generating truth: `cost = 200*age + 15000*smoker + noise`. Good interpretations should land near these true values.

### Linear Regression Q1 — **Objective (elements) + Subjective**
- Scatter of age vs cost, `c=smoker`, `cmap="coolwarm"`, title `"Medical Cost vs Age"`, axes labeled, saved to `outputs/cost_vs_age.png`.
- Comment: should notice **two distinct bands/groups** — smokers form a higher-cost band, non-smokers a lower one. This suggests `smoker` is a strong predictor and cost isn't explained by age alone.

### Linear Regression Q2 — **Objective**
`train_test_split(X, y, test_size=0.2, random_state=42)` with `age` reshaped to 2D. Shapes: `X_train (80, 1)`, `X_test (20, 1)`, `y_train (80,)`, `y_test (20,)`.

### Linear Regression Q3 — **Objective + Subjective**
Age-only model. Slope `≈ 200` (a bit off due to smoker noise, roughly 180–230), intercept in the several-thousands. R² on test is **modest** (~0.15–0.35) because smoker is omitted. RMSE is large (roughly 7000–9000).
- Slope interpretation: each additional year of age is associated with ~$200 more in annual medical cost.

### Linear Regression Q4 — **Objective + Subjective**
Two-feature model (`np.column_stack([age, smoker])`). Test R² jumps substantially (typically ~0.85+). age coef `≈ 200`, smoker coef `≈ 15000`.
- Adding smoker **helps a lot** — R² rises sharply.
- Smoker coefficient interpretation: being a smoker adds ~$15,000 to predicted annual cost, holding age fixed.

### Linear Regression Q5 — **Objective (elements) + Subjective**
Predicted vs actual scatter for the two-feature model; diagonal reference line; title `"Predicted vs Actual"`; axes labeled; saved to `outputs/predicted_vs_actual_cost.png`. Points should hug the diagonal fairly closely.
- Comment: a point **above** the diagonal means actual > predicted (model **under**-predicted); **below** means actual < predicted (model **over**-predicted).

---

# Part 2: Mini-Project — Student Math Performance (`project_02.py`)

**Overall check:** predicts G3 from background/behavioral features (not G1/G2 in the main tasks); loads the CSV correctly; handles G3=0 rows; builds baseline and full models. Because there's no fixed seed on the data itself (only on the split), exact R²/coefficients vary slightly — the ranges and reasoning below are what matter.

### Pre-preprocessing — **Objective (one detail) + Subjective**
The key detail: this CSV is **semicolon-separated**, so `pd.read_csv(..., sep=";")` is required. A comment at the top of the script should note this. If loaded without `sep=";"`, everything lands in one column — an easy tell.

### Task 1: Load and Explore — **Objective (approach)**
- Loads with `sep=";"`; prints shape (355 rows × 18 cols before filtering), first 5 rows, dtypes.
- Histogram of G3 with 21 bins, title `"Distribution of Final Math Grades"`, axes labeled, saved to `outputs/g3_distribution.png`.
- A visible cluster of zeros sits apart from the main (roughly bell-shaped, centered ~10-11) distribution.

### Task 2: Preprocess — **Objective (approach) + Subjective**
- Filters out G3=0 rows into a new DataFrame; prints shape before/after (removes ~38 rows, leaving ~357→ note dataset is ~395 rows in full original; trimmed version here starts at 355, ~38 zeros removed).
- Converts yes/no columns to 1/0 and `sex` F/M to 0/1.
- Computes Pearson `absences` vs G3 on original vs filtered — value moves from near-zero/slightly-negative to a clearer relationship.
- Reasoning comment (why filtering changes it): the G3=0 students **didn't take the final** — many had few absences but a 0 grade, breaking the real relationship. Removing them reveals the true (positive/weak) association. Keeping them would distort the model because a 0 grade doesn't mean "performed worst," it means "absent from exam."

### Task 3: EDA — **Objective (approach) + Subjective**
- Pearson correlation of each numeric feature vs G3 on the filtered data, sorted most-negative to most-positive.
- Expected pattern: `failures`, `goout`, `Walc`, `age` correlate **negatively**; `Medu`, `Fedu`, `studytime`, `higher` correlate **positively**. `failures` typically has the strongest (negative) relationship.
- At least two student-chosen plots saved to `outputs/`, each with an interpreting comment. Any reasonable choice (e.g. G3 by failures, G3 vs studytime) is fine — check that the comment describes what the plot shows.

### Task 4: Baseline Model — **Objective (approach) + Subjective**
- `failures`-only `LinearRegression`, 80/20 split, `random_state=42`. Prints slope, RMSE, R².
- Expected: negative slope (~ -2 to -3 points per failure), RMSE around 3–4 (on the 0–20 scale), R² low (~0.10–0.20).
- Interpretation: each past failure predicts ~2–3 fewer final points; RMSE of ~3 means typical prediction is off by ~3 grade points; R² likely lower than EDA might have suggested because one feature can't capture much.

### Task 5: Full Model — **Objective (approach) + Subjective**
- Uses the 15-feature `feature_cols` list, 80/20 split, `random_state=42`. Prints train R², test R², and test RMSE.
- Expected: test R² around **0.20–0.35** — better than baseline but still modest. Train R² is somewhat higher than test R² (a modest gap, indicating mild overfitting, not severe).
- Prints each feature name with its coefficient.
- Discussion should engage with: surprising signs (e.g. `absences` near zero despite decent raw correlation), which features to keep/drop (reasonable to keep `failures`, `Medu`/`Fedu`, `studytime`, `higher`, `sex`, `goout`, `Walc`; drop near-zero ones like `absences`, `freetime`, `internet`, `activities`), and the train/test gap. Justification matters more than the exact list.

### Task 6: Evaluate and Summarize — **Objective (elements) + Subjective**
- Predicted vs actual plot for the test set, diagonal line, title `"Predicted vs Actual (Full Model)"`, axes labeled, saved to `outputs/predicted_vs_actual_g3.png`.
- Comment on where error concentrates: the model typically **struggles at the extremes** (over-predicts low grades, under-predicts high ones) — regression to the mean. Above diagonal = actual > predicted; below = actual < predicted.
- Plain-language summary covering: filtered dataset & test-set size; RMSE/R² meaning on a 0–20 scale (typical error ~3 points); largest positive & negative coefficients; one surprise.

### Neglected Feature: The Power of G1 — **Objective (result) + Subjective**
- Adds `G1` to the full model, refits, prints new test R². Should jump to **~0.75–0.85**.
- Discussion should recognize: high R² does **not** mean G1 *causes* G3 (they measure the same underlying ability at different times). It's a great *predictive* model but useless for **early** intervention, since G1 doesn't exist yet at the start of the year. Educators wanting to intervene early must rely on the background/behavioral features (the weaker but *available* signal).

### After You're Done (three concept questions) — **Subjective**
Not required deliverables, but if answered:
- **absences disappearing:** correct answer explains that a small coefficient ≠ "doesn't matter"; overlapping information with `failures`/`goout`/`Walc` means absences adds little *unique* signal once those are included.
- **higher/failures changing:** correct answer notes coefficients are relative to the other features present; a one-feature model lets `failures` absorb correlated effects, and adding features narrows each to its unique contribution.
- **goout/Walc:** correct answer recognizes the negative relationship is real but the causal story is ambiguous — behavior and grades could share an upstream cause; noticing that ambiguity is the point.
