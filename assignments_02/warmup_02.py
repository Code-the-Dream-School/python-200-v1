"""Week 2 practice with linear regression."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

OUTPUTS = Path(__file__).parent / "outputs"


def main() -> None:
    """Fit the practice models and save their plots."""
    OUTPUTS.mkdir(exist_ok=True)
    # --- scikit-learn API ---
    # Q1
    temp_min = np.array([1, 4, 8, 12, 16, 20]).reshape(-1, 1)
    temp_max = np.array([8, 10, 15, 18, 23, 27])
    model = LinearRegression()
    model.fit(temp_min, temp_max)
    predictions = model.predict(np.array([6, 18]).reshape(-1, 1))
    print("Slope:", model.coef_[0])
    print("Intercept:", model.intercept_)
    print("Predicted high for low of 6 C:", predictions[0])
    print("Predicted high for low of 18 C:", predictions[1])

    # Q2
    x = np.array([10, 20, 30, 40, 50])
    print("Original shape:", x.shape)
    print("Reshaped:", x.reshape(-1, 1).shape)
    # Rows are observations; columns are features, even with just one feature.

    # --- Linear Regression ---
    rng = np.random.default_rng(42)
    num_days = 120
    temp_min = rng.uniform(-5, 22, num_days)
    is_rainy = rng.integers(0, 2, num_days).astype(float)
    temp_max = 1.0 * temp_min + 6 - 4 * is_rainy + rng.normal(0, 2, num_days)

    # Q1
    fig, ax = plt.subplots()
    points = ax.scatter(temp_min, temp_max, c=is_rainy, cmap="coolwarm")
    fig.colorbar(points, ax=ax, ticks=[0, 1], label="Rain flag (0 dry, 1 rainy)")
    ax.set(title="Daily High vs Low", xlabel="Daily low (C)", ylabel="Daily high (C)")
    fig.tight_layout()
    fig.savefig(OUTPUTS / "high_vs_low.png", dpi=150)
    plt.close(fig)

    # Q2
    X_train, X_test, y_train, y_test = train_test_split(
        temp_min.reshape(-1, 1), temp_max, test_size=0.2, random_state=42
    )
    for name, array in zip(["X_train", "X_test", "y_train", "y_test"],
                           [X_train, X_test, y_train, y_test]):
        print(name, array.shape)

    # Q3
    model = LinearRegression().fit(X_train, y_train)
    predicted = model.predict(X_test)
    baseline_r2 = model.score(X_test, y_test)
    print("Single-feature slope:", model.coef_[0])
    print("Single-feature intercept:", model.intercept_)
    print("Single-feature RMSE:", np.sqrt(mean_squared_error(y_test, predicted)))
    print("Single-feature test R2:", baseline_r2)
    print(f"Each extra degree in the low raises the predicted high by {model.coef_[0]:.3f} C.")

    # Q4
    X_full = np.column_stack([temp_min, is_rainy])
    X_train, X_test, y_train, y_test = train_test_split(
        X_full, temp_max, test_size=0.2, random_state=42
    )
    model_full = LinearRegression().fit(X_train, y_train)
    predicted = model_full.predict(X_test)
    full_r2 = r2_score(y_test, predicted)
    print("Single-feature test R2:", baseline_r2)
    print("Two-feature test R2:", full_r2)
    print("R2 change:", full_r2 - baseline_r2)
    print("temp_min coefficient:", model_full.coef_[0])
    print("is_rainy coefficient:", model_full.coef_[1])
    print(f"At the same low, switching to rainy shifts the predicted high by {model_full.coef_[1]:.3f} C.")

    # Q5
    fig, ax = plt.subplots()
    ax.scatter(predicted, y_test)
    bounds = [min(predicted.min(), y_test.min()), max(predicted.max(), y_test.max())]
    ax.plot(bounds, bounds, "k--", label="Perfect prediction")
    ax.set(title="Predicted vs Actual", xlabel="Predicted high (C)", ylabel="Actual high (C)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUTS / "predicted_vs_actual_warmup.png", dpi=150)
    plt.close(fig)
    # Above the diagonal means we predicted too low; below means too high.


if __name__ == "__main__":
    main()

# Q1 plot: two rising bands overlap, but rainy days tend to sit lower.
# Rain status can explain part of the high that the daily low misses.
# Q3 slope: one extra degree in the low adds about 0.944 C to the predicted high.
# Q4: adding rain raised test R2 from 0.8944 to 0.9451 in this run.
# At the same low, a rainy day lowers the prediction by about 2.919 C.
