"""Week 1 warmup exercises for Python 200.

Run from the repository root with:
    python assignments_01/warmup_01.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Save plots cleanly when running from the terminal.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set a seed so the random exercises produce repeatable output.
np.random.seed(42)


def save_and_close(filename: str) -> None:
    """Save the current matplotlib figure into assignments_01/outputs/."""
    output_path = OUTPUT_DIR / filename
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Saved plot: {output_path}")


def boxplot_with_labels(values, labels: list[str]) -> None:
    """Create a boxplot with labels across Matplotlib versions."""
    try:
        plt.boxplot(values, tick_labels=labels)
    except TypeError:
        plt.boxplot(values, labels=labels)


# --- Pandas ---
# Pandas Q1
print("\n--- Pandas Q1 ---")
data = {
    "name": ["Alice", "Bob", "Carol", "David", "Eve"],
    "grade": [85, 72, 90, 68, 95],
    "city": ["Boston", "Austin", "Boston", "Denver", "Austin"],
    "passed": [True, True, True, False, True],
}
df = pd.DataFrame(data)
print("First three rows:")
print(df.head(3))
print(f"Shape: {df.shape}")
print("Data types:")
print(df.dtypes)

# Pandas Q2
print("\n--- Pandas Q2 ---")
passed_above_80 = df[(df["passed"]) & (df["grade"] > 80)]
print("Students who passed and have a grade above 80:")
print(passed_above_80)

# Pandas Q3
print("\n--- Pandas Q3 ---")
df["grade_curved"] = df["grade"] + 5
print("DataFrame with grade_curved column:")
print(df)

# Pandas Q4
print("\n--- Pandas Q4 ---")
df["name_upper"] = df["name"].str.upper()
print("Original and uppercase names:")
print(df[["name", "name_upper"]])

# Pandas Q5
print("\n--- Pandas Q5 ---")
mean_grade_by_city = df.groupby("city")["grade"].mean()
print("Mean grade by city:")
print(mean_grade_by_city)

# Pandas Q6
print("\n--- Pandas Q6 ---")
df["city"] = df["city"].replace("Austin", "Houston")
print("City values after replacing Austin with Houston:")
print(df[["name", "city"]])

# Pandas Q7
print("\n--- Pandas Q7 ---")
top_three_by_grade = df.sort_values("grade", ascending=False).head(3)
print("Top 3 rows sorted by grade descending:")
print(top_three_by_grade)


# --- NumPy ---
# NumPy Q1
print("\n--- NumPy Q1 ---")
arr_1d = np.array([10, 20, 30, 40, 50])
print(f"Shape: {arr_1d.shape}")
print(f"Dtype: {arr_1d.dtype}")
print(f"Ndim: {arr_1d.ndim}")

# NumPy Q2
print("\n--- NumPy Q2 ---")
arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print("2D array:")
print(arr_2d)
print(f"Shape: {arr_2d.shape}")
print(f"Size: {arr_2d.size}")

# NumPy Q3
print("\n--- NumPy Q3 ---")
top_left_block = arr_2d[:2, :2]
print("Top-left 2x2 block:")
print(top_left_block)

# NumPy Q4
print("\n--- NumPy Q4 ---")
zeros_array = np.zeros((3, 4))
ones_array = np.ones((2, 5))
print("3x4 zeros array:")
print(zeros_array)
print("2x5 ones array:")
print(ones_array)

# NumPy Q5
print("\n--- NumPy Q5 ---")
# I expect np.arange(0, 50, 5) to start at 0 and count by 5 up to 45.
arange_array = np.arange(0, 50, 5)
print(f"Array: {arange_array}")
print(f"Shape: {arange_array.shape}")
print(f"Mean: {arange_array.mean()}")
print(f"Sum: {arange_array.sum()}")
print(f"Standard deviation: {arange_array.std()}")

# NumPy Q6
print("\n--- NumPy Q6 ---")
normal_values = np.random.normal(0, 1, 200)
print(f"Mean of 200 normal values: {normal_values.mean():.4f}")
print(f"Standard deviation of 200 normal values: {normal_values.std():.4f}")


# --- Matplotlib ---
# Matplotlib Q1
print("\n--- Matplotlib Q1 ---")
x = [0, 1, 2, 3, 4, 5]
y = [0, 1, 4, 9, 16, 25]
plt.figure()
plt.plot(x, y)
plt.title("Squares")
plt.xlabel("x")
plt.ylabel("y")
save_and_close("warmup_squares_line.png")

# Matplotlib Q2
print("\n--- Matplotlib Q2 ---")
subjects = ["Math", "Science", "English", "History"]
scores = [88, 92, 75, 83]
plt.figure()
plt.bar(subjects, scores)
plt.title("Subject Scores")
plt.xlabel("Subject")
plt.ylabel("Score")
save_and_close("warmup_subject_scores.png")

# Matplotlib Q3
print("\n--- Matplotlib Q3 ---")
x1, y1 = [1, 2, 3, 4, 5], [2, 4, 5, 4, 5]
x2, y2 = [1, 2, 3, 4, 5], [5, 4, 3, 2, 1]
plt.figure()
plt.scatter(x1, y1, color="blue", label="Dataset 1")
plt.scatter(x2, y2, color="orange", label="Dataset 2")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
save_and_close("warmup_two_scatter_datasets.png")

# Matplotlib Q4
print("\n--- Matplotlib Q4 ---")
fig, axes = plt.subplots(1, 2)
axes[0].plot(x, y)
axes[0].set_title("Squares")
axes[0].set_xlabel("x")
axes[0].set_ylabel("y")
axes[1].bar(subjects, scores)
axes[1].set_title("Subject Scores")
axes[1].set_xlabel("Subject")
axes[1].set_ylabel("Score")
plt.tight_layout()
save_and_close("warmup_subplots.png")


# --- Descriptive Statistics ---
# Descriptive Stats Q1
print("\n--- Descriptive Stats Q1 ---")
desc_data = np.array([12, 15, 14, 10, 18, 22, 13, 16, 14, 15])
print(f"Mean: {np.mean(desc_data)}")
print(f"Median: {np.median(desc_data)}")
print(f"Variance: {np.var(desc_data)}")
print(f"Standard deviation: {np.std(desc_data)}")

# Descriptive Stats Q2
print("\n--- Descriptive Stats Q2 ---")
scores_distribution = np.random.normal(65, 10, 500)
plt.figure()
plt.hist(scores_distribution, bins=20)
plt.title("Distribution of Scores")
plt.xlabel("Score")
plt.ylabel("Frequency")
save_and_close("warmup_distribution_of_scores.png")

# Descriptive Stats Q3
print("\n--- Descriptive Stats Q3 ---")
group_a_box = [55, 60, 63, 70, 68, 62, 58, 65]
group_b_box = [75, 80, 78, 90, 85, 79, 82, 88]
plt.figure()
boxplot_with_labels([group_a_box, group_b_box], ["Group A", "Group B"])
plt.title("Score Comparison")
plt.ylabel("Score")
save_and_close("warmup_score_comparison_boxplot.png")

# Descriptive Stats Q4
print("\n--- Descriptive Stats Q4 ---")
normal_data = np.random.normal(50, 5, 200)
skewed_data = np.random.exponential(10, 200)
plt.figure()
boxplot_with_labels([normal_data, skewed_data], ["Normal", "Exponential"])
plt.title("Distribution Comparison")
plt.ylabel("Value")
save_and_close("warmup_distribution_comparison_boxplot.png")
# The exponential distribution is more skewed. The median is usually a better
# measure of central tendency for skewed data, while the mean is reasonable for
# the roughly symmetric normal distribution.

# Descriptive Stats Q5
print("\n--- Descriptive Stats Q5 ---")
data1 = [10, 12, 12, 16, 18]
data2 = [10, 12, 12, 16, 150]
for label, values in [("data1", data1), ("data2", data2)]:
    series = pd.Series(values)
    print(f"{label} mean: {series.mean()}")
    print(f"{label} median: {series.median()}")
    print(f"{label} mode: {series.mode()[0]}")
# The mean and median are very different for data2 because 150 is an outlier.
# The outlier pulls the mean upward, while the median stays near the middle of
# the ordered values.


# --- Hypothesis Testing ---
# Hypothesis Q1
print("\n--- Hypothesis Q1 ---")
hyp_group_a = [72, 68, 75, 70, 69, 73, 71, 74]
hyp_group_b = [80, 85, 78, 83, 82, 86, 79, 84]
t_stat, p_value = stats.ttest_ind(hyp_group_a, hyp_group_b)
print(f"t-statistic: {t_stat:.4f}")
print(f"p-value: {p_value:.6f}")

# Hypothesis Q2
print("\n--- Hypothesis Q2 ---")
alpha = 0.05
if p_value < alpha:
    print("The result is statistically significant at alpha = 0.05.")
else:
    print("The result is not statistically significant at alpha = 0.05.")

# Hypothesis Q3
print("\n--- Hypothesis Q3 ---")
before = [60, 65, 70, 58, 62, 67, 63, 66]
after = [68, 70, 76, 65, 69, 72, 70, 71]
paired_t_stat, paired_p_value = stats.ttest_rel(before, after)
print(f"t-statistic: {paired_t_stat:.4f}")
print(f"p-value: {paired_p_value:.6f}")

# Hypothesis Q4
print("\n--- Hypothesis Q4 ---")
benchmark_scores = [72, 68, 75, 70, 69, 74, 71, 73]
one_sample_t_stat, one_sample_p_value = stats.ttest_1samp(benchmark_scores, popmean=70)
print(f"t-statistic: {one_sample_t_stat:.4f}")
print(f"p-value: {one_sample_p_value:.6f}")

# Hypothesis Q5
print("\n--- Hypothesis Q5 ---")
one_tailed_result = stats.ttest_ind(hyp_group_a, hyp_group_b, alternative="less")
print(f"one-tailed p-value: {one_tailed_result.pvalue:.6f}")

# Hypothesis Q6
print("\n--- Hypothesis Q6 ---")
print(
    "Group A's average score is lower than Group B's, and the very small "
    "p-value suggests this difference is unlikely to be due to chance."
)


# --- Correlation ---
# Correlation Q1
print("\n--- Correlation Q1 ---")
corr_x = [1, 2, 3, 4, 5]
corr_y = [2, 4, 6, 8, 10]
# I expect the correlation to be 1.0 because y is exactly 2 times x, so the
# relationship is perfectly positive and linear.
corr_matrix = np.corrcoef(corr_x, corr_y)
print("Correlation matrix:")
print(corr_matrix)
print(f"Correlation coefficient: {corr_matrix[0, 1]}")

# Correlation Q2
print("\n--- Correlation Q2 ---")
pearson_x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
pearson_y = [10, 9, 7, 8, 6, 5, 3, 4, 2, 1]
r_value, corr_p_value = pearsonr(pearson_x, pearson_y)
print(f"Correlation coefficient: {r_value:.4f}")
print(f"p-value: {corr_p_value:.6f}")

# Correlation Q3
print("\n--- Correlation Q3 ---")
people = {
    "height": [160, 165, 170, 175, 180],
    "weight": [55, 60, 65, 72, 80],
    "age": [25, 30, 22, 35, 28],
}
people_df = pd.DataFrame(people)
people_corr = people_df.corr()
print("Correlation matrix:")
print(people_corr)

# Correlation Q4
print("\n--- Correlation Q4 ---")
neg_x = [10, 20, 30, 40, 50]
neg_y = [90, 75, 60, 45, 30]
plt.figure()
plt.scatter(neg_x, neg_y)
plt.title("Negative Correlation")
plt.xlabel("x")
plt.ylabel("y")
save_and_close("warmup_negative_correlation.png")

# Correlation Q5
print("\n--- Correlation Q5 ---")
plt.figure()
sns.heatmap(people_corr, annot=True)
plt.title("Correlation Heatmap")
save_and_close("warmup_correlation_heatmap.png")


# --- Pipelines ---
# Pipeline Q1
print("\n--- Pipeline Q1 ---")


def create_series(arr: np.ndarray) -> pd.Series:
    """Convert a NumPy array into a named pandas Series."""
    return pd.Series(arr, name="values")


def clean_data(series: pd.Series) -> pd.Series:
    """Remove missing values from a Series."""
    return series.dropna()


def summarize_data(series: pd.Series) -> dict[str, float]:
    """Return basic summary statistics for a cleaned Series."""
    return {
        "mean": series.mean(),
        "median": series.median(),
        "std": series.std(),
        "mode": series.mode()[0],
    }


def data_pipeline(arr: np.ndarray) -> dict[str, float]:
    """Run the home-grown pipeline one step at a time."""
    series = create_series(arr)
    cleaned = clean_data(series)
    summary = summarize_data(cleaned)
    return summary


pipeline_arr = np.array(
    [12.0, 15.0, np.nan, 14.0, 10.0, np.nan, 18.0, 14.0, 16.0, 22.0, np.nan, 13.0]
)
pipeline_summary = data_pipeline(pipeline_arr)
for key, value in pipeline_summary.items():
    print(f"{key}: {value}")
