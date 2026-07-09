"""Week 2 warmup exercises for Python 200."""

import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_and_close(filename: str) -> str:
    """Save the active matplotlib figure into the outputs folder."""
    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def main() -> None:
    print("--- scikit-learn API ---")

    # Q1
    print("\nQ1: LinearRegression create -> fit -> predict")
    years = np.array([1, 2, 3, 5, 7, 10]).reshape(-1, 1)
    salary = np.array([45000, 50000, 60000, 75000, 90000, 120000])

    salary_model = LinearRegression()
    salary_model.fit(years, salary)
    salary_predictions = salary_model.predict(np.array([[4], [8]]))

    print(f"slope: {salary_model.coef_[0]:.2f}")
    print(f"intercept: {salary_model.intercept_:.2f}")
    print(f"predicted salary for 4 years: ${salary_predictions[0]:,.2f}")
    print(f"predicted salary for 8 years: ${salary_predictions[1]:,.2f}")

    # Q2
    print("\nQ2: Reshaping one feature for scikit-learn")
    x = np.array([10, 20, 30, 40, 50])
    print(f"original shape: {x.shape}")
    x_reshaped = x.reshape(-1, 1)
    print(f"reshaped shape: {x_reshaped.shape}")
    # scikit-learn expects X to be 2D because rows represent observations and
    # columns represent features; even one feature still needs its own column.

    # Q3
    print("\nQ3: KMeans create -> fit -> predict")
    X_clusters, _ = make_blobs(
        n_samples=120,
        centers=3,
        cluster_std=0.8,
        random_state=7,
    )

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(X_clusters)
    labels = kmeans.predict(X_clusters)

    print("cluster centers:")
    print(kmeans.cluster_centers_)
    print(f"points per cluster: {np.bincount(labels)}")

    plt.figure(figsize=(7, 5))
    plt.scatter(X_clusters[:, 0], X_clusters[:, 1], c=labels)
    plt.scatter(
        kmeans.cluster_centers_[:, 0],
        kmeans.cluster_centers_[:, 1],
        marker="x",
        s=150,
        c="black",
        linewidths=3,
        label="Cluster centers",
    )
    plt.title("KMeans Clusters")
    plt.xlabel("Feature 1")
    plt.ylabel("Feature 2")
    plt.legend()
    print(f"saved plot: {save_and_close('kmeans_clusters.png')}")

    print("\n--- Linear Regression ---")

    # Generate the synthetic medical costs dataset once and reuse it below.
    np.random.seed(42)
    num_patients = 100
    age = np.random.randint(20, 65, num_patients).astype(float)
    smoker = np.random.randint(0, 2, num_patients).astype(float)
    cost = 200 * age + 15000 * smoker + np.random.normal(0, 3000, num_patients)

    # Q1
    print("\nLinear Regression Q1: Explore medical cost data")
    plt.figure(figsize=(7, 5))
    plt.scatter(age, cost, c=smoker, cmap="coolwarm")
    plt.title("Medical Cost vs Age")
    plt.xlabel("Age")
    plt.ylabel("Annual medical cost")
    print(f"saved plot: {save_and_close('cost_vs_age.png')}")
    # The scatter plot shows two visible bands: smokers tend to have much higher
    # costs than non-smokers at similar ages. This suggests smoker status is an
    # important feature and that age alone will miss a major part of the pattern.

    # Q2
    print("\nLinear Regression Q2: Train/test split with age only")
    X_age = age.reshape(-1, 1)
    X_train, X_test, y_train, y_test = train_test_split(
        X_age,
        cost,
        test_size=0.2,
        random_state=42,
    )
    print(f"X_train shape: {X_train.shape}")
    print(f"X_test shape:  {X_test.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"y_test shape:  {y_test.shape}")

    # Q3
    print("\nLinear Regression Q3: Age-only model")
    age_model = LinearRegression()
    age_model.fit(X_train, y_train)
    y_pred_age = age_model.predict(X_test)
    age_rmse = np.sqrt(np.mean((y_pred_age - y_test) ** 2))
    age_r2 = age_model.score(X_test, y_test)

    print(f"slope: {age_model.coef_[0]:.2f}")
    print(f"intercept: {age_model.intercept_:.2f}")
    print(f"RMSE: {age_rmse:.2f}")
    print(f"test R^2: {age_r2:.3f}")
    # The slope means the model estimates medical cost rises by about $197 for
    # each additional year of age when age is the only feature in the model.

    # Q4
    print("\nLinear Regression Q4: Age + smoker model")
    X_full = np.column_stack([age, smoker])
    X_train_full, X_test_full, y_train_full, y_test_full = train_test_split(
        X_full,
        cost,
        test_size=0.2,
        random_state=42,
    )
    model_full = LinearRegression()
    model_full.fit(X_train_full, y_train_full)
    y_pred_full = model_full.predict(X_test_full)
    full_r2 = model_full.score(X_test_full, y_test_full)
    full_rmse = np.sqrt(np.mean((y_pred_full - y_test_full) ** 2))

    print(f"age-only test R^2: {age_r2:.3f}")
    print(f"age + smoker test R^2: {full_r2:.3f}")
    print(f"age + smoker RMSE: {full_rmse:.2f}")
    print("age coefficient:    ", model_full.coef_[0])
    print("smoker coefficient: ", model_full.coef_[1])
    # Adding smoker helps a lot because it separates the two cost bands. The
    # smoker coefficient means smokers are estimated to cost about $14,538 more
    # per year than comparable non-smokers in this synthetic dataset.

    # Q5
    print("\nLinear Regression Q5: Predicted vs actual plot")
    plt.figure(figsize=(7, 5))
    plt.scatter(y_pred_full, y_test_full)
    min_value = min(y_pred_full.min(), y_test_full.min())
    max_value = max(y_pred_full.max(), y_test_full.max())
    plt.plot([min_value, max_value], [min_value, max_value], linestyle="--")
    plt.title("Predicted vs Actual")
    plt.xlabel("Predicted cost")
    plt.ylabel("Actual cost")
    exact_path = save_and_close("predicted_vs_actual.png")
    print(f"saved plot: {exact_path}")

    # Keep a non-overwritten warmup copy because project_02.py is also required
    # to save a plot named outputs/predicted_vs_actual.png.
    plt.figure(figsize=(7, 5))
    plt.scatter(y_pred_full, y_test_full)
    plt.plot([min_value, max_value], [min_value, max_value], linestyle="--")
    plt.title("Predicted vs Actual")
    plt.xlabel("Predicted cost")
    plt.ylabel("Actual cost")
    print(f"saved plot: {save_and_close('warmup_predicted_vs_actual.png')}")
    # A point above the diagonal means the true cost was higher than predicted,
    # so the model underpredicted. A point below the line means the model
    # overpredicted the true cost.


if __name__ == "__main__":
    main()
