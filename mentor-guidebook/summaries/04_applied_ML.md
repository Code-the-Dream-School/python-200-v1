# Week 4 Mentor Summary: From Model to Reusable Component

**Lesson files:** `lessons/04_applied_ML.md` (overview) and three lessons in `lessons/04_applied_ML/`
**Assignment file:** `assignments/04_applied_ML.md`
**Answer key:** `mentor-guidebook/answer-key/assignment_04_key.md`
**Slides:** `mentor-guidebook/slides/04_applied_ML.pdf`

**Learning objective:** Students turn the weather classifier they saved in Week 3 into a reusable component. They write a `WeatherClassifier` class that loads the saved pipeline once and exposes a `predict()` method. They package it as `weather_model`, test it with `pytest`, and call it from a short script.

**Where this fits:** This week applies the Week 1 tools (classes, dataclasses, type hints, docstrings, `pytest`, and packaging) to the model students trained and saved in Week 3. In Week 10, a pipeline imports `WeatherClassifier` to classify rows from a cloud database. In Week 11, that step becomes part of a single orchestrated flow. Students need to keep their `weather_model/` and `models/` folders.

---

## Lesson Overview

The three lessons build one component, step by step. The demo model is a scaled logistic regression pipeline trained on the Week 3 dataset, `weather_classification.csv`, with four features: `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, and `wind_speed_10m_max`.

| Lesson | What students learn |
|---|---|
| **1. From Notebook to Component** | Why a saved `.pkl` file is awkward to reuse: every caller must know the file path, the feature order, that `1` means "good," and that the probability is in column 1. A component hides these details behind `predict()`. Loading the model once in `__init__` avoids reloading it for every prediction. Turning the Week 3 script into a component is a **refactor**, and tests make the refactor safe. |
| **2. Building the WeatherClassifier Class** | A `Prediction` dataclass with `label` and `probability`. An `__init__` that raises a clear `FileNotFoundError` before calling `joblib.load`. A `predict()` method that returns `[]` for empty input, raises a `ValueError` that names missing features, selects the features in a fixed order, and converts the model output into `Prediction` objects. Type hints and docstrings throughout. |
| **3. Packaging and Testing the Component** | The `weather_model/` package with `__init__.py` as the public entry point. An empty `conftest.py` at the project root so `pytest` can import the package. Seven tests that use a fixture to train a tiny model and save it to `tmp_path`, plus `pytest.raises(..., match=...)` for the error paths. A `predict_weather.py` script with a `main()` function under an `if __name__ == "__main__":` guard. |

---

## Assignment Deliverables

**Setup:** Students work in `assignments_04/`. They copy their Week 3 `weather_classifier.pkl` and `weather_classifier_metadata.json` into `assignments_04/models/` and create an empty `conftest.py` at the top of `assignments_04/`. They install `scikit-learn`, `joblib`, and `pytest` with `uv pip install`.

**Grading:** The grader runs `pytest` from inside `assignments_04/`. The test suite trains its own tiny model, so it should pass on any correct submission. The probabilities that `predict_weather.py` prints depend on each student's Week 3 model, so do not grade the numbers. Some names are exact, because the tests and the Week 10 pipeline import them: `weather_model`, `WeatherClassifier`, `Prediction`, `predict`, `label`, `probability`, and the four feature keys.

| Part | File | What students do | Concepts practiced |
|---|---|---|---|
| Warmup | `warmup_04.py` | Three exercises: a `ModelInfo` class that loads a JSON file in `__init__`, a `DayForecast` dataclass, and a `parse_temperature` function with two `pytest` tests. They run it with `pytest warmup_04.py -v`. | Week 1 classes, dataclasses, and `pytest` |
| Project, Tasks 1–2 | `weather_model/classifier.py` | Write the `Prediction` dataclass and the `WeatherClassifier` class with the validation and conversion rules from Lesson 2. | Classes, dataclasses, type hints, error handling |
| Project, Task 3 | `weather_model/__init__.py` | Re-export `WeatherClassifier` and `Prediction`, with an `__all__` list. | Packaging, public entry point |
| Project, Task 4 | `tests/test_classifier.py` | Write tests for all seven listed behaviors, in at least six test functions, using a `tmp_path` fixture, `match=` on the error tests, and at least one `@pytest.mark.parametrize`. Break the code on purpose, confirm that a test fails, and note which test caught it. | Fixtures, testing error paths |
| Project, Tasks 5–6 | `predict_weather.py` | Load the real saved model, predict at least four days (good, bad, and borderline), and print one line per day. Answer three reflection questions in a comment block. | Using the component, the `__main__` guard |

**Optional:** Extension A (`predict_frame` for a DataFrame), Extension B (a confidence threshold), and Extension C (a `pyproject.toml` and an editable install). These are marked "(Optional)" and are not graded.

**Submission:** A link to an open pull request in the student's `python200-homework` repository. The `models/` files need to be committed.

---

## Key Concepts

These short explanations cover the ideas students ask about most this week. Expand any one you need.

<details>
<summary><strong>What the component hides, and why it loads the model once</strong></summary>

The Week 3 prediction code asks every caller to handle many details correctly. The caller loads the file with `joblib`, loads the metadata, builds a DataFrame with the columns in order, and calls `predict` and `predict_proba`. Then the caller converts `1` to "good" and reads the probability from column 1.

The `WeatherClassifier` class does all of this once, in one place. A caller passes plain dictionaries to `predict()` and reads `result.label` and `result.probability`. If the model file, the feature list, or the label encoding changes later, only the class changes, and callers keep working.

The class loads the model in `__init__` because reading a `.pkl` file from disk is slow compared to making a prediction. The loaded model is stored on `self.model`, so every later call to `predict()` reuses it. This matters in Week 10, when the pipeline classifies many rows from a database with one `WeatherClassifier` object.

</details>

<details>
<summary><strong>Why feature order can break a model with no error</strong></summary>

A fitted pipeline stores a mean, a standard deviation, and a coefficient for each column position. If wind speed arrives in the position where the model expects the high temperature, the math still runs. The model produces a confident but wrong prediction, with no error. This is most likely when the column names are lost, for example when a caller passes a NumPy array or a plain list.

`predict()` prevents this with one line: `X = frame[self.features]`. This line selects the four features in the training order, whatever order the caller used for the dictionary keys. It also has two useful side effects:

- Extra keys are ignored. In Week 10, database rows include `date` and `loaded_at`, and the component still works.
- Missing keys are caught first. The method checks for them and raises a `ValueError` that names the missing features, instead of failing deep inside the pipeline.

This is the "concrete bug" that Reflection question 1 asks about.

</details>

<details>
<summary><strong>How the test suite works: fixtures, tmp_path, conftest.py, and match</strong></summary>

The tests do not load the student's real `models/weather_classifier.pkl`. A fixture called `model_path` trains a tiny pipeline on 15 obvious good days and 15 obvious bad days. It saves the pipeline to `tmp_path`, a temporary folder that `pytest` creates for each test. A second fixture, `clf`, loads a `WeatherClassifier` from that file. Any test that names `clf` as a parameter receives a ready classifier. The suite is therefore fast, starts clean, and passes on any correct submission.

The empty `conftest.py` at the top of `assignments_04/` tells `pytest` to add that folder to Python's import path. Without it, `from weather_model import WeatherClassifier` fails inside the tests.

The error tests use `pytest.raises(ValueError, match="missing required features")`. The `match` argument checks the error message. Without it, an unrelated `ValueError`, such as one caused by a typo in the test, would also make the test pass.

</details>

---

## FAQs and Common Trouble Spots

**1. "Every test fails with `ModuleNotFoundError: No module named 'weather_model'`."**
Check first for the empty `conftest.py` at the top of `assignments_04/`. The answer key calls this the most common cause of a whole-suite failure. Also confirm that the student runs `pytest` from inside `assignments_04/`, because that is where the grader runs it.

**2. "I do not have my Week 3 model files."**
The student can retrain and save a model with their Week 3 `train_classifier.py`. The test suite does not need the real model, but `predict_weather.py` does. If the student deployed KNN in Week 3 instead of logistic regression, the component still works, because both models provide `predict_proba`.

**3. "My real model fails, but the tests pass."**
Ask whether the student's Week 3 pipeline used extra features, for example `season` from Week 3 Extension A. The component sends only the four required features, so a model trained on other columns will not accept them. The fix is to save a four-feature model for this week.

**4. "Do I need six tests or seven?"**
The tests must cover all seven listed behaviors. One test function may cover two of them, usually a parametrized test that checks both the good and the skip label, so six test functions can be enough. Check that the error tests use `match=` and that at least one test uses `@pytest.mark.parametrize`.

**5. "`pytest` does not run my warmup tests."**
This is expected. A bare `pytest` run collects only files named `test_*.py`, and `warmup_04.py` does not match. The student runs the warmup with `pytest warmup_04.py -v`. Do not mark a student down because the warmup is missing from the main run.

**6. "My probabilities do not match the lesson output."**
The lesson prints `good (0.97)`, `skip (0.01)`, and `skip (0.33)` for its three sample days, using the course model. Each student uses their own Week 3 model, so their numbers will differ. Check only that a mild, dry, calm day comes out "good" and a cold, rainy, windy day comes out "skip."

**7. "What happens if I leave out the `if __name__ == "__main__":` guard?"**
Then `main()` runs whenever another script imports `predict_weather.py`. Importing the file would load the model and print the report as a side effect. Task 5 asks students to explain this in a comment.
