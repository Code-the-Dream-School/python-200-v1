# Week 10 Assignments

This week you built the Transform step of the pipeline: the `WeatherClassifier` component from Week 4 runs on each row in `weather_raw`, then an LLM adds a one-sentence recommendation, and the combined output goes into `weather_enriched`. Finally, you wrap the whole thing into a Prefect flow. The warmup checks your understanding of where ML and LLMs each belong and how they complement each other. The project has you build the complete double-transform end-to-end and orchestrate it.

---

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_10/`. Inside that folder, create:

1. `warmup_10.py` — warmup exercises (conceptual answers as comments, code as runnable Python)
2. `transform_10.py` — the complete double-transform pipeline, wrapped as a Prefect flow
3. `verify_10.sql` — your SQL verification queries, with their results pasted as comments
4. `weather_model/` — copy your `WeatherClassifier` component package from Week 4 here
5. `models/` — copy your `weather_classifier.pkl` from Week 4 here

If you choose to do the optional Practicum AWS Bridge in Part 3, also create an `aws_bridge/` folder inside `assignments_10/`. Part 3 lists the files that go in it.

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

**Before you run your script for the first time,** read Step 6 and run Query 1 in the SQL Editor. You need a "before" result for that query, and you can only get it while `weather_enriched` is still empty.

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

## Step 6: Verify with SQL

In Step 5, you checked `weather_enriched` with Python. In this step, you check both tables with SQL in the Supabase SQL Editor, the same way you did in Week 9. This step reviews SQL you learned in Python for Data Analysis. If you need a reminder of the syntax, open the [SQL syntax reminder](09_cloud_AI.md#step-5-verify-with-sql) in the Week 9 assignment.

Create a file called `verify_10.sql` and write two queries in it:

1. **Dates with no enrichment.** Write one query that returns every `date` in `weather_raw` that has no matching row in `weather_enriched`. Use a `LEFT JOIN` on `date` and `WHERE ... IS NULL`. Sort the results by date.
2. **Good vs. not good.** Write one query that counts how many days in `weather_enriched` are good for running and how many are not. Use `GROUP BY good_for_running`.

Run Query 1 twice:

- **Before** you run `transform_10.py` for the first time. Paste the number of rows the query returned, and the first and last date.
- **After** your transform finishes. Paste the result again.

If you already ran your transform before you read this step, you cannot get a real "before" result. Instead, write the result you would have expected and explain why.

Run Query 2 after your transform finishes. Paste each result below its query as a SQL comment (lines that start with `--`), using the same format as `verify_09.sql`. Run one query at a time, because the SQL Editor shows only the result of the last query you run.

At the bottom of `verify_10.sql`, add a comment that answers these questions:

- How did the result of Query 1 change between the two runs? What does that tell you about the incremental processing in Step 1?
- Does the result of Query 2 match the good-day count your Python code printed in Step 5?

## Step 7: Orchestrate with Prefect

Now wrap your pipeline in a Prefect flow, as shown in the orchestration lesson. Turn each stage — read, classify, enrich, load — into an `@task`, and write a `@flow(log_prints=True)` that calls them in order. Run the flow and confirm it completes with every task marked as completed.

Keep it light: you are not adding retries, scheduling, or the Prefect UI this week — that is Week 11. The goal is a working flow with the four steps as tracked tasks. `transform_10.py` should define and run this flow.

## Step 8: Reflect

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

# Part 3: (Optional) Practicum AWS Bridge — The Lambda Handler

> **This entire part is optional.** The Practicum AWS Bridge is a pilot this term. You can skip all of Part 3 without any effect on your grade.

This part goes with the optional lesson [Practicum AWS Bridge, Part 3: The Lambda Handler](../lessons/10_llm_pipelines/05_aws_bridge_handler.md). The bridge builds an automatic alert that tells the Code the Dream teaching team when fewer than 80% of students submit their weekly assignment. This week, you write the Lambda handler: the function that AWS runs on a schedule, or when a staff member checks a week by hand. You do not need an AWS account.

Plan for about two and a half hours, in addition to the optional lesson.

## Task 1: (Optional) Set Up the Folder

Create a folder called `aws_bridge/` inside `assignments_10/`, and copy everything from `assignments_09/aws_bridge/` into it. **This week adds files to that folder. Keep your Week 8 and Week 9 files.** This week's handler imports `get_alert_settings` from your Week 9 `alert_settings.py`. If you skipped Week 9, complete Week 9's Part 3, Task 2 first.

Copy these four provided files from the course repository's `assignments/resources/aws_bridge/` folder into your `aws_bridge/` folder:

- `gradebook.py` is a stand-in for Code the Dream's gradebook system. Its `fetch_submissions(token)` function returns a dictionary with three keys: `"cohort"` (a string), `"roster"` (a list of student IDs), and `"submissions"` (a list of dictionaries, each with `"student_id"`, `"week"`, and `"submitted_at"`). Do not change this file.
- `submissions.json` is the fictional cohort data that `gradebook.py` reads. Some students submitted more than once in the same week, after a mentor asked for revisions.
- `event_schedule.json` is the event that EventBridge Scheduler sends: an empty dictionary.
- `event_function_url.json` is a Function URL event. Its `"body"` is the string `"{\"week\": 5}"`.

## Task 2: (Optional) Write the Handler

Create `aws_bridge/handler.py` with the items below.

Use exactly as written: the file name `handler.py`, the names `BadEventError`, `parse_week`, `latest_week`, `calculate_submission_rate`, and `lambda_handler`, their parameters, the logger name `"submission_alert"`, and the five keys in the success response body. Week 11 of the bridge builds on this file.

1. **`BadEventError`** is an exception class that inherits from `Exception`.

2. **`parse_week(event)`** returns the week the caller asked for, as an `int`, or `None` if the caller did not ask for a week.
    - If `event` has a `"requestContext"` key, it is a Function URL event. Read `event.get("body")`. If the body is missing or empty, return `None`. Otherwise, parse it with `json.loads`. If the body is not valid JSON, raise `BadEventError`.
    - Otherwise, the event is a scheduled event, and the event dictionary itself holds any values.
    - In both cases, if there is no `"week"` key, return `None`. If `"week"` is not a whole number of at least 1, raise `BadEventError`. Note that `True` and `False` count as integers in Python, but they are not valid weeks.

3. **`latest_week(data)`** returns the highest `"week"` value in `data["submissions"]`.

4. **`calculate_submission_rate(data, week)`** returns the percentage of students on the roster who submitted in that week, rounded to one decimal place. Count each student **once**, even if they submitted more than once.

5. **`lambda_handler(event, context)`** follows these steps:
    1. Call `parse_week(event)`. If it raises `BadEventError`, return a `400` response whose body is `{"error": <the error message>}`.
    2. Call `get_alert_settings()`, and then call `fetch_submissions` with the gradebook token.
    3. Use the requested week. If no week was requested, use `latest_week(data)`. If the requested week is greater than the latest week, return a `400` response with an error message.
    4. Calculate the submission rate, and return a `200` response whose body has these five keys: `"cohort"`, `"week"`, `"submission_rate"`, `"threshold"`, and `"below_threshold"`. `"below_threshold"` is `True` when the rate is less than the threshold.
    5. Before returning a `200` response, write one `INFO` log line with `logging.getLogger("submission_alert")`. The line is the response body, converted to a string with `json.dumps`.

    Every response is a dictionary with three keys: `"statusCode"` (an `int`), `"headers"` (`{"Content-Type": "application/json"}`), and `"body"` (a JSON **string** made with `json.dumps`). Do not catch other exceptions, such as a `MissingSettingError`. Let them happen, so that Lambda records the run as failed.

## Task 3: (Optional) Test the Handler

Create `aws_bridge/test_handler.py`. Your handler reads its settings through Week 9's code, so set the two environment variables in a fixture. Then no Parameter Store is needed this week. You can use this fixture as written. `autouse=True` makes pytest use it for every test in the file:

```python
@pytest.fixture(autouse=True)
def settings_in_environment(monkeypatch):
    monkeypatch.setenv("GRADEBOOK_TOKEN", "gb-test-token")
    monkeypatch.setenv("SUBMISSION_THRESHOLD", "80")
```

Write tests for at least these cases. The expected numbers come from the provided `submissions.json`:

1. `parse_week` returns `None` for the event in `event_schedule.json`, and `5` for the event in `event_function_url.json`.
2. `parse_week` raises `BadEventError` for a Function URL event whose body is `"not json"`, `'{"week": "five"}'`, `'{"week": 0}'`, or `'{"week": true}'`. Use `@pytest.mark.parametrize`.
3. `calculate_submission_rate` returns `92.5` for week 2. Week 2 has 40 submission rows, but only 37 different students.
4. `latest_week` returns `7`.
5. `lambda_handler` with the scheduled event returns status `200`, week `7`, a submission rate of `72.5`, and `below_threshold` of `True`.
6. `lambda_handler` with the Function URL event returns week `5`, a submission rate of `82.5`, and `below_threshold` of `False`.
7. `lambda_handler` returns status `400` for a body that is not valid JSON, and for a request for week `12`.
8. `lambda_handler` writes exactly one log line from the `"submission_alert"` logger, and that line is valid JSON. Use pytest's `caplog` fixture.

A small helper function can build Function URL events for your tests. Example — adapt it to your own style:

```python
def url_event(body):
    return {"requestContext": {"http": {"method": "POST"}}, "body": body}
```

Run `pytest` and confirm that every test passes, including your tests from earlier weeks.

## Task 4: (Optional) Run the Handler by Hand

Run your handler once from the command line with each event file, and read the result. For example, from inside your `aws_bridge/` folder:

```bash
GRADEBOOK_TOKEN=gb-test-token SUBMISSION_THRESHOLD=80 python -c "import json, handler; print(handler.lambda_handler(json.load(open('event_schedule.json')), None))"
```

Windows users: run this command in Git Bash.

You do not need to submit anything for this task. It shows you what Lambda would receive back from your function.

## Task 5: (Optional) Short Answers

Create `aws_bridge/handler_notes.md` and answer these questions in two or three sentences each:

1. EventBridge Scheduler always sends the same event. How does your handler still check a new week each time it runs?
2. Your handler returns a response with a `statusCode` for every event. For which trigger does Lambda actually use that response, and what happens to it for the other trigger?
3. A teammate calculates the rate with `len([s for s in data["submissions"] if s["week"] == week])`. What does their code report for week 2, and why is it wrong?

---

<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

### Required Deliverables/Tasks

**General grading notes:**

- **Part 3 (Practicum AWS Bridge) is entirely optional.** It is a pilot this term. All of its tasks are listed under Optional Deliverables/Tasks below. Never fail a student for skipping it.

- **Student-chosen values and generated text vary.** The city, the specific predictions, and every LLM-generated `llm_summary` differ between students and between runs. Do not fail a student for text or numbers that differ from any reference. A full year is roughly 365 records.
- **External artifacts and copied files cannot be inspected.** The reviewer cannot see the student's Supabase project, the video, their `.env`, or their filesystem, and cannot confirm that `weather_model/` and `models/weather_classifier.pkl` were copied in. Grade the submitted code and written answers; do not fail a student for an unverifiable file, dashboard, or video.
- **SQL queries vary.** Accept any query in `verify_10.sql` that answers the question asked. Table aliases, column aliases, and sort direction are the student's choice. The "after" result for Query 1 is usually zero rows, and an empty result is the correct answer. The pasted counts vary by city and model.
- **Names are exact.** `Use exactly as written (they must match Week 9's tables and the Week 4 component)`: the tables `weather_raw` and `weather_enriched` and the columns `date`, `good_for_running`, `confidence`, `llm_summary`; the `WeatherClassifier` component and its `Prediction` result's `label`/`probability`; the model id `gpt-4o-mini`; and the function `call_with_retry`. `Example — adapt to your own values`: the chosen city, the exact prompt wording, and any sample values.
- - **Video link** — a link to a short narrated video posted somewhere accessible, pasted in transform_10.py. The reviewer cannot open or verify the video; grade only that a link is present, and do not fail for length or content that cannot be inspected.

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
- **Step 7 — Orchestrate with Prefect** — each stage (read, classify, enrich, load) is an `@task`, wired together by a `@flow(log_prints=True)` that runs and completes with every task marked completed. `transform_10.py` defines and runs this flow.
- **Step 8 — Reflect** — a comment block answering the three questions (model transfer across cities, whether the LLM can override the classifier, and the main concern at 50,000 records).
- **Video** — a link at the top of `transform_10.py` to a short video showing the flow running, the `weather_enriched` table with rows, and sample rows with recommendations.

**`verify_10.sql`:**

- **Step 6 — Verify with SQL** — a `verify_10.sql` file with two queries, each followed by its pasted result as a `--` comment: (1) a `LEFT JOIN` from `weather_raw` to `weather_enriched` on `date` with `WHERE ... IS NULL`, returning the dates that have no enrichment, with a "before" result and an "after" result; (2) a `GROUP BY good_for_running` count. A closing comment explains how Query 1 changed between runs (connecting it to incremental processing) and whether Query 2 matches the Step 5 Python count. If the student says they ran the transform before reading this step, an expected "before" result with an explanation is acceptable.

### Optional Deliverables/Tasks

- **Part 3 — (Optional) Practicum AWS Bridge: The Lambda Handler.** This entire part is an optional pilot. Do **not** fail or ask for revisions from a student who skipped any or all of Part 3, and do not count a missing `aws_bridge/` folder against them. If the student attempted Part 3, give feedback on what they submitted, using the notes below. A partial attempt is acceptable.
    - **Task 1 (setup)** — an `aws_bridge/` folder with the four provided files (`gradebook.py`, `submissions.json`, `event_schedule.json`, `event_function_url.json`). Files carried over from Weeks 8 and 9 are expected and must not be flagged as extra files. `gradebook.py` is provided code; do not review it as the student's work.
    - **Task 2 (`handler.py`)** — `BadEventError`, `parse_week(event)`, `latest_week(data)`, `calculate_submission_rate(data, week)`, and `lambda_handler(event, context)`. `Use exactly as written (later tasks depend on these names)`: the file name, these five names and their parameters, the logger name `"submission_alert"`, the response keys `"statusCode"`, `"headers"`, and `"body"`, and the five body keys `"cohort"`, `"week"`, `"submission_rate"`, `"threshold"`, and `"below_threshold"`. Behavior to check: Function URL events are recognized by `"requestContext"`, and their `"body"` string is parsed with `json.loads`; a missing or empty body means no week; invalid JSON, non-integer weeks, booleans, and weeks below 1 raise `BadEventError`; each student is counted once (a `set` of student IDs, or equivalent); bad requests return `400`; unexpected errors are not caught; the response body is a JSON string; one `INFO` JSON log line is written per successful run.
    - **Task 3 (`test_handler.py`)** — tests for the eight listed cases. The provided fixture and helper may be used as given. `Example — adapt to your own layout`: test names and structure. Expected values from the provided data: week 2 rate `92.5`, latest week `7`, week 7 rate `72.5`, week 5 rate `82.5`.
    - **Task 4 (run by hand)** — nothing to submit. Do not ask for evidence of it.
    - **Task 5 (`handler_notes.md`)** — (1) the scheduled event has no week, so the handler checks the latest week in the data; (2) Lambda uses the response for the Function URL trigger, where it becomes the HTTP response, while Scheduler calls the function asynchronously and discards the return value; (3) the row count reports 100% for week 2, because three students submitted twice, so 40 rows represent only 37 students. Accept any reasonable wording.

</details>
