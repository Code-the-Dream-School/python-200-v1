# Week 2: Supervised Machine Learning — Regression

Welcome to Week 2 of Python 200! This week we begin machine learning: what it is, how it works, and how to put it into practice with scikit-learn, one of Python's most important machine learning libraries. By the end of the week you will have built and evaluated a linear regression model on real weather data.

Machine learning (ML) models are embedded in many pipelines that you will help build and maintain. Nonprofits predict food insecurity in a community, public health teams model disease spread, environmental organizations track deforestation from satellite imagery, and city governments route emergency resources after a disaster. In all of these cases, someone needs to build and maintain the pipelines that feed data into the models, monitor their outputs, and keep everything running reliably. That someone is often a data engineer. Understanding ML, meaning what models need, what their outputs mean, and how to evaluate whether they are working, makes you a far more effective collaborator and a more versatile engineer.

This week and next cover *classical* ML. It is still the most common approach in production systems, and it is the right place to build intuition before we move on to large language models in later weeks. This week focuses on **regression**, which predicts a continuous number. Next week covers **classification**, which predicts a category, and then saving a trained model to disk.

We use one dataset across the whole machine learning block: daily weather. You validated weather data in Week 1, you will regress on it this week, and you will build a classifier from it in Weeks 3 and 4.

> For an introduction to the course as a whole, and a discussion of how to set up your environment, please see the [Welcome](../README.md) page.

## Topics

1. [Introduction to machine learning](02_ML_intro/01_machine_learning.md)
A big-picture overview of the machine learning landscape: what machine learning is, how it relates to AI and deep learning, and the main types of learning (supervised, unsupervised, reinforcement).

2. [Introduction to scikit-learn](02_ML_intro/02_scikit_learn.md)
An introduction to scikit-learn, the most common library for classical ML in Python. We look at its `create → fit → predict` API and see it in action with a couple of short examples.

3. [Linear Regression](02_ML_intro/03_linear_regression.md)
Our first real ML model. We take a brief look at the features, then train a linear regression model on daily weather data, evaluate it with RMSE and R², and build intuition for what those metrics mean and how adding features changes the model.
