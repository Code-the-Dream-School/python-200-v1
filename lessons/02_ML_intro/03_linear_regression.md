# Linear Regression

For a helpful overview before you begin: [Linear Regression explained (YouTube)](https://www.youtube.com/watch?v=ukZn2RJb7TU)

Earlier this week you saw the scikit-learn `create → fit → predict` workflow. This lesson uses that workflow to build your first real model. The focus is *regression*, which is the kind of machine learning problem where the goal is to predict a continuous number.

We will build a regression model step by step using daily weather data. This is the same kind of weather data you validated in Week 1, and it is the data you will train a classifier on in Week 3. We start with a single predictor and add more, so you can see how the model grows.

## What is a Regression Model?

A regression model predicts a *continuous value*. A continuous value is a number that can fall anywhere in a range, such as a price, a temperature, or a duration. The answer is a number rather than a category, and that is what separates regression from classification, which you will study in Week 3.

Our target this week is the daily high temperature. Given a few measurements about a day, we want to predict how warm it will get.

## The Intuition Behind Regression

Suppose you want to predict a day's high temperature. One useful clue is that day's low temperature. Cold nights tend to lead to cold days, and mild nights tend to lead to milder days.

<img src="resources/1_week2_Regression_Model.jpg" alt="Regression Model" width="350">

Imagine plotting your data with the daily low on the x-axis and the daily high on the y-axis. Each day becomes one point in that scatter plot, and you will usually see a trend: higher lows tend to go with higher highs. The goal of linear regression is to draw a straight line through that cloud of points that best captures the trend. That line lets you answer a question like "if the low was 10 degrees, what high should we expect?"

The *steepness* of the line, which is called the slope, tells you how much the predicted high rises for each additional degree of the low. scikit-learn finds that line for you.

## Fitting a Line Through Points

The `create → fit → predict` workflow works the same way for regression. We will see it first with a minimal example before moving to a fuller dataset.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

rng = np.random.default_rng(42)
temp_min = np.linspace(-5, 22, 50).reshape(-1, 1)
temp_max = 1.0 * temp_min.ravel() + 6 + rng.normal(0, 1.5, 50)

model = LinearRegression()          # 1. create
model.fit(temp_min, temp_max)       # 2. fit
predicted = model.predict(temp_min) # 3. predict

print("Slope:", model.coef_[0])
print("Intercept:", model.intercept_)

plt.scatter(temp_min, temp_max, color="blue", alpha=0.5, label="Data")
plt.plot(temp_min, predicted, color="red", label="Linear fit")
plt.xlabel("Daily low (C)")
plt.ylabel("Daily high (C)")
plt.legend()
plt.show()
```

<img src="resources/3_week2_fitting_a_line_through_points.jpg" alt="fitting a line through points" width="350">

Each blue dot is one day, and the red line is what the model learned. The slope should come out close to 1.0, which is the true relationship we built into the data. Even with noise added, the model recovers the trend. That is the core idea: linear regression finds the straight line that best describes the relationship between an input and an output.

Now we will apply this to a fuller dataset and introduce the tools you need to evaluate a model properly.

## Working with a Daily Weather Dataset

We will use a dataset of 500 days with five columns:

- `temp_min` -- the daily low temperature in degrees Celsius.
- `precipitation` -- total precipitation for the day in millimeters.
- `wind_speed` -- the maximum wind speed for the day in km/h.
- `is_summer` -- 1 if the day is in summer, 0 otherwise.
- `temp_max` -- the daily high temperature in degrees Celsius. This is our prediction target.

This dataset was generated with a known structure so that the numbers stay interpretable while you learn. In the Week 2 assignment you will download real daily weather from a live API and run the same workflow on it. Load the file and take a first look.

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

df = pd.read_csv("resources/weather_daily.csv")
print(df.head())
print(df.describe())
```

`df.describe()` shows you the range of each column and confirms there are no missing values. Both are worth checking before you model anything.

## A First Look at the Features

Before fitting a model, it is worth asking which features actually relate to the target. A quick way to check is the correlation between each feature and `temp_max`.

```python
print(df.corr(numeric_only=True)["temp_max"].sort_values())
```

You will see something close to this:

```text
precipitation   -0.098
wind_speed      -0.060
is_summer        0.192
temp_min         0.960
temp_max         1.000
```

Correlation measures how strongly two columns move together, on a scale from -1 to 1. Here `temp_min` has a very strong positive correlation with `temp_max` (0.96), which matches the intuition that cold nights go with cold days. The other three features look weak on their own. Keep that observation in mind, because one of them will turn out to be useful anyway once the model accounts for `temp_min`. This is a short feature check, not a full analysis, and it is enough to tell us where to start.

## Simple Linear Regression: temp_min to temp_max

We start with the simplest case, a single predictor. We will predict `temp_max` from `temp_min` alone. The model learns one equation:

temp_max = slope × temp_min + intercept

### Define features and target

```python
X = df[["temp_min"]]   # 2D: scikit-learn expects features as a DataFrame or 2D array
y = df["temp_max"]
```

### Train-test split

Before we fit anything, we need to talk about evaluation. When we train a model, we want to know how well it performs on *new* data, meaning data it has never seen. Without that check, we cannot tell whether the model has learned the real pattern or has only memorized the training examples.

Think of it like studying for an exam. You practice on notes and homework, which is the *training*. Then the exam tests you on questions you have not seen before, which is the *testing*. In machine learning we simulate this by splitting the dataset into two parts before training. The *training set* is what the model learns from. The *test set* is held aside to check how well the model generalizes. We will use 80% of the data for training and 20% for testing.

scikit-learn has a built-in tool for splitting data into training and test subsets. This is an important idea that you will use throughout machine learning.

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

`random_state=42` makes the split repeatable, so you get the same assignment of rows every time you run the code.

Create the model, fit it on the training data, and predict values for the test data:

```python
model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
```

Inspect the learned parameters:

```python
print("Slope:", model.coef_[0])
print("Intercept:", model.intercept_)
```

The *slope* is the most important number here. It tells you how much the predicted high rises for each additional degree of the low. With this dataset the slope comes out close to 1.0, which means the model predicts that the daily high rises by about one degree for each degree the low rises.

The *intercept* comes out around 5.5. It is the predicted high when the low is 0, which is a plausible early-spring day. The intercept is always required to define a line, though it is not always meaningful on its own.

### Evaluate: RMSE and R²

Fitting produced the best-fitting line, but how do we tell how *good* the model is? Two measures are common in regression: RMSE and R². For the reason stated above, we compute them on the test data, which the model was not trained on.

```python
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("RMSE:", rmse)
print("R²:", r2)
```

#### Root Mean Squared Error (RMSE)

The most natural question to ask is how far off the predictions are. For each day in the test set, we can compute the difference between the predicted high and the actual high.

Image from Geeks for Geeks:
<img src="resources/rmse.jpg" alt="evaluation metrics">

If we average those raw differences, positive and negative errors cancel out. A prediction that is 3 degrees too high and one that is 3 degrees too low would average to zero, which would make the model look perfect when it is not.

The standard fix is to square each error before averaging. Squaring does two things. It makes every error positive, and it penalizes large errors more heavily than small ones. A prediction that is 4 degrees off contributes four times as much as one that is 2 degrees off. This quantity is the *MSE*, or Mean Squared Error.

Squaring changes the units. If temperatures are in degrees Celsius, MSE ends up in degrees squared, which is not intuitive to report.

To fix the units, we take the square root of MSE. The result is *RMSE*, or Root Mean Squared Error:

$$
\text{RMSE} = \sqrt{\text{MSE}}
$$

RMSE keeps the heavier penalty for large errors and returns the result to the original units. The interpretation is direct. With the low temperature as the only predictor, this model's RMSE comes out around 2.3 degrees, which means predictions are typically off by a little more than 2 degrees. That is a number you can reason about, and it tells you there is variation in the daily high that the low alone cannot explain. That gap is what motivates adding more features.

#### R²

R² answers a different question. How much better is the model than simply predicting the mean high every time, which is the baseline? It is defined as:

$$
R^2 = 1 - \frac{\text{Model MSE}}{\text{Baseline MSE}}
$$

An R² of 1.0 means perfect predictions. An R² of 0.0 means the model does no better than guessing the mean. With the low temperature as the only predictor, R² comes out around 0.92, which is high because the low is such a strong clue to the high.

Despite the name, R² is *not* defined as a mathematical square. It is one minus a ratio of errors. That is why R² can be negative. If the model performs worse than predicting the mean on test data, which can happen when a model has overfit the training set, the ratio exceeds 1.0 and R² drops below zero.

> On *training* data, R² is always at least 0, because the fitted line is guaranteed to do at least as well as predicting the average.

#### Connecting R² to correlation

There is a direct connection between R² and the correlation you looked at earlier. In simple linear regression with one feature, R² is close to the square of the correlation between that feature and the target. You can check it directly:

```python
corr_coeff = df["temp_min"].corr(df["temp_max"])
print("Correlation coefficient:", corr_coeff)
print("Correlation coefficient squared:", corr_coeff ** 2)
```

The correlation is about 0.96, so its square is about 0.92, which is close to the R² you computed above. The two values are not identical, because R² here was measured on the test set while the correlation used the whole dataset, but they are close. This is the numerical link between a single feature's correlation and a one-feature model's fit.

## Adding Precipitation and Wind

Everything we just did, meaning the split, the fit, and the evaluation, used a single column. `X` was a (500, 1) array of 500 days with one feature each. What happens if we add more columns?

We pass `X` with more columns, and the *same* `LinearRegression()` model, the *same* `.fit()` call, and the *same* evaluation code all work without any change. scikit-learn detects that there are now several features and adapts. You do not change a single line of the training or evaluation code.

What changes is the geometry. With one feature the model fits a straight line in two dimensions. With two features it fits a *plane* in three dimensions. With more features it fits a hyperplane, which is the same idea in higher dimensions. The equation is still only multiplication and addition:

temp_max = b1 × temp_min + b2 × precipitation + b3 × wind_speed + c

There are no curves. The model is still *linear*, which means the prediction is a sum of each feature times its coefficient. This same approach scales to 10 features or 100 features with the same code. That is one reason linear regression remains one of the most widely used tools in data science.

Rain and wind both tend to come with cooler days, so we expect both coefficients to be negative.

```python
X_multi = df[["temp_min", "precipitation", "wind_speed"]]

X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(
    X_multi, y, test_size=0.2, random_state=42
)

model_multi = LinearRegression()
model_multi.fit(X_train_m, y_train_m)

print("R²:", model_multi.score(X_test_m, y_test_m))
print("temp_min coefficient:     ", model_multi.coef_[0])
print("precipitation coefficient:", model_multi.coef_[1])
print("wind_speed coefficient:   ", model_multi.coef_[2])
```

The R² rises to about 0.94, up from 0.92, and RMSE falls to about 2.0 degrees. Both coefficients for precipitation and wind are negative, as expected: about -0.5 for precipitation and about -0.05 for wind. The `temp_min` coefficient tells you how much the high rises per degree of the low while holding precipitation and wind constant. The precipitation coefficient tells you how much the high drops per millimeter of rain while holding the other two constant.

This is the central idea of multiple regression. Each coefficient describes one feature's relationship with the outcome while the model accounts for all the others.

## Adding a Binary Feature: is_summer

Our dataset also records whether a day is in summer. This is a categorical feature stored as 0 or 1. Binary variables fit into linear regression directly, with no special encoding. The coefficient for a binary variable is the shift in the predicted outcome when the variable goes from 0 to 1, with all other features held constant.

Our new model is:

temp_max = b1 × temp_min + b2 × precipitation + b3 × wind_speed + b4 × is_summer + c

```python
X_multi2 = df[["temp_min", "precipitation", "wind_speed", "is_summer"]]

X_train_m2, X_test_m2, y_train_m2, y_test_m2 = train_test_split(
    X_multi2, y, test_size=0.2, random_state=42
)

model_multi2 = LinearRegression()
model_multi2.fit(X_train_m2, y_train_m2)

print("R²:", model_multi2.score(X_test_m2, y_test_m2))
print("temp_min coefficient:     ", model_multi2.coef_[0])
print("precipitation coefficient:", model_multi2.coef_[1])
print("wind_speed coefficient:   ", model_multi2.coef_[2])
print("is_summer coefficient:    ", model_multi2.coef_[3])
```

The `is_summer` coefficient comes out around 3.0. The model predicts that a summer day is about 3 degrees warmer than a non-summer day with the same low, rain, and wind. R² rises again to about 0.96, and RMSE falls to about 1.6 degrees.

This result is worth pausing on. Look back at the correlation table. On its own, `is_summer` had a weak correlation with `temp_max`, only about 0.19. Yet in the full model it has a clear, useful coefficient. The reason is that summer's effect on the high is partly hidden by the low temperature, which already carries most of the seasonal signal. Once the model holds `temp_min` constant, the extra warmth of a summer day stands out. A feature can look weak on its own and still be useful once the other features are accounted for.

Each time we added features, the test R² improved and RMSE fell. That improvement on held-out data is the practical signal that a feature is worth keeping. If you were taking this model into production, these are the features you would keep.

## On Overfitting

Overfitting happens when a model learns the training data *too* well, so well that it memorizes the noise instead of the underlying pattern. The image below shows what this looks like. With too little flexibility (left panel), the model misses the real trend. With the right amount (middle), it captures the trend without following every fluctuation. With too much flexibility (right), the curve bends to pass near every training point, but that curve reflects noise, not the real pattern.

<img src="resources/7_week2_Overfitting_and_Underfitting.jpg" alt="Underfitting, good fit, and overfitting illustrated">

The key diagnostic is the gap between train R² and test R². A model that has overfit scores well on training data and poorly on new data. The larger the gap, the worse the overfit.

To see this clearly, we can use a small synthetic dataset where overfitting is easy to produce. With only 30 points and a degree-10 polynomial, which adds 10 columns of features (x, x², x³, and so on up to x¹⁰), the model has far more flexibility than the data can support.

```python
from sklearn.preprocessing import PolynomialFeatures

np.random.seed(0)
n = 30
X_demo = np.sort(np.random.uniform(0, 10, n)).reshape(-1, 1)
y_demo = 2 * X_demo.ravel() + np.random.normal(0, 3, n)

X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(
    X_demo, y_demo, test_size=0.3, random_state=42
)

model_lin = LinearRegression().fit(X_train_d, y_train_d)

poly = PolynomialFeatures(degree=10, include_bias=False)
X_poly_d = poly.fit_transform(X_demo)
X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(
    X_poly_d, y_demo, test_size=0.3, random_state=42
)
model_poly = LinearRegression().fit(X_train_p, y_train_p)

print("Linear    -- Train R²:", model_lin.score(X_train_d, y_train_d))
print("Linear    -- Test R²: ", model_lin.score(X_test_d, y_test_d))
print("Degree-10 -- Train R²:", model_poly.score(X_train_p, y_train_p))
print("Degree-10 -- Test R²: ", model_poly.score(X_test_p, y_test_p))
```

Your output will look something like this:

```text
Linear    -- Train R²: 0.66
Linear    -- Test R²:  0.67
Degree-10 -- Train R²: 0.76
Degree-10 -- Test R²: -2.16
```

The linear model shows a small, healthy gap. Train and test R² are nearly identical (0.66 and 0.67), which means the model generalizes well. The degree-10 model trains better (0.76 against 0.66), but it collapses on the test set, where R² is -2.16.

A negative R² means the degree-10 model is much worse than simply predicting the mean for every point. It has memorized the specific wiggles of the training data so precisely that its predictions on new data are actively harmful. This is an extreme case of overfitting. More often, overfitting just means the test R² drops noticeably below the training R².

The goal is a model with the right level of complexity: expressive enough to capture the real trend, but not so flexible that it memorizes noise. Comparing train R² and test R² is your first and most useful diagnostic.

Linear models are often the first model people use, precisely because they are simple. A line or a plane does not have enough flexibility to memorize noise, which makes it naturally resistant to overfitting. More powerful models give you more flexibility, but they also require more caution.

## Pulling It Together

It is worth consolidating what we have built.

"Linear" in linear regression means the prediction is a *linear combination* of the features. Each feature is multiplied by its coefficient, and the results are summed. A model with ten features is still linear regression. The surface it fits is a hyperplane in ten dimensions instead of a line in two.

R² measures the fraction of variation in the target that the model explains, regardless of how many features are in the model. With one feature it is close to the square of the correlation between that feature and the target. With several features that clean connection no longer holds, but R² remains a useful summary of overall fit.

Correlation is a *pairwise* measure. It describes the relationship between exactly two columns. Multiple regression brings all the features together at once and estimates each feature's relationship with the target after accounting for the others. That is why a feature such as `is_summer` can look weakly correlated with the target on its own and still be a useful predictor in the full model.

Each coefficient in multiple regression reflects the relationship between that feature and the outcome while holding all other features constant. This idea of controlling for the other variables is what separates multiple regression from looking at pairwise correlations one at a time.

## Key Takeaways

Linear regression predicts continuous values by fitting a line (with one feature) or a plane or hyperplane (with several features) through the data. MSE and RMSE measure the size of prediction errors, and RMSE reports them in the original units. R² measures how much better the model does than simply predicting the mean. As you add predictors, each coefficient describes one feature's relationship with the outcome while holding the others constant, which is the central idea of multiple regression.

## Check for Understanding

1. What does R² measure?

    a. The slope of the regression line
    b. How much variation in the target the model explains compared to predicting the mean
    c. The number of data points
    d. The size of the largest error

    <details>
    <summary>Show Answer</summary>
    b -- R² measures how much better the model performs compared to always predicting the mean target value.
    </details>

2. Why can R² be negative when evaluated on test data?

    a. Because the correlation can be negative
    b. Because R² is defined as error reduction relative to a baseline, not as a mathematical square
    c. Because the dataset is too small
    d. Because the slope is negative

    <details>
    <summary>Show Answer</summary>
    b -- R² is defined as 1 minus (model error / baseline error). If the model performs worse than predicting the mean on test data, this ratio exceeds 1.0 and R² drops below zero.
    </details>

3. What changes conceptually when we add a second feature to a regression model?

    a. The model fits a plane instead of a line, and each coefficient reflects a partial relationship
    b. R² is no longer a valid metric
    c. The model requires a different algorithm
    d. The train-test split is no longer needed

    <details>
    <summary>Show Answer</summary>
    a -- Multiple regression extends the model to higher dimensions. Each coefficient reflects the relationship between one feature and the outcome while holding all other features constant.
    </details>

4. In the full model, `is_summer` has a coefficient near 3.0, even though its correlation with `temp_max` was only about 0.19. What does this show?

    a. The model made a mistake
    b. A feature can look weak on its own and still be useful once the model accounts for the other features
    c. Correlation and coefficients always agree
    d. `is_summer` should be removed from the model

    <details>
    <summary>Show Answer</summary>
    b -- On its own, summer's effect is largely masked by the daily low, which carries most of the seasonal signal. Once the model holds `temp_min` constant, the extra warmth of a summer day becomes clear. This is the difference between a pairwise correlation and a coefficient in a multi-feature model.
    </details>
