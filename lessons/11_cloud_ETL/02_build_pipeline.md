# Building the Pipeline

You have already written all the pieces of this pipeline. In Week 9 you extracted weather data from Open-Meteo and loaded it into `weather_raw`. In Week 10 you read those rows back, classified them with the ML model from Week 4, enriched each prediction with an LLM recommendation, and wrote the results to `weather_enriched`. This lesson wires all of it into a single Prefect flow.

At this point, the main goal is not learning brand-new concepts — it is learning how the pieces connect into a real workflow. This is much closer to how production data pipelines are structured in practice.

For reference:

- [Prefect tasks documentation](https://docs.prefect.io/v3/concepts/tasks)
- [Week 9: The Extract + Load Pipeline](../09_cloud_data/03_loading_pipeline.md)
- [Week 10: ML Inference on Database Records](../10_llm_pipelines/02_ml_inference.md)
- [Week 10: LLM Enrichment and Writing to weather_enriched](../10_llm_pipelines/03_llm_enrichment.md)

## Learning Objectives

By the end of this lesson, you will be able to:

- Implement extract, load_raw, transform, and load_enriched as Prefect tasks using real cloud operations
- Wire the four tasks into a `@flow` and run the complete pipeline end-to-end
- Read a Prefect UI run to confirm success or identify a failure

## Setup

This pipeline requires packages from Weeks 9 and 10:

```bash
uv pip install prefect requests openai python-dotenv supabase joblib scikit-learn pandas
```

Copy two things from your Week 4 assignment into the directory where you run the script: the `weather_model/` package (the `WeatherClassifier` component) and the `models/` directory that holds `weather_classifier.pkl`. This is the same setup you used in Week 10.

Define your shared constants and clients at the top of the script. The Supabase and OpenAI clients are initialized once and passed into tasks via closure — they do not need to be recreated on every task call:

```python
import os
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI

from weather_model import WeatherClassifier

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
classifier = WeatherClassifier("models/weather_classifier.pkl")

DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "wind_speed_10m_max",
]

SYSTEM_PROMPT = (
    "You are writing a one-sentence running recommendation for a daily weather summary app. "
    "You will receive weather conditions for a single day and a machine learning prediction "
    "about whether the day is good for running. "
    "Write exactly one sentence — direct, practical, and specific to the conditions. "
    "Do not use bullet points, headers, or phrases like 'Based on the data'."
)
```

## The Extract Task

The extract task calls the Open-Meteo historical archive API and returns a list of row dictionaries, one per day. Adding `retries=2` means Prefect will automatically retry up to twice if the request fails — useful since API calls can fail transiently:

```python
import requests
from prefect import task

LATITUDE  = 35.23
LONGITUDE = -80.84

@task(retries=2, retry_delay_seconds=10)
def extract() -> list:
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude":   LATITUDE,
        "longitude":  LONGITUDE,
        "start_date": "2023-01-01",
        "end_date":   "2023-12-31",
        "daily": DAILY_VARIABLES,
        "timezone": "America/New_York",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    daily = response.json()["daily"]
    records = [
        {
            "date":               daily["time"][i],
            "temperature_2m_max": daily["temperature_2m_max"][i],
            "temperature_2m_min": daily["temperature_2m_min"][i],
            "precipitation_sum":  daily["precipitation_sum"][i],
            "wind_speed_10m_max": daily["wind_speed_10m_max"][i],
        }
        for i in range(len(daily["time"]))
    ]

    print(f"Extracted {len(records)} daily records from Open-Meteo")
    return records
```

One task, one responsibility: fetch the data and return it. The task does not know where it came from or where it is going — that is the flow's job.

## The Load Raw Task

The load_raw task upserts the raw records into `weather_raw`. Using `upsert` with `on_conflict="date"` makes it idempotent — re-running the pipeline does not duplicate rows:

```python
@task(retries=2, retry_delay_seconds=5)
def load_raw(records: list) -> None:
    response = (
        supabase.table("weather_raw")
        .upsert(records, on_conflict="date")
        .execute()
    )
    print(f"Upserted {len(response.data)} rows into weather_raw")
```

This task must complete before the `load_enriched` task runs. The `weather_enriched` table has a foreign key on `date`, so every enriched row needs a matching row in `weather_raw`. The transform task does not depend on this task, because its incremental check queries `weather_enriched`, not `weather_raw`. The flow calls the tasks in order, so the raw data is always stored before the enriched data.

## The Transform Task

The transform task encapsulates the double-transform from Week 10: ML inference followed by LLM enrichment. Structuring it as a single task keeps the flow clean while still making the two internal stages explicit through comments and print statements:

```python
from prefect import task

@task
def transform(raw_records: list) -> list:
    # --- Incremental check ---
    already_done = {
        r["date"]
        for r in supabase.table("weather_enriched").select("date").execute().data
    }
    to_process = [r for r in raw_records if r["date"] not in already_done]
    print(f"Records to transform: {len(to_process)} (skipping {len(already_done)} already enriched)")

    if not to_process:
        print("All records already enriched — nothing to do.")
        return []

    # --- ML classify ---
    predictions = classifier.predict(to_process)

    good = sum(1 for p in predictions if p.label == "good")
    print(f"ML classification complete. Good days: {good} / {len(predictions)}")

    enrichment_records = [
        {
            "date":             row["date"],
            "good_for_running": pred.label == "good",
            "confidence":       round(pred.probability, 4),
            "llm_summary":      None,
        }
        for row, pred in zip(to_process, predictions)
    ]

    # --- LLM enrich ---
    for i, record in enumerate(enrichment_records):
        raw_row = to_process[i]
        prediction_text = "good for running" if record["good_for_running"] else "not ideal for running"
        user_message = (
            f"Date: {raw_row['date']}\n"
            f"High: {raw_row['temperature_2m_max']}°C, Low: {raw_row['temperature_2m_min']}°C\n"
            f"Precipitation: {raw_row['precipitation_sum']} mm\n"
            f"Max wind speed: {raw_row['wind_speed_10m_max']} km/h\n"
            f"Model prediction: {prediction_text} (confidence: {record['confidence']:.0%})"
        )
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_message},
                ],
                max_tokens=100,
            )
            record["llm_summary"] = response.choices[0].message.content.strip() or "Recommendation unavailable."
        except Exception as e:
            print(f"  LLM error on {record['date']}: {e}")
            record["llm_summary"] = "Recommendation unavailable."

        if (i + 1) % 50 == 0:
            print(f"  LLM enriched {i + 1} / {len(enrichment_records)} records")

    print(f"Transform complete: {len(enrichment_records)} records enriched")
    return enrichment_records
```

Several production patterns are present here:

- The incremental check means re-running the flow on data already transformed does no extra work — and no extra LLM cost.
- The `WeatherClassifier` component is created once at the top of the script, so the model file is loaded only once.
- `classifier.predict()` is called once on the full list of records, not in a loop. Batch inference is much faster than classifying one record at a time.
- Each `Prediction` gives you a `label` and a `probability`. The component selects the feature columns in the correct order, so the extra `date` key on each row is ignored.
- LLM failures are caught and replaced with a fallback string rather than crashing the task.
- Progress logs every 50 records make long-running transforms easy to follow in the Prefect UI.

## The Load Enriched Task

The final task upserts the enrichment records into `weather_enriched`:

```python
@task(retries=2, retry_delay_seconds=5)
def load_enriched(enrichment_records: list) -> None:
    if not enrichment_records:
        print("No new enrichment records to load.")
        return

    response = (
        supabase.table("weather_enriched")
        .upsert(enrichment_records, on_conflict="date")
        .execute()
    )
    print(f"Upserted {len(response.data)} rows into weather_enriched")
```

The guard on `not enrichment_records` handles the case where the transform task found nothing to process — the task exits cleanly rather than sending an empty upsert to the database.

## Wiring the Flow

```python
from prefect import flow

@flow(log_prints=True)
def etl_pipeline():
    raw_records        = extract()
    load_raw(raw_records)
    enrichment_records = transform(raw_records)
    load_enriched(enrichment_records)
    print("Pipeline complete.")

if __name__ == "__main__":
    etl_pipeline()
```

The flow is five lines. Each task call is one line. The data dependencies — what each task returns and what the next task receives — are visible at a glance. This is the characteristic shape of a well-structured Prefect flow: the orchestration logic is minimal; the work happens inside the tasks.

## Running the Pipeline

Start the Prefect UI in one terminal:

```bash
prefect server start
```

Run the pipeline in a second terminal:

```bash
python etl_pipeline.py
```

Your Week 10 script already enriched every date, so your first run of this pipeline should look like this:
1. The extract task fetches 365 records.
2. The load_raw task upserts them into `weather_raw`.
3. The transform task finds that every date is already in `weather_enriched`. It prints `All records already enriched — nothing to do.` and returns an empty list.
4. The load_enriched task prints `No new enrichment records to load.` and exits.

This is the incremental check working correctly. The run is fast, and it makes no LLM calls.

If you want to see a full run, delete some or all of the rows from `weather_enriched` in the Supabase dashboard, and then run the pipeline again. The transform task then classifies the missing dates and sends one LLM request for each of them. A full run of 365 records takes several minutes, because each LLM call takes about one second. Each call also uses your OpenAI credits again, so delete only as many rows as you need. During a long run, the transform task prints its progress every 50 records.

## Reading the Prefect UI

Open `http://localhost:4200` and click into the `etl-pipeline` run. A successful run shows all four tasks in *Completed* state. Click any task to see its logs — you should see the print statements from each task captured there.

If a task fails, it shows in *Failed* state (red). Click the failed task and open the *Logs* tab to find the exception traceback. Tasks that completed successfully remain green, so you can see exactly where in the pipeline the failure occurred without re-running the whole thing.

A useful exercise: cause a small failure intentionally and observe how the UI responds. For example, temporarily remove your `SUPABASE_KEY` from `.env`, run the pipeline, and read the failure trace. Then restore the key and re-run — the incremental check means you pick up from where you left off, not from the beginning.
