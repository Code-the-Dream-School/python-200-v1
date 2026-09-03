# Week 4: From Model to Reusable Component

Welcome to Week 4! Over the last two weeks you trained models and, in Week 3, saved one to disk. This week you take that saved model and turn it into a **reusable component**: a small, importable package with a clean interface, tests, and everything another program needs to use it without knowing how it was built.

This is the payoff of Week 1. In Week 1 you learned classes, dataclasses, type hints, docstrings, `pytest`, and packaging, using small examples. This week you apply all of it to something real: the weather classifier. By the end you will have a `weather_model` package that any script can import and call, which is exactly the shape of the component a cloud pipeline will load in Week 10.

Why does this matter? A trained model saved as a `.pkl` file is useful, but awkward to reuse. Every script that wants a prediction has to know where the file lives, load it correctly, prepare the input in exactly the right way, and interpret the raw output. If any of those details changes, every script breaks. A component hides those details behind a simple `predict()` method. Callers depend on the method, not on the mechanics. This is the difference between a model that works on your machine and a model a team can build a pipeline around.

By the end of this week you will be able to:

- Refactor a training-and-prediction script into a class with a clean `predict()` method
- Load a saved model once in `__init__` and reuse it for many predictions
- Add type hints, docstrings, and input validation so the component is safe and self-documenting
- Write `pytest` tests that cover both correct predictions and error handling
- Package the component so any script can import it

## Topics

1. [From Notebook to Component](04_applied_ML/01_from_notebook_to_component.md)
Why a saved model is not yet a reusable component, what a good interface looks like, and why tests are what make a refactor safe. This lesson frames the work of the week.

2. [Building the WeatherClassifier Class](04_applied_ML/02_the_classifier_class.md)
The core of the week. We write a `WeatherClassifier` class that loads the saved pipeline once in `__init__` and exposes a `predict()` method, returning a small `Prediction` dataclass. We add type hints, docstrings, and validation for bad input.

3. [Packaging and Testing the Component](04_applied_ML/03_packaging_and_testing.md)
We turn the class into an importable `weather_model` package, write a `pytest` suite covering predictions and error paths, and write a `predict_weather.py` script that uses it. This is the exact layout your Week 4 assignment and the Week 10 pipeline depend on.
