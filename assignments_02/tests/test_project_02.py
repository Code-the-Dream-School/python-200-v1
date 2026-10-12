"""Check cleaning, feature boundaries, and held-out model evaluation."""

import numpy as np
import pytest
from project_02 import DAILY, TARGET, FEATURES, prepare_data, fit_models


@pytest.fixture
def payload():
    return {"daily": {
        "time": [f"2023-05-{day:02d}" for day in range(20, 32)] + ["2023-06-01", "2023-08-31", "2023-09-01"],
        TARGET: list(range(15, 30)),
        "temperature_2m_min": list(range(5, 20)),
        "precipitation_sum": [0.0] * 15,
        "wind_speed_10m_max": [10.0] * 15,
    }}


def test_summer_boundaries(payload):
    df, dropped = prepare_data(payload)
    assert dropped == 0
    flags = dict(zip(df["date"].dt.strftime("%Y-%m-%d"), df["is_summer"]))
    assert flags["2023-05-31"] == 0
    assert flags["2023-06-01"] == 1
    assert flags["2023-08-31"] == 1
    assert flags["2023-09-01"] == 0


def test_missing_rows_are_dropped_together(payload):
    payload["daily"]["precipitation_sum"][4] = None
    df, dropped = prepare_data(payload)
    assert dropped == 1
    assert len(df) == 14
    assert not df.isna().any().any()
    assert "2023-05-24" not in df["date"].dt.strftime("%Y-%m-%d").tolist()


def test_mismatched_columns_raise(payload):
    payload["daily"][TARGET].pop()
    with pytest.raises(ValueError, match="same length"):
        prepare_data(payload)


def test_duplicate_dates_raise(payload):
    payload["daily"]["time"][1] = payload["daily"]["time"][0]
    with pytest.raises(ValueError, match="unique"):
        prepare_data(payload)


@pytest.mark.parametrize("column", DAILY)
def test_infinite_values_raise(payload, column):
    payload["daily"][column][0] = np.inf
    with pytest.raises(ValueError, match="finite"):
        prepare_data(payload)


def test_split_is_disjoint_and_predictions_use_test_rows(payload):
    df, _ = prepare_data(payload)
    result = fit_models(df)
    train, test = result["train_indices"], result["test_indices"]
    assert set(train).isdisjoint(test)
    assert set(train) | set(test) == set(range(len(df)))
    assert len(test) == 3
    for name in ["baseline", "full"]:
        assert result[name]["predicted"] == pytest.approx(df[TARGET].to_numpy()[test])
        assert result[name]["rmse"] == pytest.approx(0, abs=1e-10)


def test_fit_uses_training_targets_only(payload):
    df, _ = prepare_data(payload)
    first = fit_models(df)
    altered = df.copy()
    altered.loc[first["test_indices"], TARGET] += 1000
    second = fit_models(altered)
    for name in ["baseline", "full"]:
        assert second[name]["model"].coef_ == pytest.approx(first[name]["model"].coef_)
        assert second[name]["model"].intercept_ == pytest.approx(first[name]["model"].intercept_)
        assert second[name]["test_r2"] < 0


def test_real_year_runs_from_cache():
    import json
    from project_02 import CACHE
    df, dropped = prepare_data(json.loads(CACHE.read_text()))
    assert len(df) == 365
    assert dropped == 0
    assert df["date"].min().strftime("%Y-%m-%d") == "2023-01-01"
    assert df["date"].max().strftime("%Y-%m-%d") == "2023-12-31"
    assert df["is_summer"].sum() == 92
    result = fit_models(df)
    assert len(result["train_indices"]) == 292
    assert len(result["test_indices"]) == 73
    for name in ["baseline", "full"]:
        assert np.isfinite(result[name]["predicted"]).all()
        assert np.isfinite(result[name]["rmse"])
