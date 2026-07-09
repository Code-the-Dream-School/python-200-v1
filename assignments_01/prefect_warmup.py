"""Prefect version of the Week 1 warmup data pipeline.

Run from assignments_01/ or the repository root with:
    python assignments_01/prefect_warmup.py
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

try:
    from prefect import flow, get_run_logger, task
except ModuleNotFoundError:  # Allows this script to run in environments without Prefect installed.
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


@task
def create_series(arr: np.ndarray) -> pd.Series:
    """Convert a NumPy array into a named pandas Series."""
    logger = get_run_logger()
    series = pd.Series(arr, name="values")
    logger.info("Created Series with %s values.", len(series))
    return series


@task
def clean_data(series: pd.Series) -> pd.Series:
    """Remove missing values from a Series."""
    logger = get_run_logger()
    cleaned = series.dropna()
    logger.info("Removed %s missing values.", len(series) - len(cleaned))
    return cleaned


@task
def summarize_data(series: pd.Series) -> dict[str, float]:
    """Return basic summary statistics for a cleaned Series."""
    logger = get_run_logger()
    summary = {
        "mean": float(series.mean()),
        "median": float(series.median()),
        "std": float(series.std()),
        "mode": float(series.mode()[0]),
    }
    for key, value in summary.items():
        logger.info("%s: %s", key, value)
    return summary


@flow(name="warmup-data-pipeline")
def pipeline_flow() -> dict[str, float]:
    """Run the Prefect pipeline in task order."""
    arr = np.array(
        [12.0, 15.0, np.nan, 14.0, 10.0, np.nan, 18.0, 14.0, 16.0, 22.0, np.nan, 13.0]
    )
    series = create_series(arr)
    cleaned = clean_data(series)
    summary = summarize_data(cleaned)
    return summary


if __name__ == "__main__":
    pipeline_flow()


# Reflection:
# 1. Prefect may be more overhead than it is worth here because this pipeline only
#    has three tiny steps and a few numbers. Plain functions are easier to read,
#    faster to start, and do not require a separate orchestration framework.
# 2. Prefect could still be useful if the same simple logic needed scheduling,
#    retries, logs, alerts, task-state tracking, dashboard visibility, or deployment
#    to production. It would also help if the inputs came from files, APIs, or
#    databases that might fail intermittently, or if the pipeline needed to run for
#    many datasets on a regular schedule.
