# Making Pipelines Production-Ready

The pipeline you built in the previous lesson works. If everything goes right, it extracts, transforms, and loads without issue. But "everything going right" is an optimistic assumption for a pipeline that depends on two external APIs and a cloud database. This lesson covers four patterns that make your pipeline reliable.

These patterns are extremely common in real-world data engineering. Most production pipeline work is not about writing complicated algorithms — it is about making systems dependable, observable, and safe to re-run.

For reference:

- [Prefect retries documentation](https://docs.prefect.io/v3/concepts/tasks#retries)
- [Prefect logging documentation](https://docs.prefect.io/v3/develop/logging)
- [What is idempotency?](https://blog.postman.com/what-is-idempotency/)

## Learning Objectives

By the end of this lesson, you will be able to:

- Explain why transient failures are inevitable in cloud pipelines and how retries address them
- Use `raise_for_status()` to propagate errors cleanly through a Prefect flow
- Apply `log_prints=True` and `get_run_logger()` to produce useful structured logs
- Explain idempotency and how `upsert` with `on_conflict` and the incremental check support it

## Retries

External API calls fail sometimes. Rate limit responses, brief network timeouts, and momentary service unavailability are not bugs in your code, but they will crash your pipeline if you do not account for them.

Prefect's retry mechanism handles this cleanly by adding `retries` and `retry_delay_seconds` to a task decorator:

```python
@task(retries=2, retry_delay_seconds=10)
def extract() -> list:
    ...
```

When the task raises any exception, Prefect waits 10 seconds and tries again, up to 2 more times. If all attempts fail, the task (and the flow) is marked as Failed.

In the Prefect UI, you will see the task cycle through multiple attempts before ultimately succeeding or failing. Each attempt is logged separately, which makes debugging much easier.

Retries are especially useful for operations that depend on external systems:

- API calls (Open-Meteo, OpenAI)
- Database connections and writes (Supabase)
- Cloud authentication requests

These systems occasionally fail for reasons outside your control, and a retry often fixes the problem automatically.

A useful rule of thumb:

- Use retries for transient external failures.
- *Do not* use retries for genuine programming bugs.

If your code has a logic error or a broken loop, retrying will not help — it only delays the inevitable failure and makes debugging noisier. Two or three retries with a 10–30 second delay is a very common production default.

## Error Handling

`raise_for_status()` is a powerful habit. Compare these two patterns:

```python
# Silent failure — the pipeline continues with bad data
response = requests.get(url)
if response.status_code != 200:
    print("Something went wrong")
```

```python
# Loud failure — Prefect catches the exception and marks the task Failed
response = requests.get(url)
response.raise_for_status()
```

In the first version, if the API returns a 404 or 500, the pipeline continues with an empty or malformed response. That can lead to corrupted downstream data, misleading results, or a pipeline that appears successful even though the data is wrong.

In the second version, the exception propagates immediately:

- Prefect marks the task as *Failed*
- The error appears clearly in the logs
- Downstream tasks do not run
- The bad data never gets written

The general principle:

> In data pipelines, visible failures are usually safer than silent corruption.

A failed run is inconvenient, but incorrect data silently flowing through a system is often much harder to detect and fix later.

## Logging

You already have `log_prints=True` on your flow, which captures all `print()` output as Prefect log entries. For many small pipelines, this is enough:

```python
print(f"Upserted {len(records)} rows into weather_raw")
```

This will appear automatically in the Prefect UI logs.

For more structured logging — with severity levels — use `get_run_logger()` inside a task:

```python
from prefect.logging import get_run_logger

@task
def load_enriched(enrichment_records: list) -> None:
    logger = get_run_logger()
    logger.info(f"Upserting {len(enrichment_records)} enrichment records")

    if not enrichment_records:
        logger.warning("No enrichment records to load — transform task may have found nothing to process")
        return

    response = (
        supabase.table("weather_enriched")
        .upsert(enrichment_records, on_conflict="date")
        .execute()
    )
    logger.info(f"Upserted {len(response.data)} rows into weather_enriched")
```

Structured logs are useful because they can be filtered and searched more easily across many runs.

Common logging levels:

- `logger.info()` — routine progress updates
- `logger.warning()` — something unusual but non-fatal (e.g., LLM returned an unexpected format)
- `logger.error()` — a serious problem (e.g., authentication failed after retries)

Good logging becomes more important as pipelines grow larger and run automatically on schedules. When something breaks overnight, logs are often the first place engineers look.

## Idempotency

A pipeline is *idempotent* if running it multiple times produces the same result as running it once.

This matters because pipelines frequently get re-run:

- After a retry
- After fixing a bug
- After a partial failure mid-run
- After an infrastructure outage

Your pipeline already handles this in two places.

**Upsert with `on_conflict`** in the load tasks:

```python
supabase.table("weather_raw").upsert(records, on_conflict="date").execute()
supabase.table("weather_enriched").upsert(enrichment_records, on_conflict="date").execute()
```

Re-running either load task updates existing rows in place rather than failing or duplicating them. The database always ends up in a consistent state regardless of how many times the load runs.

**The incremental check** in the transform task:

```python
already_done = {r["date"] for r in supabase.table("weather_enriched").select("date").execute().data}
to_process   = [r for r in raw_records if r["date"] not in already_done]
```

If the pipeline crashes during the LLM enrichment step after processing 200 of 365 records, re-running picks up from record 201 — not from the beginning. The 200 already-written records in `weather_enriched` are detected and skipped. This matters for LLM calls especially: re-processing records you have already paid for is waste.

Together, these two patterns mean re-running the pipeline after any failure is always safe. No manual cleanup, no duplicate rows, no extra API costs for records already processed.

## What Comes Next

The pipeline you built runs locally when you execute:

```bash
python etl_pipeline.py
```

In a real production environment, pipelines are usually scheduled automatically — for example, every morning at 6am, or every night after business hours. Prefect supports this through *deployments*, which package your flow configuration and scheduling rules. A Prefect *worker* then executes the flow automatically according to that schedule.

[Prefect Cloud](https://www.prefect.io/cloud) provides a hosted version of this infrastructure with additional monitoring, alerting, and collaboration features. The [Prefect documentation on deployments](https://docs.prefect.io/v3/deploy/index) covers the full setup.

In the practicum that follows this course, you'll deploy exactly this flow to run attended on AWS. Here's how you'll make that transition:

| What You Built with Prefect               | How You'll Refactor to AWS                        |
|-------------------------------------------|---------------------------------------------------|
| `@flow` body calling tasks in order       | Lambda handler calling the same functions         |
| `@task(retries=2, retry_delay_seconds=…)` | Lambda async retry config + SQS dead-letter queue |
| `log_prints / get_run_logger()`           | CloudWatch Logs                                   |
| Prefect UI at `localhost:4200`            | CloudWatch Metrics + Alarms                       |
| `prefect server start` run by you         | Managed and always-on (run by AWS)                |
| Deployments + workers + schedule          | EventBridge Scheduler cron -> Lambda              |
| `.env/load_dotenv()`                      | Lambda env vars + SSM Parameter Store             |
| Idempotent `upsert(on_conflict=…)`        | No change - still in Supabase                     |

---

You've now built a cloud ETL pipeline from scratch:

- Extract from a live API
- Load raw data to a cloud database
- Transform with an ML model and an LLM
- Load enriched results back to the database
- Orchestrate with Prefect
- Monitor through a UI
- Recover gracefully from transient failures

That is Week 1 pipelines + Week 4 model persistence + Week 9 database writes + Week 10 double-transform, all working together in a realistic workflow.
