"""Week 2 mini-project: predicting final math performance."""

import os
from typing import Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Pre-preprocessing observation:
# The raw file is semicolon-separated rather than comma-separated, so pd.read_csv
# needs sep=";". In this trimmed course copy, the yes/no and F/M categorical
# values are plain text and the grade columns G1, G2, and G3 are numeric.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATA_FILENAME = "student_performance_math.csv"

NUMERIC_FEATURES = [
    "age",
    "Medu",
    "Fedu",
    "traveltime",
    "studytime",
    "failures",
    "absences",
    "freetime",
    "goout",
    "Walc",
]

YES_NO_COLS = ["schoolsup", "internet", "higher", "activities"]

FEATURE_COLS = [
    "failures",
    "Medu",
    "Fedu",
    "studytime",
    "higher",
    "schoolsup",
    "internet",
    "sex",
    "freetime",
    "activities",
    "traveltime",
]


def find_data_file() -> str:
    """Return the student performance CSV path.

    The assignment asks for the CSV to be copied into assignments_02/. The two
    fallback paths make the script easier to run from a full course repository if
    the file is still in assignments/resources/.
    """
    candidates = [
        os.path.join(BASE_DIR, DATA_FILENAME),
        os.path.join(BASE_DIR, "..", "assignments", "resources", DATA_FILENAME),
        os.path.join(os.getcwd(), DATA_FILENAME),
        os.path.join(os.getcwd(), "assignments", "resources", DATA_FILENAME),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"Could not find {DATA_FILENAME}. Copy it into assignments_02/ first."
    )


def save_and_close(filename: str) -> str:
    """Save the active matplotlib figure into the outputs folder."""
    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Return root mean squared error."""
    return float(np.sqrt(np.mean((y_pred - y_true) ** 2)))


def print_coefficients(feature_names: Iterable[str], coefs: Iterable[float]) -> None:
    """Print feature coefficients in a readable format."""
    for name, coef in zip(feature_names, coefs):
        print(f"{name:12s}: {coef:+.3f}")


def main() -> None:
    data_path = find_data_file()

    print("--- Task 1: Load and Explore ---")
    df = pd.read_csv(data_path, sep=";")
    print(f"loaded file: {data_path}")
    print(f"shape: {df.shape}")
    print("\nfirst five rows:")
    print(df.head())
    print("\ndata types:")
    print(df.dtypes)

    plt.figure(figsize=(8, 5))
    plt.hist(df["G3"], bins=np.arange(-0.5, 21.5, 1), edgecolor="black")
    plt.title("Distribution of Final Math Grades")
    plt.xlabel("G3 final grade")
    plt.ylabel("Number of students")
    print(f"saved plot: {save_and_close('g3_distribution.png')}")

    print("\n--- Task 2: Preprocess the Data ---")
    original_shape = df.shape
    df_clean = df[df["G3"] > 0].copy()
    print(f"shape before filtering: {original_shape}")
    print(f"shape after filtering:  {df_clean.shape}")
    print(f"rows removed: {original_shape[0] - df_clean.shape[0]}")
    # G3=0 means the student missed the final exam, not that the student earned
    # a true score of zero. Keeping those rows would mix an attendance/non-test
    # outcome into a grade prediction model and distort the relationship between
    # background features and actual final performance.

    original_absences_corr = df["absences"].corr(df["G3"])

    for col in YES_NO_COLS:
        df_clean[col] = df_clean[col].map({"yes": 1, "no": 0})
    df_clean["sex"] = df_clean["sex"].map({"F": 0, "M": 1})

    filtered_absences_corr = df_clean["absences"].corr(df_clean["G3"])
    print(f"correlation absences vs G3, original data: {original_absences_corr:.3f}")
    print(f"correlation absences vs G3, filtered data: {filtered_absences_corr:.3f}")
    # Filtering changes the correlation because many G3=0 students had zero
    # absences in the original data, meaning their final-exam absence was not
    # captured as normal classroom absences. Those zeros made absences look like
    # a weak predictor before filtering; after filtering, more absences are more
    # clearly associated with lower grades.

    print("\n--- Task 3: Exploratory Data Analysis ---")
    correlations = df_clean[NUMERIC_FEATURES + ["G3"]].corr()["G3"].drop("G3")
    correlations = correlations.sort_values()
    print("numeric feature correlations with G3, sorted:")
    print(correlations)
    strongest_feature = correlations.abs().idxmax()
    print(f"strongest numeric relationship by absolute correlation: {strongest_feature}")
    # The strongest numeric relationship is failures, which is negative: past
    # class failures are associated with lower final grades. The filtered data
    # also makes absences meaningfully negative, which is more intuitive than the
    # near-zero correlation in the unfiltered data.

    rng = np.random.default_rng(42)
    failures_jitter = df_clean["failures"] + rng.normal(0, 0.04, size=len(df_clean))
    plt.figure(figsize=(8, 5))
    plt.scatter(failures_jitter, df_clean["G3"], alpha=0.7)
    plt.title("Final Grade vs Past Failures")
    plt.xlabel("Past class failures")
    plt.ylabel("G3 final grade")
    print(f"saved plot: {save_and_close('g3_vs_failures.png')}")
    # This plot shows grades shifting lower as past failures increase. There is
    # still a lot of spread, but failures are one of the clearest risk signals.

    studytime_summary = df_clean.groupby("studytime")["G3"].mean()
    plt.figure(figsize=(8, 5))
    plt.bar(studytime_summary.index.astype(str), studytime_summary.values)
    plt.title("Average Final Grade by Weekly Study Time")
    plt.xlabel("Study time category")
    plt.ylabel("Average G3 final grade")
    print(f"saved plot: {save_and_close('avg_g3_by_studytime.png')}")
    # This plot shows a generally positive relationship between study time and
    # final grade, although the differences are moderate rather than dramatic.

    print("\n--- Task 4: Baseline Model ---")
    X_baseline = df_clean[["failures"]].values
    y = df_clean["G3"].values
    X_train_base, X_test_base, y_train_base, y_test_base = train_test_split(
        X_baseline,
        y,
        test_size=0.2,
        random_state=42,
    )

    baseline_model = LinearRegression()
    baseline_model.fit(X_train_base, y_train_base)
    y_pred_base = baseline_model.predict(X_test_base)
    baseline_rmse = rmse(y_test_base, y_pred_base)
    baseline_r2 = baseline_model.score(X_test_base, y_test_base)

    print(f"slope: {baseline_model.coef_[0]:.3f}")
    print(f"RMSE: {baseline_rmse:.3f}")
    print(f"test R^2: {baseline_r2:.3f}")
    # The baseline slope is about -1.43, so each additional past failure predicts
    # about 1.4 fewer G3 points on the 0-20 scale. The RMSE is about 3.0 points,
    # which is a meaningful error for a 20-point grading scale. The R^2 is low,
    # but that matches the EDA: failures matter, yet they do not explain most of
    # the variation in grades by themselves.

    print("\n--- Task 5: Build the Full Model ---")
    X = df_clean[FEATURE_COLS].values
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    train_r2 = model.score(X_train, y_train)
    test_r2 = model.score(X_test, y_test)
    full_rmse = rmse(y_test, y_pred)

    print(f"train R^2: {train_r2:.3f}")
    print(f"test R^2: {test_r2:.3f}")
    print(f"test RMSE: {full_rmse:.3f}")
    print(f"baseline test R^2: {baseline_r2:.3f}")
    print(f"R^2 improvement over baseline: {test_r2 - baseline_r2:+.3f}")
    print("\ncoefficients:")
    print_coefficients(FEATURE_COLS, model.coef_)
    # Adding more features helps, but only modestly: test R^2 rises from about
    # 0.09 to about 0.15 and RMSE falls from about 2.96 to about 2.86 points.
    # The negative schoolsup coefficient is surprising at first, but it likely
    # reflects selection: students receiving school support are often already
    # struggling, so this coefficient should not be read as support causing lower
    # grades. Train and test R^2 are close, which suggests little overfitting;
    # both are low, so the selected background features have limited predictive
    # power without G1 or G2.
    # In production, I would keep failures, studytime, higher, internet,
    # schoolsup, and possibly Fedu because their coefficients or interpretation
    # are useful. I would be cautious with sex: it can help audit bias, but I
    # would not use it for high-stakes student decisions without a fairness
    # review. I would likely drop activities, freetime, traveltime, and Medu for
    # this simple model because their fitted effects are tiny or redundant here.

    print("\n--- Task 6: Evaluate and Summarize ---")
    plt.figure(figsize=(7, 5))
    plt.scatter(y_pred, y_test, alpha=0.75)
    min_value = min(y_pred.min(), y_test.min())
    max_value = max(y_pred.max(), y_test.max())
    plt.plot([min_value, max_value], [min_value, max_value], linestyle="--")
    plt.title("Predicted vs Actual (Full Model)")
    plt.xlabel("Predicted G3")
    plt.ylabel("Actual G3")
    exact_path = save_and_close("predicted_vs_actual.png")
    print(f"saved plot: {exact_path}")

    # Keep a project-specific copy because warmup_02.py is also required to save
    # a plot named outputs/predicted_vs_actual.png.
    plt.figure(figsize=(7, 5))
    plt.scatter(y_pred, y_test, alpha=0.75)
    plt.plot([min_value, max_value], [min_value, max_value], linestyle="--")
    plt.title("Predicted vs Actual (Full Model)")
    plt.xlabel("Predicted G3")
    plt.ylabel("Actual G3")
    print(f"saved plot: {save_and_close('project_predicted_vs_actual.png')}")
    # A point above the diagonal means the true grade was higher than predicted,
    # so the model underpredicted. A point below the diagonal means the model
    # overpredicted. The model's predictions are compressed toward the middle,
    # so it struggles most at the low and high ends instead of spreading evenly
    # across the full 0-20 grade scale.
    # Summary: after filtering G3=0 rows, the dataset has 357 students, and the
    # test set has 72 students. The full model's RMSE is about 2.86, meaning a
    # typical prediction misses by roughly three grade points on a 0-20 scale.
    # Its test R^2 is about 0.154, so it explains only a modest share of test-set
    # grade variation. The two largest positive coefficients are internet
    # (+0.834) and higher (+0.610), meaning those students are predicted to score
    # somewhat higher when other features are held constant. The two largest
    # negative coefficients are schoolsup (-2.062) and failures (-1.145). The
    # most surprising result is schoolsup being negative, which probably reflects
    # that extra school support is assigned to students already at risk.

    print("\n--- Neglected Feature: The Power of G1 ---")
    feature_cols_g1 = FEATURE_COLS + ["G1"]
    X_g1 = df_clean[feature_cols_g1].values
    X_train_g1, X_test_g1, y_train_g1, y_test_g1 = train_test_split(
        X_g1,
        y,
        test_size=0.2,
        random_state=42,
    )

    model_g1 = LinearRegression()
    model_g1.fit(X_train_g1, y_train_g1)
    y_pred_g1 = model_g1.predict(X_test_g1)
    g1_test_r2 = model_g1.score(X_test_g1, y_test_g1)
    g1_rmse = rmse(y_test_g1, y_pred_g1)

    print(f"test R^2 with G1 added: {g1_test_r2:.3f}")
    print(f"test RMSE with G1 added: {g1_rmse:.3f}")
    # The high R^2 after adding G1 does not prove that G1 causes G3; it mostly
    # shows that first-period grade is an early measurement of the same academic
    # performance process. This can still be useful for identifying students who
    # might struggle after the first grading period. If educators want to
    # intervene before G1 exists, they need earlier signals such as diagnostic
    # assessments, attendance patterns, homework completion, and study-support
    # needs instead of waiting for the first formal grade.


if __name__ == "__main__":
    main()
