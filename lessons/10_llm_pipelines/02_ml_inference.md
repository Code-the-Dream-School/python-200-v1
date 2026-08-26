# ML Inference on Database Records

The weather classifier you built in Week 4 has been waiting. You trained it, tuned it, saved it to `models/weather_classifier.pkl`, and wrote a prediction script that loaded it against hand-crafted test cases. This lesson connects that classifier to real data: you will read rows from `weather_raw`, run them through the saved Pipeline, and produce confidence scores and binary predictions for each day.

## Learning Objectives

By the end of this lesson, you will be able to:

- Load a saved sklearn Pipeline from disk and apply it to rows fetched from Supabase
- Build a DataFrame from database records in the correct feature order for the saved model
- Extract both predicted labels and confidence scores from `predict` and `predict_proba`
- Implement incremental processing — only classifying records not yet in `weather_enriched`

## Setup

You will need the `models/` directory from your Week 4 assignment — specifically `weather_classifier.pkl` and `weather_classifier_metadata.json`. If you do not have these files locally, re-run your `train_weather_classifier.py` from Week 4 to regenerate them before proceeding.

Install any missing packages:

```bash
uv pip install supabase python-dotenv joblib scikit-learn pandas
```

## Reading Records from weather_raw

Start by connecting to Supabase and fetching everything from `weather_raw`:

```python
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

response = supabase.table("weather_raw").select("*").execute()
raw_rows = response.data
print(f"Fetched {len(raw_rows)} rows from weather_raw")
```

`raw_rows` is a list of dictionaries. Each dictionary has keys matching the column names: `date`, `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `wind_speed_10m_max`, and `loaded_at`.

## Incremental Processing

Before classifying all 365 records, check which dates are already in `weather_enriched`. There is no reason to re-run inference on records you have already processed — and if something went wrong with the LLM step last time, you want to be able to re-run only the enrichment without re-running the classifier.

```python
enriched_response = supabase.table("weather_enriched").select("date").execute()
already_done = {row["date"] for row in enriched_response.data}

to_classify = [row for row in raw_rows if row["date"] not in already_done]
print(f"Records to classify: {len(to_classify)} (skipping {len(already_done)} already enriched)")
```

On the first run, `already_done` is empty and all 365 records will be classified. On subsequent runs, only records not yet in `weather_enriched` will be processed. This is the incremental load pattern — the pipeline advances forward without redoing completed work.

This is the difference between a one-time backfill and a repeated incremental run. It's why, in the cloud, a scheduled job can process only new data cheaply.

## Building the Feature DataFrame

The saved Pipeline expects input as a DataFrame with columns in a specific order — the same order the model was trained on. Load that order from the metadata file:

```python
import json

with open("models/weather_classifier_metadata.json") as f:
    metadata = json.load(f)

FEATURES = metadata["features"]
# ['temperature_2m_max', 'temperature_2m_min', 'precipitation_sum', 'wind_speed_10m_max']

df = pd.DataFrame(to_classify)
X = df[FEATURES]  # select only the feature columns, in the right order
```

Using `df[FEATURES]` rather than `df.drop(["date", "loaded_at"], axis=1)` is intentional: it is explicit about which columns the model expects and is robust to any extra columns that might be added to the table later. The model does not know or care about `date` or `loaded_at`.

## Running the Classifier

Load the Pipeline and run both `predict` and `predict_proba`:

```python
import joblib

clf = joblib.load("models/weather_classifier.pkl")

predictions  = clf.predict(X)          # array of 0s and 1s
probabilities = clf.predict_proba(X)[:, 1]  # probability of class 1 (good for running)

print(f"Good days predicted: {predictions.sum()} / {len(predictions)}")
print(f"Confidence range: {probabilities.min():.2f} – {probabilities.max():.2f}")
```

`predict_proba` returns a 2D array where column 0 is the probability of class 0 ("skip") and column 1 is the probability of class 1 ("good for running"). The `[:, 1]` slice extracts the confidence score you want — the model's certainty that a given day is good.

## Building Enrichment Records

Combine the predictions back with the date for each row:

```python
enrichment_records = []
for i, row in enumerate(to_classify):
    enrichment_records.append({
        "date":             row["date"],
        "good_for_running": bool(predictions[i]),
        "confidence":       round(float(probabilities[i]), 4),
        # llm_summary will be added in the next lesson
    })

print("Sample enrichment records:")
for r in enrichment_records[:3]:
    print(r)
```

Two conversions worth noting:

- `bool(predictions[i])` converts a numpy integer (0 or 1) to a Python `bool` (`False` or `True`). Supabase expects a native Python type for boolean columns.
- `float(probabilities[i])` converts a numpy float64 to a plain Python float. Same reason.

At this point you have a list of dictionaries with `date`, `good_for_running`, and `confidence` for each unprocessed day. The `llm_summary` field is missing — you will add it in the next lesson, once the LLM step generates a recommendation for each record.

## Sanity-Checking the Output

Before wiring in the LLM, take a quick look at the predictions:

```python
good_days = [r for r in enrichment_records if r["good_for_running"]]
skip_days = [r for r in enrichment_records if not r["good_for_running"]]

print(f"Good days: {len(good_days)} ({len(good_days)/len(enrichment_records):.0%})")
print(f"Skip days: {len(skip_days)}")

# Show a few high-confidence and borderline predictions
enrichment_records.sort(key=lambda r: r["confidence"], reverse=True)
print("\nHighest confidence (good for running):")
for r in enrichment_records[:3]:
    print(f"  {r['date']}: {r['confidence']:.3f}")

enrichment_records.sort(key=lambda r: abs(r["confidence"] - 0.5))
print("\nMost borderline (closest to 0.5 confidence):")
for r in enrichment_records[:3]:
    print(f"  {r['date']}: {r['confidence']:.3f}")
```

The fraction of good days should be consistent with what you saw during training. For Charlotte, NC using 2023 data, roughly 30–40% of days should be classified as good. If the number looks wildly off — nearly zero or nearly all — check that the feature column order matches the training order and that the model file corresponds to the same city you loaded data for.

## Check for Understanding

1. You call `clf.predict_proba(X)` and get a 2D array with shape `(365, 2)`. What does `[:, 1]` do, and why do you want column 1 rather than column 0?

    - A. It selects the first row; column 0 would select the second row
    - B. It selects all values in the second column, which is the probability of the positive class (good for running)
    - C. It converts the 2D array to a 1D array of predicted labels
    - D. It filters to only the rows where the model predicted class 1

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. <code>[:, 1]</code> selects all rows from column index 1 — the probability that the model assigned to class 1 (the "good for running" class). Column 0 would give the probability of class 0 ("skip"). Since both columns sum to 1.0 for each row, you only need one.
    </details>

2. Why do you use `df[FEATURES]` rather than `df.drop(["date", "loaded_at"], axis=1)` to prepare the feature matrix?

    - A. `drop` does not work on DataFrames from Supabase
    - B. `df[FEATURES]` guarantees the columns arrive in the order the model was trained on, regardless of column order in the database or DataFrame
    - C. The metadata file contains encrypted column names that only `df[FEATURES]` can parse
    - D. `drop` removes too many columns and would cause a shape mismatch

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. The model was trained with columns in a specific order. <code>df[FEATURES]</code> selects exactly those columns in exactly that order. <code>drop</code> would only work correctly if the remaining columns happened to be in the right order — a fragile assumption that breaks if the table gains new columns or if a database query returns columns in a different sequence.
    </details>

3. On a second run of the pipeline, `already_done` has 200 entries. `weather_raw` has 365 rows. How many records will `to_classify` contain, and what will happen to the other 200?

    - A. `to_classify` contains 365 records; `already_done` is ignored
    - B. `to_classify` contains 165 records; the 200 already in `weather_enriched` are skipped
    - C. `to_classify` contains 200 records; the 165 not yet enriched are skipped
    - D. `to_classify` contains 0 records; the pipeline exits early

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. The filter <code>row["date"] not in already_done</code> keeps only records whose dates are not yet in <code>weather_enriched</code>. 365 raw rows minus 200 already enriched = 165 left to classify.
    </details>

## Lesson Wrap-Up

Reading rows from `weather_raw`, loading the saved Pipeline, slicing the feature DataFrame in the correct column order, and running `predict` plus `predict_proba` — that is the ML inference step. The incremental processing check ensures the pipeline only does new work on each run. The result is a list of enrichment records with `date`, `good_for_running`, and `confidence`, ready for the LLM step.

In the next lesson, you will add `llm_summary` to each record and write the complete enrichment records to `weather_enriched`.
