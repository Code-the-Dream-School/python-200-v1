# Week 11 Mentor Summary: Cloud ETL

**Lesson files:** `lessons/11_cloud_ETL.md` (overview) and four lessons in `lessons/11_cloud_ETL/`, one of them optional
**Assignment file:** `assignments/11_cloud_ETL.md`
**Answer key:** `mentor-guidebook/answer-key/assignment_11_key.md`
**Capstone rubric:** `resources/rubric_supabase.md`
**Slides:** `mentor-guidebook/slides/11_cloud_ETL.pdf`

**Learning objective:** In the capstone, students write `etl_pipeline.py` from their own understanding, using the lessons as a guide. It is one Prefect flow with four tasks: `extract`, `load_raw`, `transform`, and `load_enriched`. Students make the pipeline reliable with retries, `raise_for_status()`, logging, and idempotent writes. They watch it run in the Prefect UI and summarize both tables with SQL.

**Where this fits:** This is the last week of the course. It joins the Week 4 `WeatherClassifier` component, the Week 9 extract and load into Supabase, and the Week 10 double transform and first Prefect flow. In the practicum that follows, students deploy this kind of pipeline on AWS. Lesson 3 ends with a table that shows how each Prefect feature maps to an AWS service.

---

## Lesson Overview

The lessons use the same weather data and the same two Supabase tables, `weather_raw` and `weather_enriched`, as Weeks 9 and 10. Most of the code is familiar. The new material is how the pieces connect and what makes a pipeline safe to run again.

| Lesson | What students learn |
|---|---|
| **1. Prefect, Revisited** | A review of `@task` and `@flow` from Week 10. Why cloud I/O makes failures more costly. Starting the Prefect UI with `prefect server start` and reading flow runs at `http://localhost:4200`. The four-task skeleton for the week's pipeline. |
| **2. Building the Pipeline** | Filling in the four tasks with code from Weeks 9 and 10: an Open-Meteo extract, an upsert into `weather_raw`, a transform that combines the incremental check, ML inference, and LLM enrichment, and an upsert into `weather_enriched`. Running the flow and reading a successful run and a failed run in the UI. |
| **3. Making Pipelines Production-Ready** | Four patterns: retries with `retries` and `retry_delay_seconds`, `raise_for_status()` so failures are visible, logging with `log_prints=True` and `get_run_logger()`, and **idempotency** through upserts and the incremental check. A preview of deployments and Prefect Cloud, and a table that maps Prefect features to AWS. |
| **4. (Optional) Practicum AWS Bridge, Part 4: Assembly** | The last part of the ungraded AWS Bridge pilot. Publishing the submission rate as a CloudWatch metric with `boto3`, defining a CloudWatch alarm, and testing the whole alert with `moto`. A permission test that uses the Week 8 IAM checker before deployment. |

---

## Assignment Deliverables

**Setup:** Students work in `assignments_11/` and copy `weather_model/` and `models/weather_classifier.pkl` from Week 4 into it. Week 9 must have filled `weather_raw`. The `.env` file from Week 10 is still needed. Students run `prefect server start` in one terminal and `python etl_pipeline.py` in a second terminal.

**Grading:** The capstone is written to a specification, so implementations vary. Grade whether each task meets its listed requirements, not whether the code matches the lessons. Names and decorator parameters are exact. The reviewer cannot see the Supabase project, the Prefect UI, or the video, so grade the code and the written answers. For the video, the rubric checks only that a link is present. `resources/rubric_supabase.md` scores each requirement as Does Not Meet, Meets, or Exceeds Expectations.

| Part | File | What students do | Concepts practiced |
|---|---|---|---|
| Warmup | `warmup_11.py` | Three Prefect questions: task or flow for a pure helper, a retry decorator for `call_api`, and where to look in the UI after a failure. Four production questions: `raise_for_status()`, upsert or insert, a `get_run_logger()` stub, and how the incremental check supports idempotency. | Lessons 1 and 3 |
| Project, `extract` and `load_raw` | `etl_pipeline.py` | Fetches 2023 daily weather for a chosen city with `@task(retries=2, retry_delay_seconds=10)` and `raise_for_status()`, and converts it to row dictionaries. Upserts the rows into `weather_raw` with `@task(retries=2, retry_delay_seconds=5)`. | Retries, error handling, upsert |
| Project, `transform` | `etl_pipeline.py` | A plain `@task` that skips dates already enriched, classifies with `WeatherClassifier` (`label` and `probability`), calls OpenAI with a fallback string on error, and prints progress every 50 records. | Incremental processing, the double transform |
| Project, `load_enriched` and flow | `etl_pipeline.py` | Returns early on an empty list, then upserts into `weather_enriched`. A `@flow(log_prints=True)` calls the four tasks in order and prints a completion message. | Idempotency, orchestration |
| SQL Summary Report | `verify_11.sql` | Query 1 returns the row count and latest `loaded_at` of `weather_raw`. Query 2 returns the row count, latest `enriched_at`, and percentage of good days of `weather_enriched`. A closing comment explains the timestamps and the percentage. | Aggregation, subqueries, `DEFAULT now()` |
| Reflection and Video | `outputs/pipeline_run.md`, `etl_pipeline.py` | A 5–7 sentence reflection on the run, the UI, the summaries, and a daily schedule. A video link goes at the top of `etl_pipeline.py`. | Observability, production thinking |

**Optional:** Part 3, the Practicum AWS Bridge, adds `metrics.py`, `test_end_to_end.py`, `test_permissions.py`, `run_local.py`, and `bridge_reflection.md`, and it updates `handler.py` and `test_handler.py`. It is an ungraded pilot, it is not part of the capstone rubric, and it must not affect the capstone grade.

**Submission:** A pull request from the student's branch into `main` in their `python200-homework` repository.

---

## Key Concepts

These short explanations cover the ideas students ask about most this week. Expand any one you need.

<details>
<summary><strong>Retries, loud failures, and fallbacks</strong></summary>

The pipeline handles errors in three different ways, and each one has its own job.

- **Retries** are for short, outside failures, such as a network timeout. With `@task(retries=2, retry_delay_seconds=10)`, Prefect runs the task again up to two more times when it raises an exception. Retries do not help with a bug in the code.
- **`raise_for_status()`** turns a 4xx or 5xx HTTP response into an exception. The task is marked Failed, the downstream tasks do not run, and bad data is never written. A check like `if response.status_code != 200: print(...)` lets the pipeline continue with bad data.
- **The fallback string** in `transform` catches each LLM error and writes `"Recommendation unavailable."` instead. One failed call does not stop the other 364.

The `transform` task has no retries in the specification. Because its LLM errors are caught, it rarely raises an exception. A Failed `transform` usually points to a problem outside the LLM calls, such as a missing model file or a failed Supabase query.

</details>

<details>
<summary><strong>Idempotency: why running the pipeline again is safe</strong></summary>

A pipeline is idempotent when running it many times gives the same result as running it once. Two parts of this pipeline make that true.

- **Upserts with `on_conflict="date"`.** If a date already exists, the row is updated in place. A plain `insert` would fail with a primary-key violation on the dates that already exist.
- **The incremental check in `transform`.** It skips every date already in `weather_enriched`. Suppose a run crashes after 200 of 365 LLM calls. The next run processes only the 165 dates that remain, so the first 200 calls are not paid for again.

The `load_enriched` task needs its empty-list guard because of this check. When every date is already enriched, `transform` returns an empty list, and `load_enriched` prints a message and returns early.

Together, these parts mean a student can fix a bug and run the whole flow again from the start, with no manual cleanup.

</details>

<details>
<summary><strong>Why the SQL report shows old timestamps</strong></summary>

This is the key teaching point of `verify_11.sql`. Students often expect the latest `loaded_at` and `enriched_at` to be from the run they just finished. Usually, `loaded_at` is from Week 9 and `enriched_at` is from Week 10. There are two reasons.

1. Both columns use `DEFAULT now()`. Postgres fills a default only when a row is first inserted. The `load_raw` upsert updates the weather columns of rows that already exist, but it does not send `loaded_at`, so the Week 9 time stays.
2. The incremental check skipped every date, because Week 10 enriched all of them. `load_enriched` received an empty list and wrote nothing.

A good answer explains one reason, and a strong answer explains both and connects them to idempotency. If a student recreated the tables or deleted rows first, today's timestamps are correct, as long as the student explains why.

</details>

---

## FAQs and Common Trouble Spots

**1. "Do I need `weather_classifier_metadata.json`, or should I call `predict_proba` myself?"**
No. The assignment requires the `WeatherClassifier` component. Students call `classifier.predict(records)` and read each `Prediction`'s `label` and `probability`, as in Week 10 and in Lesson 2's `transform` code. The component already knows its feature columns, so the metadata file is not needed. Lesson 2 lists the four weather variables in a `DAILY_VARIABLES` constant for the `extract` request. A student who copied an older version of the lesson that uses `joblib.load` and `predict_proba` directly should switch to the component, because the rubric grades the component.

**2. "My `transform` found nothing to process, and `load_enriched` loaded nothing."**
This is the expected result when Week 10 already enriched every date, and Lesson 2 ("Running the Pipeline") tells students to expect it. The empty-list guard in `load_enriched` exists for this case. Lesson 2 also explains how to see a full run: delete rows from `weather_enriched` first, and then run the pipeline again. Those LLM calls then use the student's OpenAI credits again.

**3. "Can I use a different city this week?"**
The assignment allows any city, but recommend that students use the same city they loaded in Week 9. The `load_raw` upsert replaces the weather values for each date. The incremental check then skips those dates, so `weather_enriched` keeps the predictions made from the old values.

**4. "The Prefect UI at `localhost:4200` does not load, or my run is missing."**
The server must be running in its own terminal, started with `prefect server start`. Students can stop it when they finish. The lesson says that runs are stored locally and appear again when the server restarts. To investigate a Failed task, open the flow run, then the task, then its Logs tab, where the traceback appears.

**5. "My good-day percentage is a whole number, or it is 0."**
The student probably multiplied by `100` instead of `100.0`, or divided before multiplying. Both cause integer division. A query with `good_for_running = 1` is a habit from SQLite. PostgreSQL raises `operator does not exist: boolean = integer`, and the fix is `= true`. A `CASE` expression instead of the subquery is also correct.

**6. "My timestamps are several hours off from my local time."**
This is expected. Supabase shows timestamps in UTC, marked `+00`. Whether the timestamps are from this run is a separate question, which the third Key Concept explains.

**7. "My Week 10 bridge tests fail now, and my alarm stays `OK`."**
This applies only to students doing the optional Part 3. A scheduled run now calls CloudWatch, so the Week 10 test fixture needs `AWS_DEFAULT_REGION` and `with mock_aws(): yield`. Without them, the tests try to reach real AWS and usually fail with a credentials error. An alarm in the `OK` state is expected, because `moto` stores alarms but does not evaluate them.
