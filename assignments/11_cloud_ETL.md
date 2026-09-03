# Week 11 Assignment: Cloud ETL Capstone

This is the capstone project for Python 200. You have spent ten weeks building toward this: a cloud ETL pipeline that extracts weather data from a live API, transforms it with an ML classifier and an LLM, loads the results to Supabase, and runs the whole thing as an orchestrated, observable Prefect flow. This week you build it yourself.

The warmup checks your understanding of Prefect and production patterns. The project is the pipeline.

---

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_11/`. Inside that folder, create:

1. `warmup_11.py` — warmup exercises (conceptual answers as comments, code as requested)
2. `etl_pipeline.py` — the complete ETL pipeline
3. `weather_model/` — copy your `WeatherClassifier` component package from Week 4 here
4. `models/` — copy your `weather_classifier.pkl` from Week 4 here
5. `outputs/pipeline_run.md` — a short written reflection on your run

When finished, commit and open a PR as described in the [assignments README](README.md).

**Prerequisites:** Your Week 9 project must have run and populated `weather_raw` before running this pipeline. Your Week 4 `weather_model/` package and `models/weather_classifier.pkl` must be present.

```bash
uv pip install prefect requests openai python-dotenv supabase joblib scikit-learn pandas
```

---

# Part 1: Warmup

Put all warmup answers in `warmup_11.py`. Use comments to mark each section and question. For conceptual questions, write your answer as a comment block. For code questions, write working Python.

## Prefect Orchestration

### Prefect Question 1

In a comment block, answer: what is the difference between a `@task` and a `@flow` in Prefect? You have a helper function that converts a temperature from Celsius to Fahrenheit — a pure, in-memory calculation with no I/O. Would you decorate it with `@task`? Why or why not?

### Prefect Question 2

Write just the decorator line for a task named `call_api` that retries up to 3 times with a 30-second delay between attempts.

### Prefect Question 3

You run your pipeline and the Prefect UI shows: `extract` is *Completed*, `load_raw` is *Completed*, `transform` is *Failed*, `load_enriched` never ran. In a comment block, describe: where in the UI do you look to understand what went wrong, and what specific information would you expect to find there?

## Production Patterns

### Production Question 1

In a comment block, explain what `raise_for_status()` does and why it is better than writing `if response.status_code != 200: print("error")` in a pipeline task. What happens to downstream tasks in each case when the API returns a 500 error?

### Production Question 2

Your `load_raw` task uses `upsert` with `on_conflict="date"` instead of `insert`. The pipeline crashes halfway through the transform step. You fix the bug and re-run from the beginning. In a comment block, explain: what does `upsert` protect you from in this scenario, and what would happen if you had used plain `insert` instead?

### Production Question 3

Write a task stub — just the function signature, decorator, and a single log line — that uses `get_run_logger()` to log an INFO message saying how many enrichment records were upserted. The function should accept `enrichment_records` (a list) as its argument.

### Production Question 4

In a comment block, explain how the incremental processing check in the transform task contributes to idempotency. If you removed it and the pipeline ran the ML and LLM steps on all 365 records every time, what would be the practical consequences (in terms of cost, time, and data correctness)?

---

# Part 2: Project — Full ETL Pipeline

Build `etl_pipeline.py`: a complete Prefect flow with four tasks that orchestrate the full Extract + Load + Transform + Load pipeline. Write it yourself using the lessons as a guide, not as code to copy verbatim. The requirements below specify what each task must do; the implementation is yours.

## Requirements

### extract task

- `@task(retries=2, retry_delay_seconds=10)`
- Calls the Open-Meteo historical archive API to fetch 2023 daily weather data for a city of your choice, using the same four variables as Week 4
- Uses `raise_for_status()`
- Converts the columnar API response into a list of row dictionaries
- Prints a confirmation with the record count
- Returns the list of row dicts

### load_raw task

- `@task(retries=2, retry_delay_seconds=5)`
- Upserts the raw records into `weather_raw` using `on_conflict="date"`
- Prints a confirmation with the upserted row count

### transform task

- `@task`
- Performs an incremental check: fetches dates already in `weather_enriched` and skips them
- Uses the `WeatherClassifier` component (loaded from `models/weather_classifier.pkl`) to classify the unprocessed records, reading each `Prediction`'s `label` and `probability`
- Calls the OpenAI API to generate a one-sentence recommendation for each record
- Handles LLM errors gracefully with a fallback string
- Prints progress every 50 records
- Returns the complete list of enrichment records

### load_enriched task

- `@task(retries=2, retry_delay_seconds=5)`
- Guards against an empty list (prints a message and returns early if nothing to load)
- Upserts enrichment records into `weather_enriched` using `on_conflict="date"`
- Prints a confirmation with the upserted row count

### Flow

- `@flow(log_prints=True)`
- Calls all four tasks in the correct order
- Prints a final completion message

## Running and Verifying

1. Start the Prefect server: `prefect server start`
2. Run your pipeline: `python etl_pipeline.py`
3. Open `http://localhost:4200` and verify all four tasks show *Completed*
4. Confirm the data in the Supabase dashboard: `weather_raw` should have 365 rows, `weather_enriched` should have at least as many

## Reflection

Write `outputs/pipeline_run.md` with a short reflection (5–7 sentences) covering:

- Did the pipeline run cleanly on the first try? If not, what failed and how did you fix it?
- What did the Prefect UI show? Did any tasks retry?
- Look at a few rows in `weather_enriched`. Do the LLM summaries seem accurate and useful? Pick one that stands out (positively or negatively) and explain why.
- What is one thing you would change or add if you were deploying this pipeline to run on a daily schedule — fetching the previous day's forecast each morning and enriching it automatically?

## Video

Record a short video (target: 4 minutes, max: 6). Show:

1. The pipeline running in your terminal to completion, with progress output visible
2. The Prefect UI with all four tasks in *Completed* state, and the logs from the transform task
3. The `weather_enriched` table in your Supabase dashboard with rows visible, including the `llm_summary` column

Paste the video link in a comment at the top of `etl_pipeline.py`.

---

Congratulations! With this step, you have finished Python for Cloud & AI. You built a full cloud ETL pipeline from scratch — extract, transform with an ML model and an LLM, load to a cloud database, orchestrated and observable with Prefect. That is a genuinely production-relevant workflow.

---

<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

### Required Deliverables/Tasks

**General grading notes:**

- **This is a capstone written to a specification, not a reference implementation.** The assignment says to write the pipeline from scratch, so implementations vary widely. Grade whether each task meets its stated requirements, not whether the code matches any particular solution.
- **Student-chosen values and generated text vary.** The city, the specific rows, and every LLM `llm_summary` differ between students and runs. Do not fail a student for text or numbers that differ from a reference. `weather_raw` should have roughly 365 rows for a full year.
- **External artifacts and copied files cannot be inspected.** The reviewer cannot see the student's Supabase project, the Prefect UI, the video, or their filesystem, and cannot confirm that `weather_model/` and `models/weather_classifier.pkl` were copied in. Grade the submitted code and the written reflection; do not fail a student for an unverifiable dashboard, UI, video, or file.
- **Names and Prefect parameters are exact.** `Use exactly as written`: the tables `weather_raw`/`weather_enriched` and their columns; the four task names `extract`, `load_raw`, `transform`, `load_enriched`; the retry parameters given per task (e.g. `retries=2, retry_delay_seconds=10`); `on_conflict="date"`; `get_run_logger`; the `WeatherClassifier` component and its `Prediction` `label`/`probability`; and the model id `gpt-4o-mini`. `Example — adapt to your own values`: the chosen city and the exact prompt wording.

**Part 1 — `warmup_11.py`:**

- **Prefect Q1** — a comment distinguishing `@task` from `@flow`, and a reasoned answer on whether to decorate a pure in-memory C→F helper (no — it does no I/O and gains nothing from task tracking).
- **Prefect Q2** — the single decorator line for a `call_api` task with 3 retries and a 30-second delay.
- **Prefect Q3** — a comment on where in the Prefect UI to investigate the failed `transform` task and what information to expect (the task's logs and traceback).
- **Production Q1** — a comment explaining `raise_for_status()` versus a manual status-code check, and what happens to downstream tasks on a 500 in each case.
- **Production Q2** — a comment explaining what `upsert` with `on_conflict="date"` protects against on a crash-and-rerun, and what plain `insert` would do instead.
- **Production Q3** — a task stub (decorator, signature accepting `enrichment_records`, and one `get_run_logger()` INFO line reporting the upserted count).
- **Production Q4** — a comment on how the incremental check contributes to idempotency and the cost/time/correctness consequences of reprocessing all records.

**Part 2 — `etl_pipeline.py`:**

- **`extract` task** — `@task(retries=2, retry_delay_seconds=10)`; fetches full-year 2023 daily weather (the four variables) for the chosen city; uses `raise_for_status()`; converts the columnar response to row dictionaries; prints the record count; returns the list.
- **`load_raw` task** — `@task(retries=2, retry_delay_seconds=5)`; upserts into `weather_raw` with `on_conflict="date"`; prints the upserted count.
- **`transform` task** — `@task`; incremental check that skips dates already in `weather_enriched`; classifies the unprocessed records with the `WeatherClassifier` component (label + confidence); calls the OpenAI API for a one-sentence recommendation per record with graceful fallback on error; prints progress every 50 records; returns the enrichment records.
- **`load_enriched` task** — `@task(retries=2, retry_delay_seconds=5)`; guards against an empty list (returns early); upserts into `weather_enriched` with `on_conflict="date"`; prints the upserted count.
- **Flow** — `@flow(log_prints=True)` calling all four tasks in order and printing a final completion message.
- **Running and verifying** — evidence (in the reflection/video) that the flow ran with all four tasks completed and both tables populated.
- **Reflection** — `outputs/pipeline_run.md` (5–7 sentences) covering the first-run outcome and any fixes, what the Prefect UI showed and whether any task retried, an assessment of a few `llm_summary` rows, and one change for a daily scheduled deployment.
- **Video** — a link at the top of `etl_pipeline.py` to a short video showing the pipeline running to completion, the Prefect UI with all four tasks completed and the transform logs, and the `weather_enriched` table with the `llm_summary` column.

### Optional Deliverables/Tasks

**None.**

</details>
