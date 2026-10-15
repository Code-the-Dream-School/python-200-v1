# Week 11 Assignment: Cloud ETL Capstone

This is the capstone project for Python 200. You have spent ten weeks building toward this: a cloud ETL pipeline that extracts weather data from a live API, transforms it with an ML classifier and an LLM, loads the results to Supabase, and runs the whole thing as an orchestrated, observable Prefect flow. This week you build it yourself.

The warmup checks your understanding of Prefect and production patterns. The project is the pipeline.

---

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_11/`. Inside that folder, create:

1. `warmup_11.py` — warmup exercises (conceptual answers as comments, code as requested)
2. `etl_pipeline.py` — the complete ETL pipeline
3. `verify_11.sql` — your SQL summary report queries, with their results pasted as comments
4. `weather_model/` — copy your `WeatherClassifier` component package from Week 4 here
5. `models/` — copy your `weather_classifier.pkl` from Week 4 here
6. `outputs/pipeline_run.md` — a short written reflection on your run

If you choose to do the optional Practicum AWS Bridge in Part 3, also create an `aws_bridge/` folder inside `assignments_11/`. Part 3 lists the files that go in it.

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
4. Confirm the data in the Supabase dashboard. `weather_raw` should have 365 rows, or 366 if your Week 9 test record is still there. `weather_enriched` should have the same number of rows as `weather_raw`. It cannot have more, because the foreign key requires every row in `weather_enriched` to match a date in `weather_raw`.

## SQL Summary Report

After your pipeline finishes, write a short summary report in SQL. You will run it in the Supabase SQL Editor, the same way you did in Weeks 9 and 10. This step reviews SQL you learned in Python for Data Analysis. If you need a reminder of the syntax, open the [SQL syntax reminder](09_cloud_AI.md#step-5-verify-with-sql) in the Week 9 assignment.

Create a file called `verify_11.sql` and write two queries in it:

1. **Raw table summary.** Write one query that returns the total number of rows in `weather_raw` and the most recent `loaded_at` timestamp.
2. **Enriched table summary.** Write one query that returns three values from `weather_enriched`: the total number of rows, the most recent `enriched_at` timestamp, and the percentage of days that are good for running. Round the percentage to one decimal place.

For the percentage, use a subquery to count the days where `good_for_running = true`, and then divide that count by `COUNT(*)`. Multiply by `100.0`, not `100`. If you divide one whole number by another, SQL drops the decimal part of the result, so `100 * 150 / 365` returns `41` instead of `41.1`.

Paste each result below its query as a SQL comment (lines that start with `--`), using the same format as `verify_09.sql`. Run one query at a time, because the SQL Editor shows only the result of the last query you run.

At the bottom of `verify_11.sql`, add a comment that answers these questions:

- Look at the most recent `loaded_at` and `enriched_at` timestamps. Are they from the pipeline run you just finished? Explain why or why not. **Hint:** reread what `DEFAULT now()` does in the Week 9 tables lesson. Then think about which dates your `transform` task skipped on this run.
- Is your percentage of good days for running what you expected for your city? Explain your answer in one or two sentences.

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

# Part 3: (Optional) Practicum AWS Bridge — Assembly

> **This entire part is optional.** The Practicum AWS Bridge is a pilot this term. You can skip all of Part 3 without any effect on your grade. Your capstone is Part 2.

This part goes with the optional lesson [Practicum AWS Bridge, Part 4: Assembly](../lessons/11_cloud_ETL/04_aws_bridge_assembly.md). The bridge builds an automatic alert that tells the Code the Dream teaching team when fewer than 80% of students submit their weekly assignment. This week, you finish the alert. The handler sends the submission rate to CloudWatch as a metric, and you define the CloudWatch alarm that watches it. Then you test the whole feature on your own computer with `moto`. You do not need an AWS account.

Plan for about two hours, in addition to the optional lesson.

## Task 1: (Optional) Set Up the Folder

Create a folder called `aws_bridge/` inside `assignments_11/`, and copy everything from `assignments_10/aws_bridge/` into it. **This week adds files to that folder and changes two of them. Keep all your files from Weeks 8, 9, and 10.**

This part uses your code from Weeks 9 and 10. Task 5 also uses your Week 8 `iam_checker.py` and `submission_alert_policy.json`. If you skipped Week 8, skip Task 5.

## Task 2: (Optional) Write the Metric and Alarm Functions

Create `aws_bridge/metrics.py`. Use exactly as written: the file name, the constant names and values below, and the two function names and their parameters. Your tests import them.

Define these four constants at the top of the file:

```python
NAMESPACE = "CTD/Submissions"
METRIC_NAME = "SubmissionRate"
ALARM_NAME = "low-submission-rate"
REGION = "us-east-1"
```

Then write two functions. In both, if `cloudwatch_client` is `None`, create a client with `boto3.client("cloudwatch", region_name=REGION)`.

1. **`publish_submission_rate(rate, cohort, cloudwatch_client=None)`** sends one data point with `put_metric_data`. Use the namespace `NAMESPACE`, the metric name `METRIC_NAME`, the value `rate`, the unit `"Percent"`, and one dimension: `{"Name": "Cohort", "Value": cohort}`.

2. **`create_low_submission_alarm(threshold, cohort, cloudwatch_client=None)`** defines the alarm with `put_metric_alarm`. Use these settings:
    - `AlarmName`: `ALARM_NAME`
    - `Namespace`, `MetricName`, and `Dimensions`: the same values that `publish_submission_rate` uses
    - `Statistic`: `"Minimum"`, `Period`: `86400`, `EvaluationPeriods`: `1`
    - `Threshold`: `threshold`, `ComparisonOperator`: `"LessThanThreshold"`
    - `TreatMissingData`: `"notBreaching"`
    - `AlarmDescription`: a short sentence of your choice

## Task 3: (Optional) Publish the Rate from the Handler

Update `aws_bridge/handler.py` so that a **scheduled** run calls `publish_submission_rate` with the submission rate and the cohort name, before it writes its log line and returns. A run through the Function URL does not publish anything. A scheduled run is one where `parse_week` returned `None`.

Your Week 10 tests in `test_handler.py` now need a fake CloudWatch, because a scheduled run calls AWS. Add moto to the `autouse` fixture. Example — this is one way to change the Week 10 fixture:

```python
@pytest.fixture(autouse=True)
def settings_in_environment(monkeypatch):
    monkeypatch.setenv("GRADEBOOK_TOKEN", "gb-test-token")
    monkeypatch.setenv("SUBMISSION_THRESHOLD", "80")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    with mock_aws():
        yield
```

Run `pytest` and confirm that your Week 10 tests still pass.

## Task 4: (Optional) Test the Whole Alert

Create `aws_bridge/test_end_to_end.py`. Write a fixture that does all of the following, and then yields a CloudWatch client:

- Starts `mock_aws()`
- Sets `AWS_DEFAULT_REGION`, and removes the `GRADEBOOK_TOKEN` and `SUBMISSION_THRESHOLD` environment variables, so that the handler has to read Parameter Store
- Creates the `SecureString` parameter `/ctd/submission-alert/gradebook_token` and the `String` parameter `/ctd/submission-alert/submission_threshold` with the value `"80"`

Write tests for at least these three cases:

1. A scheduled run (`lambda_handler({}, None)`) returns a submission rate of `72.5`, and `get_metric_statistics` returns exactly one published value, `72.5`.
2. A Function URL run for week 5 publishes nothing, so `get_metric_statistics` returns no data points.
3. After `create_low_submission_alarm(80, "python200-fall-2026", ...)`, `describe_alarms` returns an alarm whose namespace, metric name, dimensions, threshold, and comparison operator match the values in Task 2.

**Tip:** `get_metric_statistics` needs a time range. A range from one hour before `datetime.now(timezone.utc)` to one hour after it, with `Period=3600`, includes a data point that your test just published.

## Task 5: (Optional) Write the Pre-Deploy Permission Test

Create `aws_bridge/test_permissions.py`. It uses your Week 8 `is_allowed` function and `submission_alert_policy.json`. Write two lists of `(action, resource)` pairs, and test each list with `@pytest.mark.parametrize`.

In both lists, use the account ID `123456789012` and the region `us-east-1`.

**Calls the handler makes.** Your test checks that `is_allowed` returns `True` for every pair:

- `ssm:GetParameter` on the `gradebook_token` parameter, and on the `submission_threshold` parameter
- `cloudwatch:PutMetricData` on `*`
- `logs:CreateLogStream` and `logs:PutLogEvents` on a log stream in the log group `/aws/lambda/submission-alert`. Example — use any stream name, such as `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/submission-alert:log-stream:2026/10/26/abc123`

**Calls the handler never makes.** Your test checks that `is_allowed` returns `False` for every pair. Include at least these four:

- `ssm:PutParameter` on the `submission_threshold` parameter
- `ssm:GetParameter` on `/ctd/submission-alert/admin/override`
- `cloudwatch:PutMetricAlarm` on `*`
- `s3:GetObject` on `arn:aws:s3:::ctd-gradebook/week07.csv`

## Task 6: (Optional) Run the Alert Locally, and Reflect

Create `aws_bridge/run_local.py`, a script that does what EventBridge Scheduler would do, but on a fake AWS. Inside one `with mock_aws():` block, it does the following:

1. It creates the two parameters and the alarm, and it prints a message for each step.
2. It calls `lambda_handler({}, None)` and prints the response body.
3. It reads the published metric with `get_metric_statistics` and prints the value.
4. It prints the alarm's state from `describe_alarms`.

Run the script with `python run_local.py`. The alarm's state is `OK`, because moto does not evaluate alarms.

Then create `aws_bridge/bridge_reflection.md` and answer these questions in two or three sentences each:

1. Why does the alert's role allow `cloudwatch:PutMetricData` but not `cloudwatch:PutMetricAlarm`?
2. Name two things that your local tests confirm, and one thing that only a real deployment on AWS can confirm.
3. Why does the handler publish the metric only on scheduled runs?

---

Congratulations! With this step, you have finished Python for Cloud & AI. You built a full cloud ETL pipeline from scratch — extract, transform with an ML model and an LLM, load to a cloud database, orchestrated and observable with Prefect. That is a genuinely production-relevant workflow.

---

<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

### Required Deliverables/Tasks

**General grading notes:**

- **Part 3 (Practicum AWS Bridge) is entirely optional.** It is a pilot this term, and it is separate from the capstone. All of its tasks are listed under Optional Deliverables/Tasks below. Never fail a student for skipping it.

- **This is a capstone written to a specification, not a reference implementation.** The assignment says to write the pipeline from scratch, so implementations vary widely. Grade whether each task meets its stated requirements, not whether the code matches any particular solution.
- **Student-chosen values and generated text vary.** The city, the specific rows, and every LLM `llm_summary` differ between students and runs. Do not fail a student for text or numbers that differ from a reference. `weather_raw` should have roughly 365 rows for a full year.
- **External artifacts and copied files cannot be inspected.** The reviewer cannot see the student's Supabase project, the Prefect UI, the video, or their filesystem, and cannot confirm that `weather_model/` and `models/weather_classifier.pkl` were copied in. Grade the submitted code and the written reflection; do not fail a student for an unverifiable dashboard, UI, video, or file.
- **SQL queries vary.** Accept any query in `verify_11.sql` that returns the requested values. Aliases are the student's choice. The assignment asks for a subquery, but a student who uses a `CASE` expression instead (for example, `SUM(CASE WHEN good_for_running THEN 1 ELSE 0 END)`) is also correct. The pasted counts, timestamps, and percentage vary by student. The timestamps are usually *not* from the current run, and that is the expected result (see the answer key).
- **Names and Prefect parameters are exact.** `Use exactly as written`: the tables `weather_raw`/`weather_enriched` and their columns; the four task names `extract`, `load_raw`, `transform`, `load_enriched`; the retry parameters given per task (e.g. `retries=2, retry_delay_seconds=10`); `on_conflict="date"`; `get_run_logger`; the `WeatherClassifier` component and its `Prediction` `label`/`probability`; and the model id `gpt-4o-mini`. `Example — adapt to your own values`: the chosen city and the exact prompt wording.
- - **Video link** — a link to a short narrated video posted somewhere accessible, pasted in etl_pipeline.py. The reviewer cannot open or verify the video; grade only that a link is present, and do not fail for length or content that cannot be inspected.

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
- **SQL summary report** — a `verify_11.sql` file with two queries, each followed by its pasted result as a `--` comment: (1) the row count and most recent `loaded_at` of `weather_raw`; (2) the row count, most recent `enriched_at`, and percentage of good-for-running days (rounded to one decimal) of `weather_enriched`, using a subquery (a `CASE` expression is also acceptable). A closing comment explains whether the two timestamps come from the current run and why, and comments on whether the good-day percentage is expected for the city.
- **Reflection** — `outputs/pipeline_run.md` (5–7 sentences) covering the first-run outcome and any fixes, what the Prefect UI showed and whether any task retried, an assessment of a few `llm_summary` rows, and one change for a daily scheduled deployment.
- **Video** — a link at the top of `etl_pipeline.py` to a short video showing the pipeline running to completion, the Prefect UI with all four tasks completed and the transform logs, and the `weather_enriched` table with the `llm_summary` column.

### Optional Deliverables/Tasks

- **Part 3 — (Optional) Practicum AWS Bridge: Assembly.** This entire part is an optional pilot, and it is separate from the capstone in Part 2. Do **not** fail or ask for revisions from a student who skipped any or all of Part 3, and do not count a missing `aws_bridge/` folder against them. If the student attempted Part 3, give feedback on what they submitted, using the notes below. A partial attempt is acceptable.
    - **Task 1 (setup)** — an `aws_bridge/` folder. Files carried over from Weeks 8, 9, and 10 are expected and must not be flagged as extra files. `gradebook.py` is provided code; do not review it as the student's work. A student who skipped Week 8 also skips Task 5.
    - **Task 2 (`metrics.py`)** — the constants `NAMESPACE`, `METRIC_NAME`, `ALARM_NAME`, and `REGION`, and the functions `publish_submission_rate(rate, cohort, cloudwatch_client=None)` and `create_low_submission_alarm(threshold, cohort, cloudwatch_client=None)`. `Use exactly as written (later tasks depend on these names)`: the file name, constant names and values, function names and parameters, and the alarm settings listed in Task 2. `Example — adapt to your own layout`: the `AlarmDescription` text.
    - **Task 3 (handler update)** — `handler.py` calls `publish_submission_rate` only on scheduled runs (when `parse_week` returned `None`), and `test_handler.py` starts moto in its fixture. `Example — adapt to your own layout`: the exact fixture code.
    - **Task 4 (`test_end_to_end.py`)** — a moto fixture that creates the two parameters and removes the two environment variables, plus tests for the three listed cases: a scheduled run publishes `72.5`; a Function URL run publishes nothing; the alarm's namespace, metric name, dimensions, threshold, and comparison operator match.
    - **Task 5 (`test_permissions.py`)** — two parametrized lists that use the Week 8 `is_allowed`: the five calls the handler makes are all allowed, and at least the four listed calls it never makes are all not allowed. `Example — adapt to your own layout`: the log stream name.
    - **Task 6 (`run_local.py` and `bridge_reflection.md`)** — a script that, inside `mock_aws()`, creates the parameters and alarm, calls the handler with `{}`, and prints the response body, the published metric value, and the alarm state. The reflection answers: (1) the function publishes metrics but never creates the alarm, which a person or deployment script creates once, so least privilege leaves `PutMetricAlarm` out; (2) the tests confirm, for example, that the correct value is published, that the alarm watches the correct metric, and that the policy allows the needed calls, while only a deployment confirms, for example, that CloudWatch changes the alarm's state or that real IAM allows the calls; (3) the alarm treats each data point as the current week's result, so publishing an old week from a manual check would mislead it. Accept any reasonable wording.

</details>
