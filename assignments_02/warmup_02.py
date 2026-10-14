# --- scikit-learn API ---
# Q1
import numpy as np
from sklearn.linear_model import LinearRegression

temp_min = np.array([1, 4, 8, 12, 16, 20]).reshape(-1, 1)
temp_max = np.array([8, 10, 15, 18, 23, 27])
new_temp_min = np.array([6, 18]).reshape(-1, 1)

model = LinearRegression()
model.fit(temp_min, temp_max)
temp_max_predicted = model.predict(new_temp_min)
print("Predicted high when low is 6°C:", temp_max_predicted[0])
print("Predicted high when low is 18°C:", temp_max_predicted[1])
print("The slope is: ", model.coef_[0])
print("The intercept is: ", model.intercept_)


# Q2 
x = np.array([10, 20, 30, 40, 50])
print(x.shape)
X = np.array([10, 20, 30, 40, 50]).reshape(-1, 1)
print(X.shape)

# scikit-learn expects X to be 2D, with rows representing samples and columns representing features. Here we have 5 samples and 1 feature


# --- scikit-learn API ---
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

rng = np.random.default_rng(42)
num_days  = 120
temp_min  = rng.uniform(-5, 22, num_days)
is_rainy  = rng.integers(0, 2, num_days).astype(float)
temp_max  = 1.0 * temp_min + 6 - 4 * is_rainy + rng.normal(0, 2, num_days)


# Q1
# Create a scatter plot of temp_min on the x-axis and temp_max on the y-axis. Color the points by rain status by passing c=is_rainy and cmap="coolwarm" to plt.scatter()
plt.scatter(temp_min, temp_max, c=is_rainy, cmap="coolwarm")
plt.title("Daily High vs Low")
plt.xlabel("Minimal temperature")
plt.ylabel("Maximum temperature")

plt.tight_layout()
plt.savefig("assignments_02/outputs/high_vs_low.png")
plt.show()

# The two groups are clearly visible and distinct. he colors represent dry and rainy days, suggesting that rain status affects the daily high: rainy days tend to have a lower high temperature than dry days. 


# Q2
# Split the data into training and test sets using temp_min as the only feature, an 80/20 split, and random_state=42
X = temp_min.reshape(-1, 1)
y = temp_max

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)
print("y_train shape:", y_train.shape)
print("y_test shape:", y_test.shape)


# Q3
# Fit a LinearRegression model to your training data from Question 2. Print the slope and intercept
model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print("The slope is: ", model.coef_[0])
print("The intercept is: ", model.intercept_)
print("RMSE: ", np.sqrt(mean_squared_error(y_test, y_pred)))
print("R² on the test set: ", model.score(X_test, y_test))

# The slope is about 0.94, meaning that for each 1°C increase in the daily low, the model predicts an average increase of about 0.94°C in the daily high.


# Q4
# Now add is_rainy as a second feature and fit a new model
X_full = np.column_stack([temp_min, is_rainy])
X_train_f, X_test_f, y_train_f, y_test_f = train_test_split(
    X_full, y, test_size=0.2, random_state=42
)

model_full = LinearRegression()
model_full.fit(X_train_f, y_train_f)

print("R² on the full test set: ", model_full.score(X_test_f, y_test_f))
print("temp_min coefficient:", model_full.coef_[0])
print("is_rainy coefficient:", model_full.coef_[1])

# With is-rainy feature added, R2 improved from 0.89 to 0.94. The is_rainy coefficient represents the predicted difference in daily high between a rainy day and a dry day with the same daily low. A negative coefficient means rainy days tend to have lower highs.


# Q5
# A predicted vs actual plot
y_pred_full = model_full.predict(X_test_f)

plt.scatter(y_pred_full, y_test_f, alpha=0.7)

min_value = min(y_pred_full.min(), y_test_f.min())
max_value = max(y_pred_full.max(), y_test_f.max())
plt.plot([min_value, max_value], [min_value, max_value], "r--")

plt.title("Predicted vs Actual")
plt.xlabel("Predicted daily high (°C)")
plt.ylabel("Actual daily high (°C)")

plt.tight_layout()
plt.savefig("assignments_02/outputs/predicted_vs_actual_warmup.png")
plt.show()

# Points above the diagonal have actual values higher than predicted, meaning the model underestimated the daily high.Points below the diagonal have actual values lower than predicted, meaning the model overestimated the daily high.




