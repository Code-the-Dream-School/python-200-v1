# Preprocessing in a Pipeline

Machine learning algorithms expect data in a clean numerical format, but real datasets rarely arrive that way. *Preprocessing* is the work of turning raw data into something a model can learn from. This lesson covers the preprocessing you will use most often, and then shows how to bundle it into a scikit-learn `Pipeline` so that it travels with your model and does not leak information from the test set.

We will cover:

- Numeric and categorical features
- Scaling numeric features
- One-hot encoding categorical features
- A little feature engineering
- Putting preprocessing and the model together in a `Pipeline`

This assumes the data has already been cleaned, meaning missing values have been handled, using the techniques from Python for Data Analysis.

## Numeric and Categorical Features

Before we can train a classifier, we need to understand the kind of data we are giving it. Machine learning models only work with numbers, so every feature has to be represented numerically in the end.

**Numeric features** are already numbers, such as temperature, wind speed, age, or income. Models can use them directly, though many algorithms still need the numbers put on a similar scale first.

**Categorical features** describe a type or label rather than a quantity. They are often stored as strings, such as a season name, a city, or a shirt size. These values mean something to a person, but raw text is not useful to a model. We have to convert categories into numbers, which is what one-hot encoding does.

Our weather data has four numeric features (`temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `wind_speed_10m_max`) and, after a little feature engineering, one categorical feature (`season`). We will prepare both kinds.

## Scaling Numeric Features

Even when features are already numbers, we have to think about how large they are relative to each other. Many algorithms do not look at a feature in isolation. They compare features, and a feature measured in large units can drown out a feature measured in small ones.

Consider two features:

- `age`, ranging from about 18 to 70
- `income`, ranging from about 15,000 to 350,000

Both matter, but income varies over a much larger range of numbers. Any algorithm that measures distances between data points, such as k-Nearest Neighbors, will let income dominate the distance and will barely notice age, simply because income's numbers are larger. That is not a decision about which feature is more useful. It is an accident of the units.

Scaling puts numeric features on comparable footing. The most common method is **standardization**, which transforms each feature so that its mean becomes 0 and its standard deviation becomes 1.

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

The transformed values are called *z-scores*. A z-score tells you how many standard deviations a value is above or below the mean of its feature:

- A z-score of 0 means the value is right at the average.
- A z-score of 1 means it is one standard deviation above the average.
- A z-score of -2 means it is two standard deviations below the average.

After standardization, a negative value does not mean a negative temperature or a negative income. It means the value is below the average for that feature. Every feature now lives in the same z-score space and can be compared directly.

### When scaling matters

Scaling is important for algorithms that measure distances or that adjust weights through optimization, such as k-Nearest Neighbors and Logistic Regression, both of which you will build this week. Some models, such as tree-based models, are not sensitive to scale at all. When you are not sure, scaling is the safe default. It rarely hurts, and for distance-based models it often helps a great deal.

### Scaling without leaking the test set

There is one detail that matters more than it first appears. In a real workflow you split the data into training and test sets, and you fit the scaler **only on the training data**.

```python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # learn mean and std from training data only
X_test_scaled  = scaler.transform(X_test)        # apply the same scaling to the test data
```

The reason is subtle but important. The scaler learns two numbers from the data: the mean and the standard deviation of each feature. If you fit it on all the data, those numbers are influenced by the test set. When you later evaluate on the test set, the model has indirectly seen it, and your results look better than they truly are. This mistake is called *data leakage*.

By fitting on the training data only, the test set stays genuinely unseen, which gives you an honest measure of how the model would perform on new data. Keeping this ordering correct by hand is easy to get wrong, and later in this lesson the `Pipeline` will handle it for you automatically.

## One-Hot Encoding Categorical Features

A categorical feature such as `season` has values like `"winter"`, `"spring"`, `"summer"`, and `"fall"`. A model cannot use those strings directly, and we cannot simply number them:

```text
winter -> 1
spring -> 2
summer -> 3
fall   -> 4
```

If we did this, the model would treat `fall` (4) as larger than `winter` (1), and it would treat the distance from winter to spring as smaller than the distance from winter to fall. Those numbers invent an order and a distance that do not exist. The seasons have no natural numeric order.

**One-hot encoding** avoids this. It replaces the single column with one new column per category. Each row has a 1 in the column for its category and a 0 everywhere else:

```text
winter -> [1, 0, 0, 0]
spring -> [0, 1, 0, 0]
summer -> [0, 0, 1, 0]
fall   -> [0, 0, 0, 1]
```

No category is treated as larger than another, and no false distances are introduced. scikit-learn provides `OneHotEncoder` for this:

```python
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(sparse_output=False)

seasons = [["winter"], ["spring"], ["summer"], ["fall"]]
encoded = encoder.fit_transform(seasons)
print(encoder.categories_[0])
print(encoded)
```

The encoder sorts the categories alphabetically, so the four columns are `fall`, `spring`, `summer`, `winter`, in that order. Each row has a single 1 in the column for its season:

```text
['fall' 'spring' 'summer' 'winter']
[[0. 0. 0. 1.]
 [0. 1. 0. 0.]
 [0. 0. 1. 0.]
 [1. 0. 0. 0.]]
```

One thing to keep in mind is that one-hot encoding increases the number of columns. A feature with N categories becomes N columns. This is fine for a feature with a few categories, such as season. It becomes a problem for a feature with thousands of categories, such as a ZIP code, where one-hot encoding would create thousands of columns. For those cases there are other techniques, such as the embeddings you will meet in the AI lessons.

> A binary feature that is already stored as 0 and 1 does not need one-hot encoding. The values 0 and 1 are already a perfectly good numeric representation. You saw this last week with the `is_summer` feature.

## A Little Feature Engineering

Sometimes the most useful feature is not one that came with the data, but one you create from it. This is called *feature engineering*, and it can make patterns easier for a model to learn.

Our weather data does not include a `season` column, but it includes a date, and the season is inside the date. We can extract it:

```python
import pandas as pd

def month_to_season(month: int) -> str:
    """Map a month number (1-12) to a season name."""
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "fall"


df["season"] = df["date"].dt.month.map(month_to_season)
```

That is a small example of the three most common feature-engineering moves:

- **Extracting** part of a value, such as pulling the month or the season out of a date.
- **Combining** two features into a more meaningful one, such as dividing weight by height squared to get a body-mass index.
- **Binning** a numeric feature into groups, such as turning an exact age into an age range, when the group matters more than the precise number.

Feature engineering is a creative part of machine learning. Good features usually come from understanding the data and the real-world problem behind it. There is no fixed checklist. You get better at it by exploring your data and testing whether a new feature actually improves the model.

## Putting It Together: The Pipeline

So far we have three separate steps: scale the numeric features, one-hot encode the categorical feature, and then fit a model. Doing these by hand means keeping several arrays and several fitted objects in sync, applying each transformation to the training set and then to the test set in the right order. It is easy to forget a step, apply one out of order, or accidentally fit a scaler on the test data.

A scikit-learn **`Pipeline`** solves this. A pipeline is a sequence of steps where the output of each step becomes the input to the next. You define it once, and then it behaves like a single model.

Because our data has both numeric and categorical features that need *different* preprocessing, we first use a **`ColumnTransformer`**. It applies one transformation to some columns and a different transformation to others.

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

numeric_features = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"]
categorical_features = ["season"]

preprocess = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ]
)

model = Pipeline(
    steps=[
        ("preprocess", preprocess),
        ("classifier", LogisticRegression(max_iter=1000)),
    ]
)
```

Read the structure from the inside out. The `ColumnTransformer` scales the four numeric columns and one-hot encodes the one categorical column. The `Pipeline` runs that preprocessing and then hands the result to the classifier. Each step is a `("name", object)` pair, where the name is a label you choose.

Now the whole thing behaves like one model:

```python
model.fit(X_train, y_train)      # fits the scaler, the encoder, AND the classifier
predictions = model.predict(X_test)   # applies the same preprocessing, then predicts
```

When you call `model.fit(X_train, y_train)`, the pipeline fits the scaler and the encoder on the training data only, transforms it, and fits the classifier on the result. When you call `model.predict(X_test)`, it applies the *same* scaling and encoding, learned from the training data, to the test data before predicting.

This gives you three real benefits:

1. **No leakage.** The preprocessing is fit on the training data only, automatically, every time. You cannot accidentally fit a scaler on the test set.
2. **One object.** The preprocessing and the model are a single unit. In the deployment lesson you will save this whole pipeline to one file. When it is loaded later, the scaling and encoding come with it, so raw data can be passed straight in.
3. **Less to get wrong.** There are no intermediate arrays to keep track of and no chance of applying steps out of order.

`handle_unknown="ignore"` in the encoder tells it what to do if a category it never saw during training appears later, such as a season name with a typo. Rather than raising an error, it encodes the unknown value as all zeros. This keeps a deployed model from crashing on unexpected input.

You will use this pipeline structure for both classifiers this week, and the pipeline is exactly what you will save to disk and reuse in Weeks 4 and 10.

## Summary

Good machine learning starts with good data preparation. Numeric features usually need scaling so that no feature dominates just because of its units. Categorical features need one-hot encoding so that the model does not read a false order into them. Feature engineering can create new features that make patterns easier to learn. Finally, a `Pipeline` with a `ColumnTransformer` bundles all of this preprocessing together with the model into a single object that fits on the training data only, applies the same steps at prediction time, and can be saved and reused as one unit.

## Check for Understanding

1. Which of the following are *categorical* features?

    a. wind speed
    b. shirt size ("S", "M", "L")
    c. temperature
    d. season name

    <details>
    <summary>Show Answer</summary>
    b and d -- both describe a type or label rather than a quantity. Wind speed and temperature are numeric.
    </details>

2. Why do we fit a `StandardScaler` on the training data only?

    a. It makes training faster
    b. Fitting on all the data lets information from the test set influence the scaling, which is data leakage and makes evaluation look better than it really is
    c. The test set does not need to be scaled
    d. It is required by scikit-learn

    <details>
    <summary>Show Answer</summary>
    b -- the scaler learns the mean and standard deviation. If it learns them from all the data, the test set has influenced the model indirectly, and the evaluation is no longer honest.
    </details>

3. Why do we one-hot encode `season` instead of numbering the seasons 1 to 4?

    a. Numbers train faster than strings
    b. Numbering invents an order and distances between seasons that do not exist; one-hot encoding avoids that
    c. scikit-learn cannot store strings
    d. One-hot encoding uses less memory

    <details>
    <summary>Show Answer</summary>
    b -- numbering the seasons would tell the model that fall (4) is greater than winter (1), and that some seasons are closer together than others. One-hot encoding represents each season without any false order.
    </details>

4. What does wrapping preprocessing and the model in a `Pipeline` give you?

    a. A higher accuracy score
    b. A single object that fits preprocessing on the training data only, applies the same steps at prediction time, and can be saved and reused as one unit
    c. Automatic feature engineering
    d. A model that does not need training

    <details>
    <summary>Show Answer</summary>
    b -- the pipeline prevents leakage, keeps preprocessing and the model together, and gives you one object to save and load, which is exactly what deployment needs.
    </details>
