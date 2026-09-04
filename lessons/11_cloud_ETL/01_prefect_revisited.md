# Prefect, Revisited

You were introduced to Prefect in Week 10, where you wrapped the double-transform into a simple flow. This lesson is a short reconnection with those concepts, followed by a look at what changes when you take the same patterns into a full cloud ETL context.

If the `@task` and `@flow` decorators feel new, it is worth revisiting the [Week 10 orchestration lesson](../10_llm_pipelines/04_orchestration.md) before continuing.

For reference:
- [Prefect 3.x flows documentation](https://docs.prefect.io/v3/concepts/flows)
- [Prefect 3.x tasks documentation](https://docs.prefect.io/v3/concepts/tasks)

## Learning Objectives

By the end of this lesson, you will be able to:

- Recall the core Prefect concepts (`@task`, `@flow`) from Week 10
- Explain what changes when Prefect tasks perform cloud I/O instead of local operations
- Launch the Prefect UI and identify the key elements of a flow run

## A Quick Refresher

Prefect organizes work into two building blocks. A *task* is a single, focused unit of work — loading data, calling an API, writing to a database. A *flow* is the orchestrator that calls tasks in order and manages the run as a whole. You define them with decorators:

```python
from prefect import flow, task

@task
def extract(url: str) -> dict:
    ...

@task
def transform(data: dict) -> list:
    ...

@task
def load(records: list) -> None:
    ...

@flow(log_prints=True)
def etl_pipeline():
    data    = extract("https://api.example.com/data")
    records = transform(data)
    load(records)

if __name__ == "__main__":
    etl_pipeline()
```

When you call `etl_pipeline()`, Prefect runs each task in sequence, tracks its state (Completed, Failed, etc.), and captures any `print()` output as structured logs (because of `log_prints=True`). This is the same `@task` and `@flow` structure you used in Week 10. What is new this week is everything around it: cloud I/O in the tasks, the Prefect UI, retries, structured logging, and running the whole extract-load-transform pipeline as one flow.

## What Changes in a Cloud ETL Context

The Week 10 flow you built ran its tasks once, in order. If a task failed, the flow stopped and you re-ran it by hand. That was the light version, and it was fine for learning the shape of a flow.

In a full cloud ETL pipeline that runs on a schedule, the stakes are higher, because each task does real I/O:

- The extract task makes an HTTP call to an external API. The call can fail due to rate limits, network blips, or a momentarily unavailable service.
- The transform task calls an ML model and the OpenAI API for each record. Each LLM call costs money and takes time; a mid-run failure wastes both.
- The load tasks write to Supabase. A failed run after partial inserts may leave the database in an inconsistent state.

Failures are not just inconvenient — they waste money, leave incomplete data, and may not be obvious unless you are watching the logs. This is why observability (knowing what ran, what failed, and why) matters much more in a cloud pipeline than in a local script.

Prefect addresses this through three mechanisms, which this week introduces: retries to handle transient failures automatically, explicit error checks to surface problems cleanly, and structured logging so you can see exactly what happened in each run.

## The Prefect UI

Before building the full pipeline, it is worth getting familiar with the Prefect UI. Launch it in a terminal:

```bash
prefect server start
```

Then open `http://localhost:4200` in your browser. You will see a list of flow runs. Each run has a status indicator: *Completed* (green), *Failed* (red), *Running* (blue), or *Crashed* (dark red for unexpected exits).

Click into any run to see its individual tasks and their states. The *Logs* tab shows everything Prefect captured during that run — task states, any `print()` output captured by `log_prints=True`, and structured log messages from `get_run_logger()`.

You do not need to keep the server running all the time. Start it when you want to inspect runs, and stop it when you are done. Flow runs are stored locally and will still appear when you restart the server.

## The ETL Skeleton

Here is the structural skeleton for the pipeline you will build in the next lesson — four tasks, each corresponding to one step in the pipeline:

```python
from prefect import flow, task

@task
def extract() -> list:
    ...  # Open-Meteo API → list of raw weather records

@task
def load_raw(records: list) -> None:
    ...  # Upsert raw records into weather_raw

@task
def transform(raw_records: list) -> list:
    ...  # ML classify + LLM enrich → list of enrichment records

@task
def load_enriched(enrichment_records: list) -> None:
    ...  # Upsert enrichment records into weather_enriched

@flow(log_prints=True)
def etl_pipeline():
    raw_records        = extract()
    load_raw(raw_records)
    enrichment_records = transform(raw_records)
    load_enriched(enrichment_records)

if __name__ == "__main__":
    etl_pipeline()
```

Four tasks, two load steps. The flow structure makes the pipeline stages explicit: fetch raw data, persist it, transform it (both ML and LLM), persist the enriched output. In the next lesson you will fill in each task with the real code from Weeks 9 and 10.
