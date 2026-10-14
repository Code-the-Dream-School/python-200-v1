# Task 1: Fetch the Data
# I have chosen Bishkek city, that is located in Kyrgyzstan

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 42.87,
    "longitude": 74.59,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "wind_speed_10m_max",
    ],
    "timezone": "Asia/Bishkek",
}
response = requests.get(url, params=params)
response.raise_for_status()
df = pd.DataFrame(response.json()["daily"])
df["date"] = pd.to_datetime(df["time"])
df = df.drop("time", axis=1)

print("Dataset shape:", df.shape)
print("First five rows:")
print(df.head())


# Task 2: Look at the Features
print(df.describe())
print("\nMissing values per column:")
print(df.isna().sum())
# The dataset contains no missing values

# Print the correlation of each numeric column with temperature_2m_max
print(df.corr(numeric_only=True)["temperature_2m_max"].sort_values())
# The daily low has the strongest correlation with the daily high

# Create at least one plot that helps you understand the data
plt.scatter( df["temperature_2m_min"], df["temperature_2m_max"], color="blue", alpha=0.5)
plt.xlabel("Daily low (C)")
plt.ylabel("Daily high (C)")
plt.title("Daily Low vs. Daily High in Bishkek (2025)")
plt.tight_layout()
plt.savefig("assignments_02/outputs/low_vs_high.png")
plt.show()

# The plot shows a strong positive relationship: days with higher minimum temperatures generally also have higher maximum temperatures


# Task 3: Engineer a Feature
# Add a binary is_summer column: 1 if the month is June, July, or August, and 0 otherwise
df["is_summer"] = df["date"].dt.month.isin([6, 7, 8]).astype(int)

print(df["is_summer"].value_counts())

# I expect is_summer to help predict the daily high because summer days generally have higher maximum temperatures than other seasons, even when the daily minimum temperatures are similar.


# Task 4: Baseline Model
# Define features and target
X = df[["temperature_2m_min"]]
y = df["temperature_2m_max"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create a model
model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Evaluate RMSE and R2
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("Slope: ", model.coef_[0])
print("RMSE: ", rmse)
print("R2: ", r2)

# The RMSE is about 3.96°C, meaning the model's prediction errors are typically on the scale of about 4°C


# Task 5: Full Model
feature_cols = ["temperature_2m_min", "precipitation_sum",
                "wind_speed_10m_max", "is_summer"]
X_multi = df[feature_cols].values
y = df["temperature_2m_max"].values

X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(
    X_multi, y, test_size=0.2, random_state=42
)

model_multi = LinearRegression()
model_multi.fit(X_train_m, y_train_m)
y_pred_m = model_multi.predict(X_test_m)

rmse_m = np.sqrt(mean_squared_error(y_test_m, y_pred_m))

print("Train R2: ", model_multi.score(X_train_m, y_train_m))
print("Test R2: ", model_multi.score(X_test_m, y_test_m))
print("RMSE: ", rmse_m)

# Each feature name with its coefficient:
for name, coef in zip(feature_cols, model_multi.coef_):
    print(f"{name:22s}: {coef:+.3f}")

# The daily minimum temperature has the strongest positive coefficient. Precipitation has a negative coefficient, while wind speed has a very small positive coefficient. The negative summer coefficient is surprising, but it represents the effect of summer after accounting for the other features, not the overall seasonal effect.

# Train R² (0.927) is higher than test R² (0.891), a gap of about 0.036. This suggests the model fits the training data better than unseen data. The gap is moderate, but the full model does not improve test performance compared with the simpler baseline model.



# Task 6: Evaluate and Summarize
# Predicted vs actual plot for your full model on the test set

plt.scatter(y_pred_m, y_test_m, alpha=0.7)

min_value = min(y_pred_m.min(), y_test_m.min())
max_value = max(y_pred_m.max(), y_test_m.max())
plt.plot([min_value, max_value], [min_value, max_value], "r--")

plt.title("Predicted vs Actual (Full Model)")
plt.xlabel("Predicted daily high (°C)")
plt.ylabel("Actual daily high (°C)")

plt.tight_layout()
plt.savefig("assignments_02/outputs/predicted_vs_actual_high.png")
plt.show()

# Plot observation:
# The model seems to struggle slightly more at the high end

# Summary:
# The dataset contains 365 daily observations, and the test set contains 73 observations (20% of the dataset).

# The full model has an RMSE of about 3.98°C, meaning its prediction errors are on the scale of about 4°C. Its test R² is about 0.891, so it explains about 89.1% of the variation in daily high temperatures in the test set.

# Daily minimum temperature has the largest effect on the predicted high: its coefficient is +1.169, so higher daily lows predict higher daily highs.

# One surprising result is that adding precipitation, wind speed, and the summer indicator did not improve test performance compared with the baseline model that uses only daily minimum temperature.







