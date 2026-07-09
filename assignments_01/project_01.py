"""Week 1 mini-project: World Happiness Prefect pipeline.

Run from the repository root with:
    python assignments_01/project_01.py

The raw CSV files use semicolons as delimiters and commas as decimal symbols, so
pd.read_csv() needs sep=";" and decimal=",". The pipeline normalizes the column
names to snake_case and saves all generated outputs under assignments_01/outputs/.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr

try:
    from prefect import flow, get_run_logger, task
except ModuleNotFoundError:  # Allows local validation even when Prefect is not installed.
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    def task(fn=None, **_task_kwargs):
        def decorator(func):
            return func

        return decorator(fn) if fn is not None else decorator

    def flow(fn=None, **_flow_kwargs):
        def decorator(func):
            return func

        return decorator(fn) if fn is not None else decorator

    def get_run_logger():
        return logging.getLogger("prefect-fallback")


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "assignments" / "resources" / "happiness_project"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"


def normalize_column_name(column_name: str) -> str:
    """Convert a source column name into a clean snake_case name."""
    normalized = column_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    return normalized.strip("_")


def boxplot_with_labels(values, labels: list[str]) -> None:
    """Create a boxplot with labels across Matplotlib versions."""
    try:
        plt.boxplot(values, tick_labels=labels)
    except TypeError:
        plt.boxplot(values, labels=labels)


@task(retries=3, retry_delay_seconds=2)
def load_multiple_years_of_data() -> pd.DataFrame:
    """Load every yearly happiness CSV, add year, merge, and save the result."""
    logger = get_run_logger()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    file_paths = sorted(DATA_DIR.glob("world_happiness_*.csv"))
    if not file_paths:
        raise FileNotFoundError(f"No world_happiness_*.csv files found in {DATA_DIR}")

    frames: list[pd.DataFrame] = []
    for file_path in file_paths:
        year_match = re.search(r"(\d{4})", file_path.stem)
        if year_match is None:
            logger.warning("Skipping file because no year was found in its name: %s", file_path.name)
            continue

        year = int(year_match.group(1))
        # Raw inspection shows semicolon-delimited files with comma decimal symbols.
        yearly_df = pd.read_csv(file_path, sep=";", decimal=",")
        yearly_df.columns = [normalize_column_name(column) for column in yearly_df.columns]
        yearly_df = yearly_df.rename(columns={"ladder_score": "happiness_score"})
        yearly_df["year"] = year
        frames.append(yearly_df)
        logger.info("Loaded %s rows for %s from %s.", len(yearly_df), year, file_path.name)

    combined_df = pd.concat(frames, ignore_index=True)
    output_path = OUTPUT_DIR / "merged_happiness.csv"
    combined_df.to_csv(output_path, index=False)
    logger.info("Saved merged dataset with %s rows and %s columns to %s.", *combined_df.shape, output_path)
    return combined_df


@task
def descriptive_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """Compute and log descriptive statistics overall, by year, and by region."""
    logger = get_run_logger()

    overall_stats = {
        "mean": float(df["happiness_score"].mean()),
        "median": float(df["happiness_score"].median()),
        "std": float(df["happiness_score"].std()),
    }
    logger.info("Overall happiness score mean: %.4f", overall_stats["mean"])
    logger.info("Overall happiness score median: %.4f", overall_stats["median"])
    logger.info("Overall happiness score standard deviation: %.4f", overall_stats["std"])

    mean_by_year = df.groupby("year")["happiness_score"].mean().sort_index()
    logger.info("Mean happiness score by year:\n%s", mean_by_year.to_string())

    mean_by_region = df.groupby("regional_indicator")["happiness_score"].mean().sort_values(ascending=False)
    logger.info("Mean happiness score by region:\n%s", mean_by_region.to_string())

    return {
        "overall": overall_stats,
        "mean_by_year": mean_by_year,
        "mean_by_region": mean_by_region,
    }


@task
def visual_exploration(df: pd.DataFrame) -> list[str]:
    """Create and save all requested visualizations."""
    logger = get_run_logger()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    saved_files: list[str] = []

    histogram_path = OUTPUT_DIR / "happiness_histogram.png"
    plt.figure(figsize=(9, 6))
    plt.hist(df["happiness_score"].dropna(), bins=20)
    plt.title("Distribution of Happiness Scores Across All Years")
    plt.xlabel("Happiness Score")
    plt.ylabel("Frequency")
    plt.savefig(histogram_path, bbox_inches="tight")
    plt.close()
    logger.info("Saved histogram to %s.", histogram_path)
    saved_files.append(str(histogram_path))

    boxplot_path = OUTPUT_DIR / "happiness_by_year.png"
    plt.figure(figsize=(11, 6))
    year_values = [group["happiness_score"].dropna() for _, group in df.sort_values("year").groupby("year")]
    year_labels = [str(year) for year in sorted(df["year"].unique())]
    boxplot_with_labels(year_values, year_labels)
    plt.title("Happiness Score Distribution by Year")
    plt.xlabel("Year")
    plt.ylabel("Happiness Score")
    plt.savefig(boxplot_path, bbox_inches="tight")
    plt.close()
    logger.info("Saved year boxplot to %s.", boxplot_path)
    saved_files.append(str(boxplot_path))

    scatter_path = OUTPUT_DIR / "gdp_vs_happiness.png"
    plt.figure(figsize=(9, 6))
    plt.scatter(df["gdp_per_capita"], df["happiness_score"], alpha=0.65)
    plt.title("GDP per Capita vs. Happiness Score")
    plt.xlabel("GDP per Capita")
    plt.ylabel("Happiness Score")
    plt.savefig(scatter_path, bbox_inches="tight")
    plt.close()
    logger.info("Saved GDP scatter plot to %s.", scatter_path)
    saved_files.append(str(scatter_path))

    heatmap_path = OUTPUT_DIR / "correlation_heatmap.png"
    numeric_df = df.select_dtypes(include="number")
    plt.figure(figsize=(11, 8))
    sns.heatmap(numeric_df.corr(), annot=True, fmt=".2f")
    plt.title("Correlation Heatmap")
    plt.savefig(heatmap_path, bbox_inches="tight")
    plt.close()
    logger.info("Saved correlation heatmap to %s.", heatmap_path)
    saved_files.append(str(heatmap_path))

    return saved_files


@task
def hypothesis_testing(df: pd.DataFrame, mean_by_region: pd.Series) -> dict[str, Any]:
    """Run the requested 2019 vs. 2020 test and a second regional comparison."""
    logger = get_run_logger()
    alpha = 0.05

    scores_2019 = df.loc[df["year"] == 2019, "happiness_score"].dropna()
    scores_2020 = df.loc[df["year"] == 2020, "happiness_score"].dropna()
    t_stat, p_value = stats.ttest_ind(scores_2019, scores_2020, equal_var=False)
    mean_2019 = float(scores_2019.mean())
    mean_2020 = float(scores_2020.mean())

    if p_value < alpha:
        direction = "higher" if mean_2020 > mean_2019 else "lower"
        interpretation_2020 = (
            f"The 2020 mean happiness score was {direction} than the 2019 mean, "
            f"and the difference is statistically significant at alpha = {alpha}."
        )
    else:
        interpretation_2020 = (
            f"The 2020 mean happiness score was {mean_2020:.3f} compared with {mean_2019:.3f} in 2019, "
            f"but this difference is not statistically significant at alpha = {alpha}; in this dataset, "
            "the year-to-year change could plausibly be due to random variation."
        )

    logger.info("2019 vs 2020 t-statistic: %.4f", t_stat)
    logger.info("2019 vs 2020 p-value: %.6f", p_value)
    logger.info("2019 mean happiness: %.4f", mean_2019)
    logger.info("2020 mean happiness: %.4f", mean_2020)
    logger.info("2019 vs 2020 interpretation: %s", interpretation_2020)

    # Second test: compare the regions with the highest and lowest mean happiness.
    top_region = str(mean_by_region.index[0])
    bottom_region = str(mean_by_region.index[-1])
    top_scores = df.loc[df["regional_indicator"] == top_region, "happiness_score"].dropna()
    bottom_scores = df.loc[df["regional_indicator"] == bottom_region, "happiness_score"].dropna()
    region_t_stat, region_p_value = stats.ttest_ind(top_scores, bottom_scores, equal_var=False)
    top_mean = float(top_scores.mean())
    bottom_mean = float(bottom_scores.mean())

    if region_p_value < alpha:
        region_interpretation = (
            f"{top_region} has a higher mean happiness score than {bottom_region}, and the difference "
            f"is statistically significant at alpha = {alpha}."
        )
    else:
        region_interpretation = (
            f"{top_region} has a higher mean happiness score than {bottom_region}, but the difference "
            f"is not statistically significant at alpha = {alpha}."
        )

    logger.info("Second test regions: %s vs %s", top_region, bottom_region)
    logger.info("%s mean happiness: %.4f", top_region, top_mean)
    logger.info("%s mean happiness: %.4f", bottom_region, bottom_mean)
    logger.info("Regional comparison t-statistic: %.4f", region_t_stat)
    logger.info("Regional comparison p-value: %.6f", region_p_value)
    logger.info("Regional comparison interpretation: %s", region_interpretation)

    return {
        "pandemic_test": {
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "mean_2019": mean_2019,
            "mean_2020": mean_2020,
            "interpretation": interpretation_2020,
        },
        "region_test": {
            "top_region": top_region,
            "bottom_region": bottom_region,
            "t_statistic": float(region_t_stat),
            "p_value": float(region_p_value),
            "top_region_mean": top_mean,
            "bottom_region_mean": bottom_mean,
            "interpretation": region_interpretation,
        },
    }


@task
def correlation_and_multiple_comparisons(df: pd.DataFrame) -> dict[str, Any]:
    """Correlate each numeric explanatory variable with happiness score."""
    logger = get_run_logger()
    alpha = 0.05
    target = "happiness_score"

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    explanatory_columns = [column for column in numeric_columns if column not in {target, "ranking", "year"}]

    results: list[dict[str, float | str]] = []
    for column in explanatory_columns:
        pair_df = df[[target, column]].dropna()
        if len(pair_df) < 2 or pair_df[column].nunique() < 2:
            logger.info("Skipping %s because there is not enough variation for Pearson correlation.", column)
            continue
        coefficient, p_value = pearsonr(pair_df[column], pair_df[target])
        result = {"variable": column, "coefficient": float(coefficient), "p_value": float(p_value)}
        results.append(result)
        logger.info("Correlation between %s and happiness_score: r = %.4f, p = %.6f", column, coefficient, p_value)

    number_of_tests = len(results)
    adjusted_alpha = alpha / number_of_tests if number_of_tests else np.nan
    original_significant = [result for result in results if result["p_value"] < alpha]
    bonferroni_significant = [result for result in results if result["p_value"] < adjusted_alpha]

    logger.info("Number of correlation tests performed: %s", number_of_tests)
    logger.info("Bonferroni-adjusted alpha: %.6f", adjusted_alpha)
    logger.info(
        "Significant at original alpha = 0.05: %s",
        [result["variable"] for result in original_significant],
    )
    logger.info(
        "Significant after Bonferroni correction: %s",
        [result["variable"] for result in bonferroni_significant],
    )

    strongest_after_correction = None
    if bonferroni_significant:
        strongest_after_correction = max(bonferroni_significant, key=lambda result: abs(result["coefficient"]))
        logger.info(
            "Strongest Bonferroni-significant correlation: %s (r = %.4f, p = %.6f)",
            strongest_after_correction["variable"],
            strongest_after_correction["coefficient"],
            strongest_after_correction["p_value"],
        )
    else:
        logger.info("No explanatory variables remained significant after Bonferroni correction.")

    return {
        "number_of_tests": number_of_tests,
        "adjusted_alpha": float(adjusted_alpha),
        "all_results": results,
        "original_significant": original_significant,
        "bonferroni_significant": bonferroni_significant,
        "strongest_after_correction": strongest_after_correction,
    }


@task
def summary_report(
    df: pd.DataFrame,
    descriptive_results: dict[str, Any],
    hypothesis_results: dict[str, Any],
    correlation_results: dict[str, Any],
) -> None:
    """Log the final human-readable report for a non-technical colleague."""
    logger = get_run_logger()

    number_of_countries = df["country"].nunique()
    number_of_years = df["year"].nunique()
    logger.info("Summary: The merged dataset contains %s countries across %s years.", number_of_countries, number_of_years)

    mean_by_region = descriptive_results["mean_by_region"]
    top_three_regions = mean_by_region.head(3)
    bottom_three_regions = mean_by_region.tail(3).sort_values()
    logger.info("Summary: Top 3 regions by mean happiness score:\n%s", top_three_regions.to_string())
    logger.info("Summary: Bottom 3 regions by mean happiness score:\n%s", bottom_three_regions.to_string())

    logger.info("Summary: 2019 vs 2020 test: %s", hypothesis_results["pandemic_test"]["interpretation"])

    strongest = correlation_results["strongest_after_correction"]
    if strongest is None:
        logger.info("Summary: No explanatory variable remained significantly correlated after Bonferroni correction.")
    else:
        logger.info(
            "Summary: The strongest Bonferroni-significant correlation with happiness score was %s "
            "(r = %.4f, p = %.6f).",
            strongest["variable"],
            strongest["coefficient"],
            strongest["p_value"],
        )


@flow(name="world-happiness-pipeline")
def happiness_pipeline() -> None:
    """Run the full World Happiness analysis pipeline."""
    df = load_multiple_years_of_data()
    descriptive_results = descriptive_statistics(df)
    visual_exploration(df)
    hypothesis_results = hypothesis_testing(df, descriptive_results["mean_by_region"])
    correlation_results = correlation_and_multiple_comparisons(df)
    summary_report(df, descriptive_results, hypothesis_results, correlation_results)


if __name__ == "__main__":
    happiness_pipeline()
