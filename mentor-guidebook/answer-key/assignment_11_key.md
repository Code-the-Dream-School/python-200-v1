# Assignment 11 Answer Key: Cloud ETL Capstone

**Mentor note:** This is the **capstone** — a full Prefect ETL flow: Extract (Open-Meteo) → Load raw (Supabase) → Transform (Week 4 ML model + LLM) → Load enriched, orchestrated and observable in the Prefect UI. Warmups mix Prefect/production concept answers with small code stubs; the project pulls together everything from Weeks 4, 9, and 10. Grade the flow structure, task decorators, incremental/idempotent design, and error handling. The **video is not assessed**. The decorator/stub questions have exact expected answers (below); the pipeline itself is approach-graded.

---

## Expected File Setup

Assignment lives in `assignments_11/`:

```
assignments_11/
├── warmup_11.py            # concept answers (comments) + code stubs
├── etl_pipeline.py         # full Prefect flow (video link in top comment)
├── models/                 # weather_classifier.pkl + metadata.json from Week 4
└── outputs/
    └── pipeline_run.md      # written reflection on the run
```

Requires `prefect requests openai python-dotenv supabase joblib scikit-learn pandas`. Week 9 must have populated `weather_raw`; Week 4 model files must be in `models/`.

---

# Part 1: Warmup (`warmup_11.py`)

## Prefect Orchestration

### Prefect Q1 — **Objective (concept)**
`@task` = a single unit of work (one step, retryable, observable); `@flow` = the orchestrator that calls tasks in order. The C→F helper (pure, in-memory, no I/O) **does not need `@task`** — tasks add overhead and are most valuable for I/O or failure-prone steps. Wrapping a trivial pure function just clutters the run graph. (Accept "you could, but it's unnecessary" with that reasoning.)

### Prefect Q2 — **Objective** (exact)
```python
@task(retries=3, retry_delay_seconds=30)
```

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
The incremental check (skip dates already in `weather_enriched`) makes the transform idempotent — re-runs process only new rows, so running twice ≠ double work. Removing it and re-processing all 365 every run means: **cost** (repeat LLM calls add up), **time** (re-embedding/re-calling for nothing), and **data correctness** (redundant/overwritten enrichment, wasted API quota). Same lesson as Week 10's incremental step.

---

# Part 2: Project — Full ETL Pipeline (`etl_pipeline.py`)

**Overall check:** four Prefect tasks wired into one flow, correct decorators, incremental + idempotent, graceful LLM fallback. Students are told to write it themselves using the lessons as a guide (not copy verbatim).

### extract task — **Objective (approach)**
`@task(retries=2, retry_delay_seconds=10)`; calls Open-Meteo for 2023 with the four variables; uses `raise_for_status()`; converts columnar response to row dicts; prints record count; returns the list.

### load_raw task — **Objective (approach)**
`@task(retries=2, retry_delay_seconds=5)`; upserts raw records into `weather_raw` with `on_conflict="date"`; prints upserted count.

### transform task — **Objective (approach)**
`@task`; incremental check (fetch existing `weather_enriched` dates, skip them); loads `weather_classifier.pkl`; loads feature names from metadata; runs `predict` + `predict_proba`; calls OpenAI for a one-sentence rec per record; **graceful LLM fallback string** on error; progress print every 50; returns the enrichment records. This is the most complex task — verify the incremental skip and the error handling both exist.

### load_enriched task — **Objective (approach)**
`@task(retries=2, retry_delay_seconds=5)`; **guards against an empty list** (prints + returns early); upserts into `weather_enriched` with `on_conflict="date"`; prints upserted count. The empty-list guard is a common miss — without it a no-op run can error.

### Flow — **Objective (approach)**
`@flow(log_prints=True)`; calls the four tasks in the correct order (extract → load_raw → transform → load_enriched); prints a final completion message.

### Running and Verifying — **Objective (approach)**
Runs with `prefect server start` + `python etl_pipeline.py`; all four tasks show *Completed* in the UI at `localhost:4200`; `weather_raw` has 365 rows and `weather_enriched` has at least as many.

### Reflection (`outputs/pipeline_run.md`) — **Subjective**
5–7 sentences covering: clean run or what failed/how fixed; what the Prefect UI showed and whether tasks retried; a look at a few `weather_enriched` rows (one standout summary, good or bad, with why); and one change for a daily-scheduled deployment (e.g. switch to the forecast API for yesterday's data, add a Prefect **schedule/deployment**, alerting on failure, secrets management). Look for genuine engagement, especially with the scheduling question.

### Video — **Not assessed**
Linked in top comment; shows the pipeline running, the Prefect UI with all tasks Completed + transform logs, and the populated `weather_enriched` table. Not graded for code.

---

**Course complete.** This capstone ties together the Prefect pipelines (Week 1), the weather classifier (Week 4), the LLM enrichment (Weeks 5–6), and the Supabase cloud database (Weeks 8–10) into one production-style ETL flow.
