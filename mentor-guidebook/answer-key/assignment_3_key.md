# Assignment 3 Answer Key: ML Classification

**Mentor note:** This key covers Week 3 warmups (preprocessing, KNN, evaluation, decision trees, logistic regression, PCA) and the Spambase "classifier shootout" mini-project. The warmups use fixed datasets (Iris, digits) with fixed random states, so accuracy numbers are reproducible and given below. The mini-project is more open-ended — check approach and reasoning over exact numbers. Plots vary in styling; check the required elements.

---

## Expected File Setup

Assignment lives in `assignments_03/`:

```
assignments_03/
├── warmup_03.py     # all warmup exercises
├── project_03.py    # mini-project
└── outputs/         # plots
```

Submitted as a PR. Warmups use comment markers per section and `print()`. The setup import block and the Iris load (`load_iris(as_frame=True)`) run once at the top.

---

# Part 1: Warmup Exercises (`warmup_03.py`)

## Preprocessing

### Preprocessing Q1 — **Objective**
`train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)`. Shapes: `X_train (120, 4)`, `X_test (30, 4)`, `y_train (120,)`, `y_test (30,)`.

### Preprocessing Q2 — **Objective + Subjective**
Fit `StandardScaler` on `X_train`, transform both. Column means of `X_train_scaled` are all ≈ 0 (e.g. `1e-15`). Comment must explain: fit on train only to **avoid data leakage** — the test set must stay unseen, so scaling parameters (mean/std) are learned from training data only.

## KNN

### KNN Q1 — **Objective**
`KNeighborsClassifier(n_neighbors=5)` on **unscaled** train, predict test. Accuracy `≈ 0.967` (29/30). Classification report shows near-perfect precision/recall, usually one misclassification between versicolor/virginica.

### KNN Q2 — **Objective + Subjective**
Same on **scaled** data. Accuracy is the **same or nearly identical** (`≈ 0.967`, occasionally 1.0). Comment: scaling makes little difference here because Iris features are already on **similar scales** (all in cm, same order of magnitude), so no feature dominates the distance calculation.

### KNN Q3 — **Objective + Subjective**
`cross_val_score(knn, X_train, y_train, cv=5)`. Prints 5 fold scores, mean (`≈ 0.95–0.96`), std (small, ~0.03). Comment: CV is **more trustworthy** than a single split because it averages over multiple splits, reducing the chance that one lucky/unlucky split misleads you.

### KNN Q4 — **Objective + Subjective**
Loops k in `[1,3,5,7,9,11,13,15]`, prints k and mean 5-fold CV accuracy. All are high (~0.94–0.97). Comment picks a k with a justification — mid-range values (5–11) are reasonable; a good answer avoids k=1 (overfits/noisy) and notes the scores are close.

## Classifier Evaluation

### Classifier Eval Q1 — **Objective (elements) + Subjective**
Confusion matrix from KNN Q1 predictions via `ConfusionMatrixDisplay(display_labels=iris.target_names)`, saved to `outputs/knn_confusion_matrix.png`. Comment: the confusion (if any) is between **versicolor and virginica** — setosa is always perfectly separated.

## Decision Trees

### Decision Trees Q1 — **Objective + Subjective**
`DecisionTreeClassifier(max_depth=3, random_state=42)` on unscaled train. Accuracy `≈ 0.967–1.0` (typically ~0.97). Two comments expected:
- Comparison to KNN: roughly **comparable** accuracy on this easy dataset.
- Scaling: would **not** affect a decision tree — trees split on one feature threshold at a time, so monotonic rescaling doesn't change the splits.

## Logistic Regression and Regularization

### Logistic Regression Q1 — **Objective + Subjective**
Three `OneVsRestClassifier(LogisticRegression(C=..., max_iter=1000, solver='liblinear'))` on scaled Iris, C = 0.01, 1.0, 100. Prints C and `np.abs(model.coef_).sum()` for each. **Coefficient magnitude increases as C increases** (0.01 → smallest sum, 100 → largest). Comment: larger C = **weaker regularization**, so coefficients grow; smaller C = stronger regularization, shrinking coefficients toward zero. Regularization constrains coefficient size to reduce overfitting.

## PCA (digits dataset)

### PCA Q1 — **Objective (elements)**
`X_digits.shape` is `(1797, 64)`; `images.shape` is `(1797, 8, 8)`. A 1-row subplot of one example per digit 0–9, `cmap='gray_r'`, each titled with its label, saved to `outputs/sample_digits.png`.

### PCA Q2 — **Objective (elements) + Subjective**
`PCA()` fit on `X_digits`, `scores = pca.transform(X_digits)`. 2D scatter of `scores[:,0]` vs `scores[:,1]`, colored by `y_digits` (`cmap='tab10'`), with colorbar, saved to `outputs/pca_2d_projection.png`. Comment: same-digit points **do tend to cluster**, though several digits overlap in just 2 components (0, 6, 4 often separate well; others blend).

### PCA Q3 — **Objective + Subjective**
Plot `np.cumsum(pca.explained_variance_ratio_)`, saved to `outputs/pca_variance_explained.png`. Comment: roughly **13–15 components** explain ~80% of variance (accept answers in ~12–16 range).

### PCA Q4 — **Objective (elements) + Subjective**
Uses the provided `reconstruct_digit` function to reconstruct the first 5 digits at n = 2, 5, 15, 40. Grid of subplots: an "Original" row (using `images[i]`) plus one row per n value, 5 columns. Saved to `outputs/pca_reconstructions.png`. Comment: digits become clearly recognizable around **n = 15** (blurry at 2–5, sharp by 15–40), which lines up with where the variance curve from Q3 starts leveling off.

---

# Part 2: Mini-Project — Spam or Ham? (`project_03.py`)

**Overall check:** loads Spambase, builds and compares five classifiers, uses PCA correctly (scale first, fit on train only), cross-validates, and packages the best models as sklearn `Pipeline`s. Exact accuracies vary a little but Spambase results are quite stable — rough numbers given below.

### Task 1: Load and Explore — **Objective (approach) + Subjective**
- Loads Spambase (~4601 emails, 57 features + `spam_label`). Reports class balance: roughly **39% spam / 61% ham** (moderately imbalanced, not severe).
- Correct point on the imbalance: raw accuracy can be misleading — a model predicting "ham" for everything would score ~61%, so precision/recall matter.
- Boxplots for `word_freq_free`, `char_freq_!`, `capital_run_length_total` (spam vs ham), saved to `outputs/`. Spam skews higher on all three, but distributions overlap heavily with many zeros — differences are real but not clean separations.
- Correct observations: heavy zero-skew (most emails lack a given word); feature scales vary wildly (word frequencies are small fractions, capital-run lengths reach thousands); this matters for **distance-based (KNN) and coefficient-based (logistic regression)** models, which need scaling — but not for trees.

### Task 2: Prepare Data — **Objective (approach) + Subjective**
- Train/test split (a `random_state` set for reproducibility; stratify is good practice).
- `StandardScaler` fit on **train only**.
- PCA: scale first, `PCA()` fit on `X_train_scaled` only, cumulative-variance plot saved to `outputs/`, prints `n` where variance first reaches 90% (typically **~40–45 components** for Spambase).
- Slices both sets to first `n` components; keeps both full-scaled and PCA-reduced arrays.
- Common miss: fitting the scaler or PCA on the full dataset (leakage) — should be flagged.

### Task 3: Classifier Comparison — **Objective (approach) + Subjective**
Five classifiers, each with accuracy + classification report. Rough expectations:
- **KNN unscaled**: weakest, ~0.80 (distances dominated by large-scale features).
- **KNN scaled**: much better, ~0.90+. **KNN on PCA**: similar to scaled, sometimes marginally better.
- **Decision Tree**: tries `max_depth` 3/5/10/None, printing train vs test accuracy each. As depth increases, **train accuracy approaches 1.0 while test plateaus/drops** — classic overfitting. A reasonable production pick is a moderate depth (e.g. 10) with justification. Final chosen-depth report ~0.90–0.92.
- **Random Forest**: strongest, ~0.94–0.95.
- **Logistic Regression scaled**: ~0.92–0.93; on **PCA** usually slightly lower or equal.
- Summary discussion: Random Forest usually best; PCA typically doesn't beat full-feature versions here (matches the Task 2 hypothesis that trees don't benefit, and LR/KNN gain little). On the false-positive vs false-negative question, a good answer takes a clear position — for spam, a **false positive (real email marked spam) is usually costlier**, so favor precision on the spam class — and defends it.
- Best-model confusion matrix saved to `outputs/best_model_confusion_matrix.png`, with a note on which error type dominates.

### Decision Trees & Random Forests (feature importances) — **Objective (elements) + Subjective**
- Prints top 10 `.feature_importances_` for both the tree and the forest; bar chart of RF importances saved to `outputs/feature_importances.png`.
- Expected top features: `char_freq_!`, `char_freq_$`, `word_freq_free`, `word_freq_remove`, `capital_run_length_*`, `word_freq_your`, `word_freq_hp`. The two models **largely agree** on the top features, and these match intuition about spam.

### Task 4: Cross-Validation — **Objective (approach) + Subjective**
`cross_val_score(..., cv=5)` on training data for each classifier; prints mean and std per model. Random Forest is typically **most accurate and most stable** (lowest std); single Decision Tree has higher variance. Ranking should roughly match the single-split results.

### Task 5: Prediction Pipeline — **Objective (approach) + Subjective**
- Two `Pipeline`s: one tree-based (no scaler needed), one non-tree (with `StandardScaler`, plus `PCA` if it helped). Each fit on train, full classification report on test, matching earlier manual results.
- Comment: the pipelines have **different structure** — the tree pipeline skips scaling because trees are scale-invariant, while the non-tree pipeline needs the scaler (and maybe PCA). Practical value: packaging preprocessing + model together prevents train/test leakage and "forgot to scale" bugs, and makes the model a single portable object for handoff/deployment.
