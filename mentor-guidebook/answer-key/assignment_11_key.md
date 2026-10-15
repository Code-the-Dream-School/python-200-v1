# Assignment 11 Answer Key: Cloud ETL Capstone

**Mentor note:** This is the **capstone** — a full Prefect ETL flow: Extract (Open-Meteo) → Load raw (Supabase) → Transform (Week 4 `WeatherClassifier` component + LLM) → Load enriched, orchestrated and observable in the Prefect UI. Warmups mix Prefect/production concept answers with small code stubs; the project pulls together everything from Weeks 4, 9, and 10. Grade the flow structure, task decorators, incremental/idempotent design, and error handling. The **video link is required**, but its content is not graded, because the AirHub reviewer cannot watch it. Mentors may watch it to give feedback. The decorator/stub questions have exact expected answers (below); the pipeline itself is approach-graded.

---

## Expected File Setup

Assignment lives in `assignments_11/`:

```
assignments_11/
├── warmup_11.py            # concept answers (comments) + code stubs
├── etl_pipeline.py         # full Prefect flow (video link in top comment)
├── verify_11.sql           # SQL summary report, results pasted as -- comments
├── weather_model/          # copied WeatherClassifier component package from Week 4
├── models/                 # weather_classifier.pkl from Week 4
└── outputs/
    └── pipeline_run.md      # written reflection on the run
```

Students who do the **optional** Practicum AWS Bridge (Part 3) also have an `aws_bridge/` folder. It holds `metrics.py`, `test_end_to_end.py`, `test_permissions.py`, `run_local.py`, `bridge_reflection.md`, an updated `handler.py` and `test_handler.py`, and their Week 8–10 bridge files. The bridge is **not** part of the capstone.

Requires `prefect requests openai python-dotenv supabase joblib scikit-learn pandas`. Week 9 must have populated `weather_raw`; the Week 4 `weather_model/` package must be copied in, and the Week 4 model files must be in `models/`.

---

# Part 1: Warmup (`warmup_11.py`)

## Prefect Orchestration

### Prefect Q1 — **Objective (concept)**
`@task` = a single unit of work (one step, retryable, observable); `@flow` = the orchestrator that calls tasks in order. The C→F helper (pure, in-memory, no I/O) **does not need `@task`** — tasks add overhead and are most valuable for I/O or failure-prone steps. Wrapping a trivial pure function just clutters the run graph. (Accept "you could, but it's unnecessary" with that reasoning.)

### Prefect Q2 — **Objective** (exact)
```python
@task(retries=3, retry_delay_seconds=30)
```

Also correct: `@task(name="call_api", retries=3, retry_delay_seconds=30)`. Prefect uses the function name as the task name by default, so the `name=` argument is optional. The retry values must be exactly `retries=3` and `retry_delay_seconds=30`.

### Prefect Q3 — **Subjective**
Where to look when `transform` failed: the **Prefect UI**, the failed flow run → the `transform` task run → its **Logs** (and state/exception details). Expect to find the **traceback / error message**, which task failed and when, retry attempts, and the log output leading up to the failure. Good answer names the logs/task-run detail view specifically.

## Production Patterns

### Production Q1 — **Objective (concept)**
`raise_for_status()` raises an exception on a 4xx/5xx HTTP response. Better than `if status != 200: print(...)` because the print **doesn't stop execution** — downstream tasks run on bad/empty data. With `raise_for_status()`, a 500 **raises**, the task fails, and Prefect **halts downstream tasks** (and can retry). With the print approach, the pipeline continues silently and corrupts later steps.

### Production Q2 — **Objective (concept)**
`upsert(on_conflict="date")` on re-run **updates existing rows instead of erroring on duplicates**, so re-running from the start after a crash is safe (idempotent). Plain `insert` would **fail on the already-loaded rows** (primary-key violation) or create duplicates — forcing manual cleanup before re-running.

### Production Q3 — **Objective** (stub)
```python
@task
def load_enriched(enrichment_records: list):
    logger = get_run_logger()
    logger.info(f"Upserted {len(enrichment_records)} enrichment records")
```
Check: uses `get_run_logger()`, logs an INFO line with the count, accepts the list arg.

### Production Q4 — **Subjective**
The incremental check (skip dates already in `weather_enriched`) makes the transform idempotent — re-runs process only new rows, so running twice ≠ double work. Removing it and re-processing all 365 every run means: **cost** (repeat LLM calls add up), **time** (calling the classifier and the LLM again for records that are already done), and **data correctness** (redundant/overwritten enrichment, wasted API quota). Same lesson as Week 10's incremental step.

---

# Part 2: Project — Full ETL Pipeline (`etl_pipeline.py`)

**Overall check:** four Prefect tasks wired into one flow, correct decorators, incremental + idempotent, graceful LLM fallback. Students are told to write it themselves using the lessons as a guide (not copy verbatim).

### extract task — **Objective (approach)**
`@task(retries=2, retry_delay_seconds=10)`; calls Open-Meteo for 2023 with the four variables; uses `raise_for_status()`; converts columnar response to row dicts; prints record count; returns the list.

### load_raw task — **Objective (approach)**
`@task(retries=2, retry_delay_seconds=5)`; upserts raw records into `weather_raw` with `on_conflict="date"`; prints upserted count.

### transform task — **Objective (approach)**
`@task`; incremental check (fetch existing `weather_enriched` dates, skip them); uses the `WeatherClassifier` component (loaded from `models/weather_classifier.pkl`) to classify the unprocessed records, reading each `Prediction`'s `label` and `probability`; calls OpenAI for a one-sentence rec per record; **graceful LLM fallback string** on error; progress print every 50; returns the enrichment records. This is the most complex task — verify the incremental skip and the error handling both exist.

### load_enriched task — **Objective (approach)**
`@task(retries=2, retry_delay_seconds=5)`; **guards against an empty list** (prints + returns early); upserts into `weather_enriched` with `on_conflict="date"`; prints upserted count. The empty-list guard is a common miss — without it a no-op run can error.

### Flow — **Objective (approach)**
`@flow(log_prints=True)`; calls the four tasks in the correct order (extract → load_raw → transform → load_enriched); prints a final completion message.

### Running and Verifying — **Objective (approach)**
Runs with `prefect server start` + `python etl_pipeline.py`; all four tasks show *Completed* in the UI at `localhost:4200`; `weather_raw` has 365 rows (366 if the Week 9 CRUD Q1 test record is still there), and `weather_enriched` has the same number. `weather_enriched` can never have more rows than `weather_raw`, because its `date` column is a foreign key to `weather_raw.date`.

### SQL Summary Report (`verify_11.sql`) — **Objective (approach) + Subjective**
A summary report of both tables, run in the Supabase SQL Editor. This is SQL review from Python for Data Analysis (aggregation and subqueries), not new material. Accept any query that returns the requested values. Sample answers:
```sql
-- Query 1: Raw table summary
SELECT
  COUNT(*)       AS raw_rows,
  MAX(loaded_at) AS last_loaded
FROM weather_raw;

-- Query 2: Enriched table summary
SELECT
  COUNT(*)         AS enriched_rows,
  MAX(enriched_at) AS last_enriched,
  ROUND(100.0 * (SELECT COUNT(*) FROM weather_enriched WHERE good_for_running = true) / COUNT(*), 1) AS pct_good
FROM weather_enriched;
```
The subquery counts the good days, and the outer `COUNT(*)` counts all days. Python for Data Analysis did not teach `CASE`, so the assignment asks for a subquery. A student who already knows `CASE` and writes `ROUND(100.0 * SUM(CASE WHEN good_for_running THEN 1 ELSE 0 END) / COUNT(*), 1)` is also correct.

**Expected results:**
- Query 1: 365 or 366 rows (see Running and Verifying). `last_loaded` is from **Week 9**, not from today.
- Query 2: the same row count as Query 1. `last_enriched` is from **Week 10**, not from today. `pct_good` varies by city and model.

**Why the timestamps are old (the key thing to look for in the closing comment):**
- `loaded_at` uses `DEFAULT now()`, which fills the column only when a row is **first inserted**. The `load_raw` task's upsert updates the four weather columns on rows that already exist, but it does not send `loaded_at`, so Postgres keeps the original Week 9 timestamp.
- `enriched_at` also comes from `DEFAULT now()`. In addition, the `transform` task's incremental check skipped every date, because all of them were enriched in Week 10. So `load_enriched` received an empty list and wrote nothing.
- A good answer explains at least one of these. A strong answer explains both and connects them to idempotency: re-running the pipeline did not change the enriched data.

Exceptions: if the student deleted rows, recreated the tables, or used a new Supabase project before this run, the timestamps *will* be from today. Accept this if the student explains it.

**Percentage comment:** this question is subjective. Look for a reason tied to the city's climate, for example "Phoenix is very hot in summer, so I expected fewer good days."

**Common trouble spots:**
- Multiplying by `100` instead of `100.0`. Integer division drops the decimal, so the percentage comes out as a whole number. If the student divides before multiplying (`(SELECT COUNT(*) ...) / COUNT(*) * 100`), the result is `0`. The assignment warns about this, but it is still the most likely mistake.
- Writing `WHERE good_for_running = 1`. This is a habit from SQLite, which Python for Data Analysis used. PostgreSQL raises an error (`operator does not exist: boolean = integer`). The fix is `= true`. The Week 9 syntax reminder covers this.
- Timestamps are shown in UTC (`+00`), so they may look several hours off from the student's local time. This is expected.

### Reflection (`outputs/pipeline_run.md`) — **Subjective**
5–7 sentences covering: clean run or what failed/how fixed; what the Prefect UI showed and whether tasks retried; a look at a few `weather_enriched` rows (one standout summary, good or bad, with why); and one change for a daily-scheduled deployment (e.g. switch to the forecast API for yesterday's data, add a Prefect **schedule/deployment**, alerting on failure, secrets management). Look for genuine engagement, especially with the scheduling question.

### Video — **Link required; content not graded**
A link must be present in the top comment of `etl_pipeline.py`. The video should show the pipeline running, the Prefect UI with all tasks Completed and the transform logs, and the populated `weather_enriched` table. The AirHub reviewer cannot watch it, so do not fail a student for its length or content. Mentors may watch it to give feedback.

---

# Part 3: (Optional) Practicum AWS Bridge — Assembly

**Mentor note:** This part is an **optional pilot**, and it is separate from the capstone. Never ask a student to revise because they skipped it, and do not let it affect how you assess Part 2. It goes with the optional lesson `lessons/11_cloud_ETL/04_aws_bridge_assembly.md`. The handler now publishes the submission rate to CloudWatch as a custom metric. A CloudWatch alarm (threshold 80, `LessThanThreshold`) watches that metric, and the whole alert is tested locally with moto. The expected time is about two hours plus the lesson.

**Two moto limits to know before helping a student:**
- **moto stores alarms but never evaluates them.** `describe_alarms` always shows `StateValue: "OK"`, even after a 72.5 is published. This is expected. If a student thinks their alarm is broken because it stays `OK`, it is not.
- **moto does not enforce IAM by default.** That is why Task 5 checks the policy with the Week 8 checker instead.

### Task 1: Setup — **Not assessed**
Week 8–10 files are expected. A student who skipped Week 8 skips Task 5.

### Task 2: `metrics.py` — **Objective (approach)**
Reference solution:

```python
"""Send the submission rate to CloudWatch and define the low-submission alarm."""

import boto3

NAMESPACE = "CTD/Submissions"
METRIC_NAME = "SubmissionRate"
ALARM_NAME = "low-submission-rate"
REGION = "us-east-1"


def _cloudwatch(client):
    return client or boto3.client("cloudwatch", region_name=REGION)


def publish_submission_rate(rate, cohort, cloudwatch_client=None):
    """Send one SubmissionRate data point for this cohort to CloudWatch."""
    _cloudwatch(cloudwatch_client).put_metric_data(
        Namespace=NAMESPACE,
        MetricData=[
            {
                "MetricName": METRIC_NAME,
                "Value": rate,
                "Unit": "Percent",
                "Dimensions": [{"Name": "Cohort", "Value": cohort}],
            }
        ],
    )


def create_low_submission_alarm(threshold, cohort, cloudwatch_client=None):
    """Create (or update) the alarm that fires when the rate drops below the threshold.

    A team member or a deployment script runs this once. The Lambda function
    does not run it, so the function's role does not need this permission.
    """
    _cloudwatch(cloudwatch_client).put_metric_alarm(
        AlarmName=ALARM_NAME,
        AlarmDescription=f"Fewer than {threshold:g}% of {cohort} submitted this week.",
        Namespace=NAMESPACE,
        MetricName=METRIC_NAME,
        Dimensions=[{"Name": "Cohort", "Value": cohort}],
        Statistic="Minimum",
        Period=86400,
        EvaluationPeriods=1,
        Threshold=threshold,
        ComparisonOperator="LessThanThreshold",
        TreatMissingData="notBreaching",
    )
```

The alarm uses `Minimum` over a one-day period with `notBreaching`. The metric is published once a week, so on the publishing day the one data point is the minimum, and on other days missing data counts as fine. The alarm goes to `ALARM` on a low week and back to `OK` the next day. That is acceptable for a weekly alert, because the notification happens when the state changes to `ALARM`. Students do not need to explain this.

### Task 3: Handler update — **Objective (approach)**
The end of `lambda_handler` becomes:

```python
    rate = calculate_submission_rate(data, week)
    result = {
        "cohort": data["cohort"],
        "week": week,
        "submission_rate": rate,
        "threshold": settings["threshold"],
        "below_threshold": rate < settings["threshold"],
    }
    # Only scheduled runs feed the alarm. A manual check of an old week should
    # not change what the alarm sees for the current week.
    if requested_week is None:
        publish_submission_rate(rate, data["cohort"])
    logger.info(json.dumps(result))
    return _response(200, result)
```

The Week 10 `test_handler.py` fixture gains `AWS_DEFAULT_REGION` and `with mock_aws(): yield`. Without this, the scheduled-run tests try to reach real AWS and fail, usually with a credentials error. Most students will hit this error before they read the Task 3 instructions about the fixture. That is a normal and useful moment.

### Task 4: `test_end_to_end.py` — **Objective (approach)**

```python
"""Run the whole alert on a fake AWS: Parameter Store, the handler, and CloudWatch."""

import json
from datetime import datetime, timedelta, timezone

import boto3
import pytest
from moto import mock_aws

from handler import lambda_handler
from metrics import ALARM_NAME, METRIC_NAME, NAMESPACE, create_low_submission_alarm

COHORT = "python200-fall-2026"


@pytest.fixture
def aws(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    # No environment variables: the handler has to read Parameter Store.
    monkeypatch.delenv("GRADEBOOK_TOKEN", raising=False)
    monkeypatch.delenv("SUBMISSION_THRESHOLD", raising=False)
    with mock_aws():
        ssm = boto3.client("ssm", region_name="us-east-1")
        ssm.put_parameter(Name="/ctd/submission-alert/gradebook_token",
                          Value="gb-test-token", Type="SecureString")
        ssm.put_parameter(Name="/ctd/submission-alert/submission_threshold",
                          Value="80", Type="String")
        yield boto3.client("cloudwatch", region_name="us-east-1")


def published_rates(cloudwatch):
    now = datetime.now(timezone.utc)
    stats = cloudwatch.get_metric_statistics(
        Namespace=NAMESPACE,
        MetricName=METRIC_NAME,
        Dimensions=[{"Name": "Cohort", "Value": COHORT}],
        StartTime=now - timedelta(hours=1),
        EndTime=now + timedelta(hours=1),
        Period=3600,
        Statistics=["Minimum"],
    )
    return [point["Minimum"] for point in stats["Datapoints"]]


def test_scheduled_run_publishes_the_rate(aws):
    response = lambda_handler({}, None)
    assert json.loads(response["body"])["submission_rate"] == 72.5
    assert published_rates(aws) == [72.5]


def test_manual_run_does_not_publish(aws):
    lambda_handler({"requestContext": {}, "body": '{"week": 5}'}, None)
    assert published_rates(aws) == []


def test_alarm_watches_the_metric(aws):
    create_low_submission_alarm(80, COHORT, aws)
    alarm = aws.describe_alarms(AlarmNames=[ALARM_NAME])["MetricAlarms"][0]
    assert alarm["Namespace"] == NAMESPACE
    assert alarm["MetricName"] == METRIC_NAME
    assert alarm["Threshold"] == 80
    assert alarm["ComparisonOperator"] == "LessThanThreshold"
    assert alarm["Dimensions"] == [{"Name": "Cohort", "Value": COHORT}]
```

Common mistakes:
- **A dimension mismatch** between `publish_submission_rate` and the test's `get_metric_statistics` call (for example, a different cohort string). The query then returns no data points, and the scheduled-run test fails with `[] != [72.5]`.
- **A time range that misses the data point.** moto timestamps the data point with the current UTC time. A range built with `datetime.now()` (local time, no time zone) can miss it.
- **Forgetting to remove the environment variables** in the fixture. The handler then reads them instead of Parameter Store, and the test still passes, but it no longer tests the Parameter Store path. This is worth pointing out, but it is not a failure.

### Task 5: `test_permissions.py` — **Objective (approach)**

```python
"""A pre-deploy check: the alert's role allows what the handler uses, and no more."""

from pathlib import Path

import pytest

from iam_checker import is_allowed, load_policy

ACCOUNT = "123456789012"
PARAM = f"arn:aws:ssm:us-east-1:{ACCOUNT}:parameter/ctd/submission-alert/"
LOG_GROUP = f"arn:aws:logs:us-east-1:{ACCOUNT}:log-group:/aws/lambda/submission-alert:"

# Every AWS call the deployed handler makes, and the resource it touches.
NEEDED = [
    ("ssm:GetParameter", PARAM + "gradebook_token"),
    ("ssm:GetParameter", PARAM + "submission_threshold"),
    ("cloudwatch:PutMetricData", "*"),
    ("logs:CreateLogStream", LOG_GROUP + "log-stream:2026/10/26/abc123"),
    ("logs:PutLogEvents", LOG_GROUP + "log-stream:2026/10/26/abc123"),
]

# Things the handler never does, so its role must not allow them.
NOT_NEEDED = [
    ("ssm:PutParameter", PARAM + "submission_threshold"),
    ("ssm:GetParameter", PARAM + "admin/override"),
    ("cloudwatch:PutMetricAlarm", "*"),
    ("cloudwatch:DeleteAlarms", "*"),
    ("s3:GetObject", "arn:aws:s3:::ctd-gradebook/week07.csv"),
]


@pytest.fixture
def policy():
    return load_policy(Path(__file__).parent / "submission_alert_policy.json")


@pytest.mark.parametrize("action, resource", NEEDED)
def test_role_allows_what_handler_needs(policy, action, resource):
    assert is_allowed(policy, action, resource)


@pytest.mark.parametrize("action, resource", NOT_NEEDED)
def test_role_denies_what_handler_does_not_need(policy, action, resource):
    assert not is_allowed(policy, action, resource)
```

The KMS question: reading a `SecureString` encrypted with the default AWS-managed key (`aws/ssm`) does not need a separate `kms:Decrypt` permission in the role. A customer-managed key would need one. Students do not need to know this. It may come up in practicum.

The log group: the policy has no `logs:CreateLogGroup`, because the bridge assumes that the log group `/aws/lambda/submission-alert` is created at deployment. A Lambda function without this permission cannot create its log group the first time it runs, and its first logs would be lost. If a student asks, this is a good practicum topic.

### Task 6: `run_local.py` and `bridge_reflection.md` — **Objective (approach) + Subjective**
Reference driver. It includes one extra step, a manual check of week 5, which the assignment does not require:

```python
"""Simulate one scheduled run of the submission alert on a fake AWS."""

import json
from datetime import datetime, timedelta, timezone

import boto3
from moto import mock_aws

from handler import lambda_handler
from metrics import ALARM_NAME, METRIC_NAME, NAMESPACE, create_low_submission_alarm

REGION = "us-east-1"
COHORT = "python200-fall-2026"


def main():
    with mock_aws():
        # 1. Set up the fake AWS, as an administrator would do once.
        ssm = boto3.client("ssm", region_name=REGION)
        ssm.put_parameter(Name="/ctd/submission-alert/gradebook_token",
                          Value="gb-demo-token", Type="SecureString")
        ssm.put_parameter(Name="/ctd/submission-alert/submission_threshold",
                          Value="80", Type="String")
        cloudwatch = boto3.client("cloudwatch", region_name=REGION)
        create_low_submission_alarm(80, COHORT, cloudwatch)
        print(f"Created alarm: {ALARM_NAME}")

        # 2. Do what EventBridge Scheduler does: call the handler with the empty event.
        response = lambda_handler({}, None)
        print("Scheduled run:", json.loads(response["body"]))

        # 3. Read back the metric that the handler published.
        now = datetime.now(timezone.utc)
        stats = cloudwatch.get_metric_statistics(
            Namespace=NAMESPACE, MetricName=METRIC_NAME,
            Dimensions=[{"Name": "Cohort", "Value": COHORT}],
            StartTime=now - timedelta(hours=1), EndTime=now + timedelta(hours=1),
            Period=3600, Statistics=["Minimum"],
        )
        print("Published SubmissionRate:", [p["Minimum"] for p in stats["Datapoints"]])

        # 4. A manual check of an earlier week, as a staff member would do.
        response = lambda_handler({"requestContext": {}, "body": '{"week": 5}'}, None)
        print("Manual check:", json.loads(response["body"]))

        alarm = cloudwatch.describe_alarms(AlarmNames=[ALARM_NAME])["MetricAlarms"][0]
        print(f"Alarm state in moto: {alarm['StateValue']}")
        print("moto stores alarms but does not evaluate them. On AWS, a rate of 72.5")
        print("is below the threshold of 80, so CloudWatch would set the alarm to ALARM.")


if __name__ == "__main__":
    main()
```

Expected output: a scheduled run for week 7 at 72.5% with `below_threshold: True`, a published value of `[72.5]`, and an alarm state of `OK`.

Reflection answers:
1. The function publishes the metric every week, but it never creates the alarm. A person or a deployment script creates the alarm once, so least privilege leaves `PutMetricAlarm` out of the role.
2. Local tests confirm, for example, the published value, the alarm's settings, the event handling, and that the policy allows the needed calls. Only a deployment confirms, for example, that CloudWatch actually changes the alarm's state, that real IAM allows the calls, or that the schedule triggers the function.
3. The alarm treats every data point as the current week's result. A manual check of an old week would send a misleading value.


---

**Course complete.** This capstone ties together the weather classifier (trained in Week 3 and packaged as the `WeatherClassifier` component in Week 4), the OpenAI API (Week 5), the Supabase database (set up in Week 8 and loaded in Week 9), and the LLM enrichment and first Prefect flow (Week 10) into one production-style ETL flow.
