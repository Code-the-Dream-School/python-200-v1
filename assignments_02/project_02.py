"""Compare daily-high regression models on a year of local weather."""

import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).parent
OUTPUTS = ROOT / "outputs"
CACHE = OUTPUTS / "weather_daily_raw.json"
TARGET = "temperature_2m_max"
DAILY = [TARGET, "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]
FEATURES = ["temperature_2m_min", "precipitation_sum", "wind_speed_10m_max", "is_summer"]
PARAMS = {
    "latitude": 35.78, "longitude": -78.64,
    "start_date": "2023-01-01", "end_date": "2023-12-31",
    "daily": DAILY, "timezone": "America/New_York",
}
# Raleigh, North Carolina, 2023. Summer means June through August here.


def fetch_weather(path: Path = CACHE) -> dict:
    """Fetch the public archive once and save it for repeatable local runs."""
    response = requests.get("https://archive-api.open-meteo.com/v1/archive", params=PARAMS, timeout=60)
    response.raise_for_status()
    payload = response.json()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def prepare_data(payload: dict) -> tuple[pd.DataFrame, int]:
    """Check the columns, drop incomplete rows, and add the summer flag."""
    daily = payload.get("daily")
    required = ["time", *DAILY]
    if not isinstance(daily, dict) or any(name not in daily for name in required):
        raise ValueError("daily weather columns are missing")
    if any(not isinstance(daily[name], list) for name in required):
        raise ValueError("daily columns must be lists")
    if len({len(daily[name]) for name in required}) != 1:
        raise ValueError("daily columns must have the same length")
    df = pd.DataFrame({name: daily[name] for name in required})
    df["date"] = pd.to_datetime(df.pop("time"), errors="raise")
    if df["date"].isna().any() or df["date"].duplicated().any():
        raise ValueError("dates must be present and unique")
    for name in DAILY:
        df[name] = pd.to_numeric(df[name], errors="raise")
    if np.isinf(df[DAILY].to_numpy(dtype=float)).any():
        raise ValueError("measurements must be finite")
    print("Missing values before cleaning:")
    print(df.isna().sum())
    original_size = len(df)
    # Drop incomplete days rather than fill in invented measurements.
    df = df.dropna(subset=DAILY).sort_values("date").reset_index(drop=True)
    if len(df) < 10:
        raise ValueError("need at least ten complete days")
    if (df[TARGET] < df["temperature_2m_min"]).any():
        raise ValueError("daily high cannot be below the low")
    if (df[["precipitation_sum", "wind_speed_10m_max"]] < 0).any().any():
        raise ValueError("rain and wind cannot be negative")
    df["is_summer"] = df["date"].dt.month.isin([6, 7, 8]).astype(int)
    return df, original_size - len(df)


def fit_models(df: pd.DataFrame) -> dict:
    """Compare both models using the same held-out rows."""
    train, test = train_test_split(np.arange(len(df)), test_size=0.2, random_state=42)
    y = df[TARGET].to_numpy()
    results = {"train_indices": train, "test_indices": test}
    for name, features in [("baseline", [FEATURES[0]]), ("full", FEATURES)]:
        X = df[features].to_numpy()
        model = LinearRegression().fit(X[train], y[train])
        predicted = model.predict(X[test])
        results[name] = {
            "model": model, "predicted": predicted,
            "train_r2": float(model.score(X[train], y[train])),
            "test_r2": float(r2_score(y[test], predicted)),
            "rmse": float(np.sqrt(mean_squared_error(y[test], predicted))),
        }
    return results


def save_plots(df: pd.DataFrame, results: dict, directory: Path = OUTPUTS) -> None:
    """Save feature and held-out prediction plots."""
    directory.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots()
    points = ax.scatter(df[FEATURES[0]], df[TARGET], c=df["precipitation_sum"], cmap="viridis", alpha=0.7)
    fig.colorbar(points, ax=ax, label="Rain (mm)")
    ax.set(title="Raleigh Daily High vs Low", xlabel="Daily low (C)", ylabel="Daily high (C)")
    fig.tight_layout()
    fig.savefig(directory / "weather_high_vs_low.png", dpi=150)
    plt.close(fig)
    actual = df[TARGET].to_numpy()[results["test_indices"]]
    predicted = results["full"]["predicted"]
    fig, ax = plt.subplots()
    ax.scatter(predicted, actual, alpha=0.7)
    bounds = [min(actual.min(), predicted.min()), max(actual.max(), predicted.max())]
    ax.plot(bounds, bounds, "k--", label="Perfect prediction")
    ax.set(title="Predicted vs Actual (Full Model)", xlabel="Predicted high (C)", ylabel="Actual high (C)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(directory / "predicted_vs_actual_high.png", dpi=150)
    plt.close(fig)


def main() -> None:
    """Run from cached data unless a fresh download is requested."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="download the public weather archive")
    args = parser.parse_args()
    if args.fetch:
        payload = fetch_weather()
    elif CACHE.exists():
        payload = json.loads(CACHE.read_text(encoding="utf-8"))
    else:
        parser.error("no cached data; use --fetch after authorizing the public request")
    df, dropped = prepare_data(payload)
    print("Dataset shape:", df.shape)
    print(df.head().to_string(index=False))
    print(df.describe().to_string())
    print("Dropped incomplete days:", dropped)
    print("Correlations with daily high:")
    print(df[DAILY].corr()[TARGET].drop(TARGET).sort_values())
    print("Summer/non-summer counts:", df["is_summer"].value_counts().to_dict())
    # Summer may add a seasonal shift that the daily low doesn't fully capture.
    results = fit_models(df)
    for name in ["baseline", "full"]:
        item = results[name]
        print(f"{name}: train R2={item['train_r2']:.6f}, test R2={item['test_r2']:.6f}, RMSE={item['rmse']:.6f} C")
    print("Baseline slope:", results["baseline"]["model"].coef_[0])
    print("Full model coefficients:")
    for name, coefficient in zip(FEATURES, results["full"]["model"].coef_, strict=True):
        print(f"{name:22s}: {coefficient:+.6f}")
    print("Test R2 change:", results["full"]["test_r2"] - results["baseline"]["test_r2"])
    print("Train minus test R2:", results["full"]["train_r2"] - results["full"]["test_r2"])
    # Each coefficient changes predicted Celsius per feature unit, holding others fixed.
    # Coefficient sizes aren't directly comparable across C, mm, km/h, and a binary flag.
    # These same-day measurements explain observed highs; they aren't a morning forecast.
    # A random split tests held-out days in this year, not performance on future years.
    save_plots(df, results)
    actual = df[TARGET].to_numpy()[results["test_indices"]]
    predictions = results["full"]["predicted"]
    pd.DataFrame({"date": df.iloc[results["test_indices"]]["date"].to_numpy(),
                  "actual_high_c": actual, "predicted_high_c": predictions,
                  "residual_c": actual - predictions}).sort_values("date").to_csv(
        OUTPUTS / "test_predictions.csv", index=False
    )
    df.to_csv(OUTPUTS / "weather_daily.csv", index=False)
    metrics = {
        "city": "Raleigh, NC", "year": 2023, "rows": len(df), "dropped": dropped,
        "train_rows": len(results["train_indices"]), "test_rows": len(results["test_indices"]),
        "baseline": {key: results["baseline"][key] for key in ["train_r2", "test_r2", "rmse"]},
        "full": {key: results["full"][key] for key in ["train_r2", "test_r2", "rmse"]},
        "coefficients": dict(zip(FEATURES, map(float, results["full"]["model"].coef_), strict=True)),
    }
    (OUTPUTS / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("Train/test days:", metrics["train_rows"], metrics["test_rows"])
    print(f"The error scale is {metrics['full']['rmse']:.2f} C; larger misses count more in RMSE.")


if __name__ == "__main__":
    main()

# Task 2: no values were missing in the downloaded 2023 data.
# The low has the strongest correlation with the high: 0.918.
# The scatter rises clearly; wetter days often sit below the dry-day trend.
# Task 3: 92 summer days and 273 other days.
# Task 4: baseline RMSE is 3.23 C, an error scale of a few degrees.
# RMSE weights large misses more; it isn't the mean absolute error.
# Task 5: low +0.911 C per C, rain -0.146 C per mm, wind -0.069 C per km/h.
# Summer adds 1.132 C at the same low, rain, and wind. The signs look reasonable.
# Full test R2 improves by 0.0352, with RMSE falling by about 0.41 C.
# Train R2 0.8639 and test R2 0.8875 are close; no large train advantage here.
# Task 6: 365 days total, 292 training days, and 73 test days.
# Full RMSE 2.82 C means errors are on a few-degree scale; test R2 is 0.8875.
# About 88.7% of test-target variation is explained relative to its mean.
# The low dominates on a comparable scale: a one-SD shift adds about 6.72 C.
# Summer has the largest raw coefficient, but its units differ from the others.
# Cold/middle/hot test thirds have RMSE 3.03/2.74/2.67 C: colder days are a bit harder.
# The model tends to overpredict cold days and underpredict hot days.
# One notable result: test R2 is slightly higher than train R2. A split can do that;
# it doesn't mean the model learned from the test days.
