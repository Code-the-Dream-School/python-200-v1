# Orchestrating with Prefect

You now have a working double-transform script: it reads from `weather_raw`, classifies each day, enriches it with an LLM recommendation, and writes to `weather_enriched`. It runs top to bottom as one long script. That works, but it has no memory of what happened. If the LLM step fails halfway through, you get a stack trace and little else. You cannot easily see which steps ran, how long they took, or which one broke.

This lesson introduces **Prefect**, the tool that turns a linear script into an orchestrated *flow*. We keep it light here: the goal is to wrap the steps you already wrote into tasks and a flow, and to see the run tracked. The production features — retries, structured logging, scheduling, and the Prefect UI — come in Week 11, which builds directly on this lesson.

## Learning Objectives

By the end of this lesson, you will be able to:

- Explain what a Prefect *task* and *flow* are and why orchestration matters
- Wrap the steps of a pipeline into `@task` functions
- Combine those tasks into a single `@flow` and run it

Install Prefect:

```bash
uv pip install prefect
```

## Why Orchestrate?

A plain script treats every line as equal. An orchestrator treats a pipeline as a set of named steps with a defined order, and it tracks each one. That gives you three things a script does not have:

- **Visibility.** You can see each step run, whether it succeeded or failed, and how long it took.
- **Structure.** The pipeline becomes a set of reusable units instead of one long block of code.
- **A foundation for reliability.** Once the steps are separate tracked units, you can add retries, logging, and scheduling on top without rewriting the logic. That is the Week 11 work.

Prefect is a Python library built for exactly this. You describe your pipeline as ordinary Python functions and add two decorators.

## Tasks and Flows

Prefect has two building blocks.

A **task** is a single unit of work: read the records, run the classifier, call the LLM, write the results. You mark a function as a task with the `@task` decorator.

A **flow** is the orchestrator that calls tasks in order and manages the run as a whole. You mark it with the `@flow` decorator.

```python
from prefect import task, flow

@task
def add(a, b):
    return a + b

@flow
def math_flow():
    result = add(2, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    math_flow()
```

When you run this, Prefect does more than call `add`. It records that the flow started, that the `add` task ran and completed, and that the flow finished, printing a short summary of the run. On a two-line example that is not very interesting. On a four-step pipeline that calls an external API, it is exactly the visibility you want.

## Wrapping the Double-Transform in Tasks

Now we turn the double-transform script into a flow. Each stage of the pipeline becomes a task. The bodies are the same code you wrote in the last two lessons, moved into functions.

We create the clients and the component once, at the top, so every task can use them.

```python
import os
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI
from prefect import task, flow

from weather_model import WeatherClassifier

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
classifier = WeatherClassifier("models/weather_classifier.pkl")

SYSTEM_PROMPT = (
    "You are writing a one-sentence running recommendation for a daily weather summary app. "
    "You will receive weather conditions for a single day and a machine learning prediction "
    "about whether the day is good for running. "
    "Write exactly one sentence — direct, practical, and specific to the conditions. "
    "Do not use bullet points, headers, or phrases like 'Based on the data'."
)
```

**The read task** fetches the new records, applying the incremental check from the ML lesson:

```python
@task
def read_new_records():
    raw_rows = supabase.table("weather_raw").select("*").execute().data
    already_done = {r["date"] for r in supabase.table("weather_enriched").select("date").execute().data}
    return [r for r in raw_rows if r["date"] not in already_done]
```

**The classify task** runs the `WeatherClassifier` component and builds the enrichment records:

```python
@task
def classify(records):
    predictions = classifier.predict(records)
    return [
        {
            "date":             row["date"],
            "good_for_running": pred.label == "good",
            "confidence":       round(pred.probability, 4),
            "llm_summary":      None,
        }
        for row, pred in zip(records, predictions)
    ]
```

**The enrich task** adds the LLM recommendation to each record. This is the loop from the enrichment lesson:

```python
@task
def enrich(enrichment_records, raw_records):
    by_date = {r["date"]: r for r in raw_records}
    for record in enrichment_records:
        raw = by_date[record["date"]]
        prediction_text = "good for running" if record["good_for_running"] else "not ideal for running"
        user_message = (
            f"Date: {raw['date']}\n"
            f"High: {raw['temperature_2m_max']}°C, Low: {raw['temperature_2m_min']}°C\n"
            f"Precipitation: {raw['precipitation_sum']} mm\n"
            f"Max wind speed: {raw['wind_speed_10m_max']} km/h\n"
            f"Model prediction: {prediction_text} (confidence: {record['confidence']:.0%})"
        )
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=100,
            )
            record["llm_summary"] = response.choices[0].message.content.strip() or "Recommendation unavailable."
        except Exception as e:
            print(f"API error on {record['date']}: {e}")
            record["llm_summary"] = "Recommendation unavailable."
    return enrichment_records
```

**The load task** upserts the finished records:

```python
@task
def load(enrichment_records):
    result = supabase.table("weather_enriched").upsert(enrichment_records, on_conflict="date").execute()
    return len(result.data)
```

## Combining Them in a Flow

The flow calls the tasks in order and passes the output of one to the next.

```python
@flow(log_prints=True)
def double_transform_flow():
    records = read_new_records()
    if not records:
        print("Nothing to do — all records already enriched.")
        return

    print(f"Processing {len(records)} new records")
    enrichment_records = classify(records)
    enrichment_records = enrich(enrichment_records, records)
    count = load(enrichment_records)
    print(f"Loaded {count} enriched records")


if __name__ == "__main__":
    double_transform_flow()
```

`@flow(log_prints=True)` tells Prefect to capture every `print()` in the flow and its tasks as part of the run's log. When you run the file, Prefect prints a summary as each task moves from running to completed, then reports whether the flow as a whole succeeded. You are running the exact same double-transform logic as before, but now it runs as a tracked pipeline: four named steps, in order, each with its own state.

Notice what the flow reads like. It is a short, readable description of the pipeline — read, classify, enrich, load — with the details tucked inside the tasks. That readability is a real benefit of orchestration on its own, before any of the reliability features.

## What Comes Next

This is deliberately the light version. The tasks run once, in order, and if one fails the flow stops. In Week 11 you will take this same flow and make it production-ready:

- **Retries** so a transient network error on the LLM call does not kill the whole run.
- **Structured logging** with `get_run_logger()` for cleaner, searchable logs.
- **The Prefect UI**, where you can inspect each run visually.
- **Scheduling**, so the pipeline runs on its own every day, and it is combined with the Week 9 extract-and-load into one complete cloud ETL pipeline.

For now, the important idea is the shape: a pipeline is a set of tasks, wired together by a flow.

## Check for Understanding

1. What is the difference between a Prefect `@task` and a `@flow`?

    - A. A task is faster than a flow
    - B. A task is a single unit of work; a flow is the orchestrator that calls tasks in order and manages the run
    - C. A flow can only contain one task
    - D. They are interchangeable decorators

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. Each step of the pipeline is a task, and the flow calls the tasks in sequence and tracks the run as a whole.
    </details>

2. What does wrapping the double-transform script in a flow give you that the plain script did not?

    - A. Faster predictions from the model
    - B. Visibility into each step's state, a readable pipeline structure, and a foundation for adding retries and scheduling later
    - C. A way to avoid using the LLM
    - D. Automatic correction of failed API calls

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. Orchestration tracks each step, makes the pipeline's structure explicit, and sets up the reliability features you add in Week 11. It does not change the underlying logic.
    </details>

3. The flow passes the output of `classify` into `enrich`, and the output of `enrich` into `load`. Why does the order matter?

    - A. It does not; Prefect runs tasks in random order
    - B. Each task depends on the result of the previous one — you cannot enrich records before they are classified, or load them before they are enriched
    - C. Prefect requires alphabetical task order
    - D. The order only matters for logging

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. The pipeline is a sequence: classify produces the records, enrich adds the LLM summary, and load writes them. Passing each result to the next task is what defines that order.
    </details>
