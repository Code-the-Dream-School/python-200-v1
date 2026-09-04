# Week 3: Classification and Model Deployment

Welcome to Week 3 of Python 200! Last week you built regression models that predict a continuous number. This week you turn to *classification*, which predicts which category something belongs to. Is this email spam? Is this transaction fraud? Is today a good day for a run? Classification is one of the most common tasks in applied machine learning.

We continue with the same daily weather data you used last week. Last week you predicted the daily high temperature. This week you will build a classifier that predicts whether a day is **good for running**, based on the temperature, precipitation, and wind. You will build two kinds of classifier, learn how to measure whether a classifier is actually working, and then take the most important step for everything that follows: **save a trained model to disk so it can be loaded and used later.** That last skill is the bridge to the rest of the course. In Week 4 you will wrap the saved model in a reusable component, and in Week 10 a cloud pipeline will load it and make predictions on a schedule.

By the end of this week you will be able to:

- Prepare data for a classifier by scaling numeric features and encoding categorical ones, all inside a scikit-learn `Pipeline`
- Build k-Nearest Neighbors and Logistic Regression classifiers
- Evaluate a classifier with accuracy, precision, recall, F1, and the confusion matrix
- Save a trained model to disk with `joblib`, then load it in a separate script and predict

## Topics

1. [Preprocessing in a Pipeline](03_ML_classification/01_preprocessing.md)
Getting data ready for a classifier: scaling numeric features, one-hot encoding categorical features, and a little feature engineering. Then we bundle these steps into a scikit-learn `Pipeline` so that preprocessing and prediction travel together and no information leaks from the test set.

2. [Evaluating Classifiers](03_ML_classification/02_classifier_evaluation.md)
How do you tell whether a classifier is any good? We introduce the confusion matrix and the four core metrics -- accuracy, precision, recall, and F1 -- using a familiar real-world classifier, and connect them to the cost of different mistakes.

3. [k-Nearest Neighbors](03_ML_classification/03_knn.md)
Your first classifier. KNN classifies a new day by looking at the most similar days it has already seen. It is simple, which makes it a good place to see scaling, cross-validation, and the confusion matrix in action.

4. [Logistic Regression](03_ML_classification/04_logistic_regression.md)
A second classifier that draws one clean boundary between the classes and, unlike KNN, produces a probability for each prediction. Its coefficients are interpretable, which tells you *why* the model made a decision.

5. [Model Deployment with joblib](03_ML_classification/05_model_deployment.md)
The bridge to the rest of the course. Save a trained pipeline to disk, load it in a separate script, and use it to predict on new days. This is the exact step a cloud pipeline depends on.

6. [(Optional) Dimensionality Reduction with PCA](03_ML_classification/06_pca.md)
An optional lesson on Principal Component Analysis, a technique for compressing many correlated features into a few. You will use it again in Week 5 to visualize language-model embeddings.
