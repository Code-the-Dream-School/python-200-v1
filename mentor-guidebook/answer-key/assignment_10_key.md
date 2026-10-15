# Assignment 10 Answer Key: Cloud ML (Double-Transform Pipeline)

**Mentor note:** Week 10 builds the Transform step — the Week 4 ML classifier predicts good/skip for each `weather_raw` row, then an LLM adds a one-sentence recommendation, and both land in `weather_enriched`. Warmups mix conceptual comment-answers with code; the project is the double-transform end-to-end, wrapped in a Prefect flow. Grade approach, correct incremental processing, and graceful LLM error handling. LLM summary text varies. The **video link is required**, but its content is not graded, because the AirHub reviewer cannot watch it. Mentors may watch it to give feedback. Two themes to verify: **ML vs. LLM role separation** and **incremental processing** (don't re-process already-enriched rows).

---

## Expected File Setup

Assignment lives in `assignments_10/`:

```
assignments_10/
├── warmup_10.py       # conceptual answers (comments) + code
├── transform_10.py    # double-transform pipeline, wrapped as a Prefect flow (video link in top comment)
├── verify_10.sql      # SQL verification queries, results pasted as -- comments
├── weather_model/     # WeatherClassifier component package copied from Week 4
└── models/            # weather_classifier.pkl copied from Week 4
```

Students who do the **optional** Practicum AWS Bridge (Part 3) also have an `aws_bridge/` folder. It holds `handler.py`, `test_handler.py`, `handler_notes.md`, the four provided files (`gradebook.py`, `submissions.json`, `event_schedule.json`, `event_function_url.json`), and their Week 8–9 bridge files.

Requires `supabase python-dotenv joblib scikit-learn pandas openai prefect`. Week 9 must have populated `weather_raw`; the Week 4 component must be in `weather_model/` and the model file in `models/`.

---

# Part 1: Warmup (`warmup_10.py`)

## ML vs. LLM in Pipelines

### ML/LLM Q1 — **Subjective**
Core distinction:
- The **ML classifier** produces a **structured, deterministic** output — a binary good/skip label + probability — from numeric features. Fast, cheap, consistent.
- The **LLM** produces **fluent natural-language** text (the recommendation). Good at phrasing, bad as a precise numeric classifier.
- Swapping them fails: an LLM making the binary call is slower, costlier, and non-deterministic (may vary run to run); an ML regression/classifier can't write a readable sentence. Right tool for right job.

### ML/LLM Q2 — **Objective** (tool-choice per task)
- Date string → day-of-week → **deterministic code** (`datetime`), no ML/LLM needed.
- Job posting → entry/mid/senior from freeform text → **LLM** (unstructured language understanding; no labeled training set implied).
- Customer churn from 15 numeric features + labeled data → **trained ML model** (classic supervised classification).
- Normalizing messy city names to canonical form → **LLM** (fuzzy, many variants) — accept deterministic code/lookup if the variants are bounded; reasoning matters.
- Summing a revenue column → **deterministic code** (never an LLM for arithmetic).

### ML/LLM Q3 — **Subjective**
Incremental processing = only process **new/unprocessed** records, not the whole table each run. Important because re-processing all 365 rows every run **wastes money** (repeat LLM API calls), **wastes time**, and risks overwriting/duplicating. The incremental check (skip dates already in `weather_enriched`) keeps runs cheap and idempotent.

## Prompt Design

### Prompt Q1 — **Objective (approach) + Subjective**
An alternative two-sentence system prompt (sentence 1 = prediction, sentence 2 = reasoning). Comment on validation change: the one-sentence check would need to **allow/expect two sentences** — e.g. adjust any sentence-count or length validation, or split on the two parts. Look for awareness that output-format changes require validation changes.

### Prompt Q2 — **Objective (approach)**
`call_with_retry(client, messages, max_retries=3)` calls `chat.completions.create()`, retries on **any exception** up to `max_retries` with a **2-second wait** between attempts, returns `None` on final failure:
```python
def call_with_retry(client, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return None
```
Comment: used in production to survive **transient API failures** (rate limits, timeouts, network blips) without crashing the whole pipeline.

---

# Part 2: Project — Double-Transform Pipeline (`transform_10.py`)

**Overall check:** reads unprocessed `weather_raw` rows, runs the ML model, adds an LLM sentence, upserts to `weather_enriched`. Must be incremental and must not crash on an LLM error.

### Step 1: Incremental Read — **Objective (approach)**
Fetches all `weather_raw` rows and all dates already in `weather_enriched`; computes the difference (unprocessed dates). Prints a summary: raw count, already-enriched count, to-be-processed count. On a fresh run all 365 process; on a second run, 0.

### Step 2: ML Transform — **Objective (approach)**
Constructs a `WeatherClassifier` from `models/weather_classifier.pkl` and calls `predict()` on the unprocessed row dicts. Each result is a `Prediction`; the student reads its `.label` ("good"/"skip") into `good_for_running` and its `.probability` into `confidence`, building records with `date`, `good_for_running`, `confidence`. Prints how many good days + confidence range. The component handles feature selection and column order internally, so students do not build a DataFrame or call `predict_proba` themselves. Common mistake: re-implementing the raw sklearn logic instead of using the component.

### Step 3: LLM Transform — **Objective (approach) + Subjective**
A system prompt + user-message function passing each day's features + the ML prediction to `gpt-4o-mini`; adds a one-sentence `llm_summary`. **Handles API errors with a fallback string** (not a crash). Progress print every 50 records. The prompt should feed the model the ML prediction so the sentence stays consistent with it.

### Step 4: Load — **Objective (approach)**
Upserts enrichment records into `weather_enriched`, prints the upserted count.

### Step 5: Verify — **Objective (approach) + Subjective**
Queries `weather_enriched`: total rows, five sample rows (`date`, `good_for_running`, `confidence`, `llm_summary`), count of good-for-running days. Comment evaluates a few summaries — a good one accurately reflects the features + prediction; a weak one might contradict the data or be generic. Look for genuine inspection.

### Step 6: Verify with SQL (`verify_10.sql`) — **Objective (approach) + Subjective**
A SQL cross-check of both tables, run in the Supabase SQL Editor. This is SQL review from Python for Data Analysis (`LEFT JOIN`, `GROUP BY`), plus the `IS NULL` check introduced in the Week 9 syntax reminder. Accept any query that answers the question; aliases and sort direction are the student's choice. Sample answers:
```sql
-- Query 1: Dates in weather_raw with no enrichment
SELECT r.date
FROM weather_raw r
LEFT JOIN weather_enriched e ON r.date = e.date
WHERE e.date IS NULL
ORDER BY r.date;

-- Query 2: Good vs. not good for running
SELECT good_for_running, COUNT(*) AS days
FROM weather_enriched
GROUP BY good_for_running;
```
**Expected results:**
- Query 1 **before** the first transform run: every date in `weather_raw`. That is usually **366 rows**, from `2023-01-01` to the date of the Week 9 CRUD Q1 test record. If the student deleted the test record, it is 365 rows ending on `2023-12-31`.
- Query 1 **after** the transform: **0 rows**. The SQL Editor shows "Success. No rows returned." This empty result is the correct answer.
- Query 2: two rows, one for `true` and one for `false`. The two counts add up to the total number of rows in `weather_enriched`, and the `true` count matches the Step 5 Python good-day count. The split itself varies by city and model.

**Closing comment:** A good answer says that Query 1 went from every date to no dates, because the transform processed everything that was not yet enriched. A strong answer adds that a second run would also start with zero dates to process, which is the incremental check from Step 1 working as intended.

If Query 1 still returns dates after the transform, the run probably crashed partway through, or the incremental logic in Step 1 has a bug. LLM errors alone do not cause this, because the fallback string still produces a row.

**Common trouble spots:**
- Joining in the wrong direction (`FROM weather_enriched LEFT JOIN weather_raw`). Because of the foreign key, every enriched date exists in `weather_raw`, so this query always returns zero rows, even before the transform runs.
- Checking the wrong column for NULL (`WHERE r.date IS NULL`). `r.date` is the primary key, so it is never NULL. Check the column from the right-hand table (`e.date`).
- Using `JOIN` (an inner join) instead of `LEFT JOIN`. An inner join drops the unmatched rows, which are the rows the query is looking for.
- Students who ran the transform before reading the step cannot produce a real "before" result. The assignment allows an expected result with an explanation instead.

### Step 7: Orchestrate with Prefect — **Objective (approach)**
Wraps the pipeline in a Prefect flow: each stage (read, classify, enrich, load) becomes an `@task`, and a `@flow(log_prints=True)` calls them in order. `transform_10.py` defines and runs the flow, and every task shows as completed. No retries, scheduling, or Prefect UI this week — that is Week 11. Accept any working flow with the four stages as tracked tasks.

### Step 8: Reflect — **Subjective**
5–6+ sentences on:
1. The model was trained on the student's own chosen city (from Week 3). If Week 9 loaded a **different** city, predictions may be **less accurate** because the thresholds learned in training reflect the training city's climate. Good answer engages with distribution shift.
2. The LLM is **purely additive** — it describes the prediction but can't override the classifier's good/skip decision. Implication: the ML model is the source of truth; a bad prediction produces a confident-but-wrong sentence.
3. Scaling to 50,000 records → main concern is usually **cost and latency of the per-row LLM calls** (365 → 50k is 137× the API spend/time). Fixes: batching, caching, cheaper/local model, parallelism, or only enriching a subset.

### Video — **Link required; content not graded**
A link must be present in the top comment of `transform_10.py`. The AirHub reviewer cannot watch the video, so do not fail a student for its length or content. Mentors may watch it to give feedback.

---

# Part 3: (Optional) Practicum AWS Bridge — The Lambda Handler

**Mentor note:** This part is an **optional pilot** this term. Never ask a student to revise because they skipped it. It goes with the optional lesson `lessons/10_llm_pipelines/05_aws_bridge_handler.md`. Students write the alert's Lambda handler, which handles two event types:
- **EventBridge Scheduler** sends a fixed JSON input, here `{}`, and calls the function asynchronously, so it discards the return value.
- **A Lambda Function URL** sends an HTTP event whose `body` is a JSON *string*, and it uses the returned `statusCode`/`headers`/`body` as the HTTP response.

No AWS account or moto is needed this week, because the tests set the settings through environment variables. The handler depends on the student's Week 9 `alert_settings.py`. The expected time is about two and a half hours plus the lesson.

**Expected numbers from the provided `submissions.json`** (40 students, weeks 1–7, with 8 resubmissions):

| Week | Rows | Different students | Rate | Below 80%? |
|---|---|---|---|---|
| 1 | 39 | 38 | 95.0 | No |
| 2 | 40 | 37 | 92.5 | No |
| 3 | 38 | 36 | 90.0 | No |
| 4 | 35 | 34 | 85.0 | No |
| 5 | 33 | 33 | 82.5 | No |
| 6 | 31 | 31 | 77.5 | Yes |
| 7 | 30 | 29 | 72.5 | Yes |

If a student's numbers match the "Rows" column divided by 40, they counted rows instead of students.

### Task 1: Setup — **Not assessed**
Week 8–9 files and the four provided files are expected. `gradebook.py` is provided code, so do not review it as the student's work.

### Task 2: `handler.py` — **Objective (approach)**
Names are exact, because Week 11 builds on this file. Reference solution:

```python
"""The submission alert's Lambda handler."""

import json
import logging

from alert_settings import get_alert_settings
from gradebook import fetch_submissions

# A named logger. On Lambda, its lines go to CloudWatch Logs automatically.
logger = logging.getLogger("submission_alert")
logger.setLevel(logging.INFO)


class BadEventError(Exception):
    """Raised when an event cannot be understood."""


def parse_week(event):
    """Return the week the caller asked for, or None if no week was given.

    A scheduled event is a plain dictionary (often empty). A Function URL
    event has a "requestContext" key, and it puts the caller's JSON in
    event["body"] as a string. The body can be missing or empty.
    """
    if "requestContext" in event:
        body = event.get("body")
        if not body:
            return None
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            raise BadEventError("The request body is not valid JSON.") from None
    else:
        payload = event

    week = payload.get("week")
    if week is None:
        return None
    if not isinstance(week, int) or isinstance(week, bool) or week < 1:
        raise BadEventError("'week' must be a positive whole number.")
    return week


def latest_week(data):
    """Return the highest week number that has any submissions."""
    return max(s["week"] for s in data["submissions"])


def calculate_submission_rate(data, week):
    """Return the percentage of the roster that submitted in this week.

    Students who resubmit appear more than once, so count each student once.
    """
    submitted = {s["student_id"] for s in data["submissions"] if s["week"] == week}
    return round(100 * len(submitted) / len(data["roster"]), 1)


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    try:
        requested_week = parse_week(event)
    except BadEventError as error:
        logger.warning(json.dumps({"error": str(error)}))
        return _response(400, {"error": str(error)})

    settings = get_alert_settings()
    data = fetch_submissions(settings["gradebook_token"])

    week = requested_week or latest_week(data)
    if week > latest_week(data):
        message = f"There is no submission data for week {week} yet."
        logger.warning(json.dumps({"error": message}))
        return _response(400, {"error": message})

    rate = calculate_submission_rate(data, week)
    result = {
        "cohort": data["cohort"],
        "week": week,
        "submission_rate": rate,
        "threshold": settings["threshold"],
        "below_threshold": rate < settings["threshold"],
    }
    logger.info(json.dumps(result))
    return _response(200, result)
```

Common mistakes:
- **Indexing the body as a dictionary** (`event["body"]["week"]`). This raises `TypeError: string indices must be integers`. The body is a JSON string, so it needs `json.loads`.
- **Detecting a Function URL event by `"body" in event`.** AWS can leave out `body` when a request has no data, so `"requestContext"` is the reliable marker. The assignment states this rule, so hold students to it gently. If a student detects by `body` and all their tests pass, mention why `requestContext` is safer, without asking for a revision.
- **Counting rows instead of students.** Week 2 then reports 100.0. Point the student to the week 2 test.
- **Accepting `True` as week 1.** `isinstance(True, int)` is `True` in Python, so the check needs `not isinstance(week, bool)` as well. This is a subtle Python detail. Accept a solution that misses it if the student's tests pass, but point it out.
- **Returning `body` as a dictionary instead of a string.** A Function URL would then not return valid JSON. Tests that call `json.loads(response["body"])` catch this.
- **Wrapping everything in `try/except Exception` and returning 500.** For a Function URL this produces a tidy response, but for a scheduled run Lambda would record a success, and the failure would be invisible. This is why the spec says to let unexpected exceptions happen.
- **Function URL body encoding.** For JSON requests, `isBase64Encoded` is `false`, which is the only case in this exercise. Real Function URLs base64-encode some non-text bodies. Students do not need to handle that.

### Task 3: `test_handler.py` — **Objective (approach)**
Eight cases. Reference tests:

```python
import json
from pathlib import Path

import pytest

from gradebook import fetch_submissions
from handler import (
    BadEventError,
    calculate_submission_rate,
    lambda_handler,
    latest_week,
    parse_week,
)

HERE = Path(__file__).parent


def load_event(name):
    return json.loads((HERE / name).read_text())


def url_event(body):
    """A minimal Function URL event with the given body string."""
    return {"requestContext": {"http": {"method": "POST"}}, "body": body}


@pytest.fixture
def data():
    return fetch_submissions("any-token")


@pytest.fixture(autouse=True)
def settings_in_environment(monkeypatch):
    # The handler reads its settings from environment variables in these tests,
    # so no Parameter Store (and no moto) is needed this week.
    monkeypatch.setenv("GRADEBOOK_TOKEN", "gb-test-token")
    monkeypatch.setenv("SUBMISSION_THRESHOLD", "80")


def test_schedule_event_has_no_week():
    assert parse_week(load_event("event_schedule.json")) is None


def test_function_url_event_without_body_has_no_week():
    assert parse_week({"requestContext": {"http": {"method": "GET"}}}) is None


def test_function_url_event_week_comes_from_body():
    assert parse_week(load_event("event_function_url.json")) == 5


@pytest.mark.parametrize("body", ["not json", '{"week": "five"}', '{"week": 0}', '{"week": true}'])
def test_bad_body_raises(body):
    with pytest.raises(BadEventError):
        parse_week(url_event(body))


def test_resubmissions_count_once(data):
    # Week 2 has 40 submission rows, but only 37 different students.
    assert calculate_submission_rate(data, 2) == 92.5


def test_latest_week(data):
    assert latest_week(data) == 7


def test_scheduled_run_checks_latest_week():
    response = lambda_handler(load_event("event_schedule.json"), None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["week"] == 7
    assert body["submission_rate"] == 72.5
    assert body["below_threshold"] is True


def test_manual_run_checks_requested_week():
    response = lambda_handler(load_event("event_function_url.json"), None)
    body = json.loads(response["body"])
    assert body["week"] == 5
    assert body["submission_rate"] == 82.5
    assert body["below_threshold"] is False


def test_bad_request_returns_400():
    response = lambda_handler(url_event("not json"), None)
    assert response["statusCode"] == 400


def test_future_week_returns_400():
    response = lambda_handler(url_event('{"week": 12}'), None)
    assert response["statusCode"] == 400


def test_handler_logs_one_result_line(caplog):
    with caplog.at_level("INFO"):
        lambda_handler({}, None)
    logged = [json.loads(r.getMessage()) for r in caplog.records if r.name == "submission_alert"]
    assert len(logged) == 1
    assert logged[0]["week"] == 7
```

The log test filters on `record.name == "submission_alert"`. This matters in Week 11: once `boto3` is involved, botocore writes its own `INFO` lines (for example, "Found credentials in environment variables"), and a test that reads every `INFO` line breaks.

### Task 4: Run by hand — **Not assessed**
Expected output for the scheduled event: status 200, week 7, rate 72.5, `below_threshold` true. The `VAR=value command` syntax works in macOS/Linux shells and Git Bash, but not in PowerShell or `cmd`.

### Task 5: `handler_notes.md` — **Subjective**
1. The scheduled event has no week, so the handler checks the latest week that has data.
2. The Function URL trigger uses the response as the HTTP response. Scheduler calls the function asynchronously and discards the return value. For a scheduled run, only an exception marks the run as failed.
3. It reports 100% for week 2 (40 rows out of 40 students). Three students resubmitted, so it counts them twice.
