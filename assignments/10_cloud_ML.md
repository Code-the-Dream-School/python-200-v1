# Week 10 Assignments

This week you built the Transform step of the pipeline: the `WeatherClassifier` component from Week 4 runs on each row in `weather_raw`, then an LLM adds a one-sentence recommendation, and the combined output goes into `weather_enriched`. Finally, you wrap the whole thing into a Prefect flow. The warmup checks your understanding of where ML and LLMs each belong and how they complement each other. The project has you build the complete double-transform end-to-end and orchestrate it.

---

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_10/`. Inside that folder, create:

1. `warmup_10.py` — warmup exercises (conceptual answers as comments, code as runnable Python)
2. `transform_10.py` — the complete double-transform pipeline, wrapped as a Prefect flow
3. `weather_model/` — copy your `WeatherClassifier` component package from Week 4 here
4. `models/` — copy your `weather_classifier.pkl` from Week 4 here

When finished, commit and open a PR as described in the [assignments README](README.md).

**Prerequisites:** Your Week 9 project must have run successfully and populated `weather_raw` in your Supabase project before you run this week's transform script.

```bash
uv pip install supabase python-dotenv joblib scikit-learn pandas openai prefect
```

---

# Part 1: Warmup

Put all warmup answers in `warmup_10.py`. Label each section and question with comments.

## ML vs. LLM in Pipelines

### ML/LLM Question 1

In a comment block, explain the difference between what the ML classifier produces and what the LLM produces in this week's pipeline. Why does each tool do what it does? What would go wrong if you tried to swap them — using the LLM to make the binary good/skip prediction and the ML model to write the recommendation?

### ML/LLM Question 2

For each task below, write one sentence in a comment block stating whether you would use a trained ML model, an LLM, or deterministic code, and why:

- Converting a date string like `"2023-07-04"` to day-of-week
- Classifying a job posting as "entry-level", "mid-level", or "senior" based on freeform text
- Predicting customer churn given 15 numeric features and a labeled training dataset
- Normalizing inconsistent city names ("NYC", "New York City", "New York, NY") to a canonical form
- Summing a column of revenue figures

### ML/LLM Question 3

In a comment block, answer: what is incremental processing, and why is it important for this pipeline? What would happen — in terms of cost and data correctness — if the transform script re-processed all 365 records every time it ran?

## Prompt Design

### Prompt Question 1

The lesson prompt asks the LLM for exactly one sentence. Write an alternative system prompt that asks for a two-sentence recommendation where the first sentence states the prediction and the second sentence explains the reasoning. In a comment, describe: what would you need to change in the validation logic to accommodate two sentences instead of one?

### Prompt Question 2

Write a function `call_with_retry(client, messages, max_retries=3)` that calls `client.chat.completions.create()` and retries up to `max_retries` times on any exception, with a 2-second wait between attempts. On final failure, return `None`. In a comment, describe when you would use this in a production pipeline.

---

# Part 2: Project — The Double-Transform Pipeline

Build `transform_10.py`, a script that reads from `weather_raw`, runs the ML classifier and LLM enrichment on each unprocessed record, and writes the results to `weather_enriched`.

## Step 1: Incremental Read

Fetch all rows from `weather_raw`. Fetch all dates already present in `weather_enriched`. Determine which records still need processing.

Print a summary: how many raw records exist, how many are already enriched, and how many will be processed this run.

## Step 2: ML Transform

Create a `WeatherClassifier` from `models/weather_classifier.pkl` and call `predict()` on the unprocessed records. Build a list of enrichment records with `date`, `good_for_running` (from each `Prediction`'s `label`), and `confidence` (from its `probability`).

Print a summary of the predictions: how many days were classified as good, and what is the confidence range?

## Step 3: LLM Transform

Design a system prompt and user message function that passes each day's weather features and ML prediction to `gpt-4o-mini`. For each enrichment record, call the API and add an `llm_summary` field with the one-sentence recommendation.

Handle API errors gracefully: use a fallback string rather than crashing. Add a progress print every 50 records.

## Step 4: Load

Upsert all enrichment records into `weather_enriched`. Print the number of rows upserted.

## Step 5: Verify

Query `weather_enriched` and print:
- The total number of rows
- Five sample rows showing `date`, `good_for_running`, `confidence`, and `llm_summary`
- The number of days classified as good for running

Add a comment: look at a few of the LLM summaries. Do they accurately reflect the weather features and the model's prediction? Pick one you think is particularly good and one that seems off — what might have caused the weaker one?

## Step 6: Orchestrate with Prefect

Now wrap your pipeline in a Prefect flow, as shown in the orchestration lesson. Turn each stage — read, classify, enrich, load — into an `@task`, and write a `@flow(log_prints=True)` that calls them in order. Run the flow and confirm it completes with every task marked as completed.

Keep it light: you are not adding retries, scheduling, or the Prefect UI this week — that is Week 11. The goal is a working flow with the four steps as tracked tasks. `transform_10.py` should define and run this flow.

## Step 7: Reflect

Add a comment block (at least 5–6 sentences) addressing:

1. Your ML classifier was trained on one particular city's data (whichever city you chose in Week 3). If you loaded weather for a *different* city in Week 9 than the one your model was trained on, do you expect the classifier's predictions to be accurate? Why or why not?
2. The LLM recommendations are generated from the model's prediction and the weather features. Does the LLM have any ability to "override" the classifier, or is it purely additive? What are the implications of that?
3. If you ran this pipeline on 50,000 records instead of 365, what would be your main concern: cost, latency, or something else? How would you address it?

## Video

Record a short video (target: 3–4 minutes, max: 5). Show:

1. The Prefect flow running in your terminal with no errors — the run summary showing each task completing
2. The `weather_enriched` table in your Supabase dashboard with rows visible
3. A few printed sample rows showing the LLM recommendations

Paste the video link in a comment at the top of `transform_10.py`.

---

<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

### Required Deliverables/Tasks

**General grading notes:**

- **Student-chosen values and generated text vary.** The city, the specific predictions, and every LLM-generated `llm_summary` differ between students and between runs. Do not fail a student for text or numbers that differ from any reference. A full year is roughly 365 records.
- **External artifacts and copied files cannot be inspected.** The reviewer cannot see the student's Supabase project, the video, their `.env`, or their filesystem, and cannot confirm that `weather_model/` and `models/weather_classifier.pkl` were copied in. Grade the submitted code and written answers; do not fail a student for an unverifiable file, dashboard, or video.
- **Names are exact.** `Use exactly as written (they must match Week 9's tables and the Week 4 component)`: the tables `weather_raw` and `weather_enriched` and the columns `date`, `good_for_running`, `confidence`, `llm_summary`; the `WeatherClassifier` component and its `Prediction` result's `label`/`probability`; the model id `gpt-4o-mini`; and the function `call_with_retry`. `Example — adapt to your own values`: the chosen city, the exact prompt wording, and any sample values.

**Part 1 — `warmup_10.py`:**

- **ML/LLM Q1** — a comment explaining what the ML classifier produces vs what the LLM produces, why each tool fits its role, and what breaks if they are swapped.
- **ML/LLM Q2** — one sentence for each of the five tasks stating ML model / LLM / deterministic code, with a reason.
- **ML/LLM Q3** — a comment explaining incremental processing and the cost/correctness consequences of reprocessing all records every run.
- **Prompt Q1** — an alternative two-sentence system prompt (prediction, then reasoning), plus a comment on the validation change needed.
- **Prompt Q2** — a `call_with_retry(client, messages, max_retries=3)` that retries on any exception with a 2-second wait and returns `None` on final failure, plus a comment on when to use it.

**Part 2 — `transform_10.py`:**

- **Step 1 — Incremental Read** — fetches `weather_raw`, fetches dates already in `weather_enriched`, determines which records still need processing, and prints a summary of the three counts.
- **Step 2 — ML Transform** — creates a `WeatherClassifier` from the saved model and calls `predict()` on the unprocessed records, building enrichment records with `date`, `good_for_running` (from each `Prediction`'s `label`), and `confidence` (from its `probability`); prints a prediction summary.
- **Step 3 — LLM Transform** — a system prompt and message function passing each day's features and prediction to `gpt-4o-mini`, adding an `llm_summary`; graceful error handling with a fallback string; a progress print every 50 records.
- **Step 4 — Load** — upserts the enrichment records into `weather_enriched` and prints the number upserted.
- **Step 5 — Verify** — prints the total row count, five sample rows (`date`, `good_for_running`, `confidence`, `llm_summary`), and the good-day count, plus a comment evaluating a strong and a weak LLM summary.
- **Step 6 — Orchestrate with Prefect** — each stage (read, classify, enrich, load) is an `@task`, wired together by a `@flow(log_prints=True)` that runs and completes with every task marked completed. `transform_10.py` defines and runs this flow.
- **Step 7 — Reflect** — a comment block answering the three questions (model transfer across cities, whether the LLM can override the classifier, and the main concern at 50,000 records).
- **Video** — a link at the top of `transform_10.py` to a short video showing the flow running, the `weather_enriched` table with rows, and sample rows with recommendations.

### Optional Deliverables/Tasks

**None.**

</details>
