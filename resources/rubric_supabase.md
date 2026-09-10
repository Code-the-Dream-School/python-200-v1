# Week 11 Capstone Rubric: Cloud ETL Pipeline

**Assignment:** Build a Prefect-orchestrated ETL pipeline (`etl_pipeline.py`) that extracts historical weather data, classifies it with a saved sklearn model, enriches it with LLM-generated recommendations, and loads results to Supabase.

**Scale:**
- **Does Not Meet Expectations** — requirement is missing or incorrect
- **Meets Expectations** — requirement fulfilled as described in the instructions
- **Exceeds Expectations** — requirement fulfilled with meaningful additions (better error handling, extra logging, thoughtful design choices, etc.)

**Deliverables:**
- `warmup_11.py`
- `etl_pipeline.py`
- `models/weather_classifier.pkl` and `models/weather_classifier_metadata.json`
- `outputs/pipeline_run.md` (5–7 sentence reflection)
- Video: terminal run + Prefect UI (all tasks Completed) + Supabase dashboard with `weather_enriched` rows

---

## 1. Warmup

| Criterion | Does Not Meet Expectations | Meets Expectations | Exceeds Expectations |
|---|---|---|---|
| Prefect Question 1 | Missing or does not distinguish `@task` from `@flow` | Explains the difference and correctly argues the pure helper should **not** be a `@task` (no I/O, no need for retries/observability) | Gives a concrete example of when you *would* promote a helper to a task |
| Prefect Question 2 | Missing or incorrect decorator syntax | Correct decorator: `@task(name="call_api", retries=3, retry_delay_seconds=30)` | |
| Prefect Question 3 | Missing or vague | Identifies the task-run page / logs tab in the Prefect UI and describes finding the traceback or error message for `transform` | Mentions checking the timeline view or understanding that `load_enriched` never ran because `transform` failed |
| Production Question 1 | Missing or does not explain `raise_for_status()` | Explains it raises an `HTTPError` on non-2xx responses; contrasts with `print("error")` which lets corrupted data flow downstream silently | Connects to how Prefect marks the task as Failed and prevents downstream execution |
| Production Question 2 | Missing or does not explain upsert vs. insert | Explains that upsert allows a safe re-run (idempotent) because duplicate dates are updated rather than causing a conflict error | Mentions that plain `insert` would raise a unique-constraint violation on the duplicate rows from the first partial run |
| Production Question 3 | Missing or incorrect | Provides a correctly decorated `@task` stub using `get_run_logger()` with an INFO-level message that includes `len(enrichment_records)` | Adds extra context to the log message (e.g., timing, batch info) |
| Production Question 4 | Missing or does not address idempotency | Explains that skipping already-enriched dates prevents duplicate LLM calls and redundant writes; notes the cost, time, and correctness consequences of reprocessing all 365 records | Connects to real-world scheduling scenarios or cost estimation |

---

## 2. Extract Task

| Criterion | Does Not Meet Expectations | Meets Expectations | Exceeds Expectations |
|---|---|---|---|
| `@task` decorator | Missing or incorrectly applied | `@task(retries=2, retry_delay_seconds=10)` present | Adds a descriptive task name |
| API call | Missing, wrong endpoint, or wrong parameters | Open-Meteo historical archive API called for 2023 daily data using the same four variables as Week 4 | Adds timeout, request headers, or validates response schema |
| `raise_for_status()` | Missing | Called on the response | |
| Data reshaping | Returns raw columnar JSON without reshaping | Converts columnar API response into a list of row dictionaries | |
| Print confirmation | Missing | Prints record count | |
| Return value | Does not return the row list | Returns the list of row dicts | |

---

## 3. Load Raw Task

| Criterion | Does Not Meet Expectations | Meets Expectations | Exceeds Expectations |
|---|---|---|---|
| `@task` decorator | Missing or incorrectly applied | `@task(retries=2, retry_delay_seconds=5)` present | Adds a descriptive task name |
| Supabase upsert | Missing, uses plain insert, or targets wrong table | Upserts records into `weather_raw` using `on_conflict="date"` | Logs the upsert count or handles partial-failure scenarios |
| Print confirmation | Missing | Prints upserted row count | |

---

## 4. Transform Task

| Criterion | Does Not Meet Expectations | Meets Expectations | Exceeds Expectations |
|---|---|---|---|
| `@task` decorator | Missing or incorrectly applied | `@task` present | Adds a descriptive task name |
| Incremental check | Missing; processes all records every run | Fetches dates already in `weather_enriched` and skips them | Logs how many records were skipped vs. how many will be processed |
| Model loading | Missing or wrong path | Loads `weather_classifier.pkl` and `weather_classifier_metadata.json` from `models/` | Validates that feature names match the incoming data |
| ML classification | Missing or incorrectly applied | Runs `predict` and `predict_proba` on unprocessed records | |
| LLM enrichment | Missing or not called per record | Calls OpenAI API to generate a one-sentence recommendation for each unprocessed record | Uses structured output parsing or batches requests efficiently |
| Fallback handling | No fallback / crashes on LLM error | Handles LLM errors gracefully with a fallback string | Logs the error details before falling back |
| Progress logging | Missing | Prints progress every 50 records | |
| Return value | Does not return enrichment records | Returns the complete list of enrichment records | |

---

## 5. Load Enriched Task

| Criterion | Does Not Meet Expectations | Meets Expectations | Exceeds Expectations |
|---|---|---|---|
| `@task` decorator | Missing or incorrectly applied | `@task(retries=2, retry_delay_seconds=5)` present | Adds a descriptive task name |
| Empty-list guard | Missing; crashes or silently upserts nothing | Checks for empty list, prints a message, and returns early | |
| Supabase upsert | Missing, uses plain insert, or targets wrong table | Upserts enrichment records into `weather_enriched` using `on_conflict="date"` | Logs blob URL, row count, or handles partial-failure scenarios |
| Print confirmation | Missing | Prints upserted row count | |

---

## 6. Prefect Flow

| Criterion | Does Not Meet Expectations | Meets Expectations | Exceeds Expectations |
|---|---|---|---|
| `@flow` decorator | Missing or incorrectly applied | `@flow(log_prints=True)` present | Adds flow name or description |
| Task sequencing | Tasks not called or called out of order | Extract → Load Raw → Transform → Load Enriched in sequence | |
| Data handoff | Re-fetches data or uses globals | Output of each task passed as input to the next | |
| Completion message | Missing | Prints a final completion message | |

---

## 7. Verification Artifacts

| Criterion | Does Not Meet Expectations | Meets Expectations | Exceeds Expectations |
|---|---|---|---|
| Prefect UI | Not shown or shows failed/crashed tasks | Video shows all four tasks in **Completed** state | Shows task duration, retry attempts, or transform logs in the UI |
| Supabase dashboard | Not shown or tables are empty/missing | `weather_raw` has 365 rows; `weather_enriched` has rows visible with `llm_summary` column | |
| `pipeline_run.md` | Missing or empty | File present with 5–7 sentence reflection | |
| Video scope | Missing or incomplete | Shows terminal run, Prefect UI, and Supabase dashboard as described | Narrates decisions or points out interesting details |

---

## 8. Reflection

| Criterion | Does Not Meet Expectations | Meets Expectations | Exceeds Expectations |
|---|---|---|---|
| Length | Fewer than 5 sentences | 5–7 sentences as required | |
| First-run experience | Not addressed | Describes whether the pipeline ran cleanly and any fixes needed | |
| Prefect UI observations | Not addressed | Describes what the Prefect UI showed, including any retries | |
| LLM quality assessment | Not addressed | Picks out a specific `llm_summary` row and explains why it stands out | Compares multiple rows or critiques the prompt design |
| Production thinking | Not addressed | Proposes one change for a daily-schedule deployment | Connects to real-world concerns like cost, monitoring, or failure recovery |
