# Week 10 Mentor Summary: LLMs in Pipelines

**Lesson files:** `lessons/10_cloud_ML.md` (overview) and five lessons in `lessons/10_llm_pipelines/`, one of them optional
**Assignment file:** `assignments/10_cloud_ML.md`
**Answer key:** `mentor-guidebook/answer-key/assignment_10_key.md`
**Slides:** `mentor-guidebook/slides/10_llm_pipelines.pdf`

**Learning objective:** Students build the Transform step of the weather pipeline as a **double transform**. The `WeatherClassifier` component predicts whether each day in `weather_raw` is good for running, and then an LLM writes a one-sentence recommendation for that day. The results go into `weather_enriched`. Students check the result with SQL and wrap the script in a simple Prefect flow.

**Where this fits:** The week combines three earlier pieces. Students trained the classifier in Week 3 and packaged it in Week 4, used language models in Weeks 5 to 7, and loaded the Supabase tables in Week 9. Week 11 joins this transform with the Week 9 extract and load into one Prefect pipeline with retries and logging. The practicum after the course moves that pipeline to AWS.

---

## Lesson Overview

All lessons use the two Supabase tables from Week 9. `weather_raw` holds one year of daily weather, and `weather_enriched` receives `good_for_running`, `confidence`, and `llm_summary` for each date.

| Lesson | What students learn |
|---|---|
| **1. The Double-Transform Pattern** | Where ML models, LLMs, and deterministic code each belong in the Transform step. How the Week 4 `WeatherClassifier` plugs into a pipeline through its `predict()` method. Cost and latency at scale: 365 calls to `gpt-4o-mini` cost under $0.02. Constrained prompts that return output that code can check. |
| **2. ML Inference on Database Records** | Reading rows from `weather_raw` with `supabase-py`. **Incremental processing**: skipping dates already in `weather_enriched`. Calling `classifier.predict()` and reading each `Prediction`'s `label` and `probability`. Building enrichment records and checking that the share of good days looks reasonable. |
| **3. LLM Enrichment and Writing to weather_enriched** | A system prompt and a user message that include the features, the prediction, and the confidence. Calling the OpenAI API in a loop with `max_tokens=100`. A `try/except` with the fallback string `"Recommendation unavailable."`. Upserting into `weather_enriched` with `on_conflict="date"`, and a spot-check query. |
| **4. Orchestrating with Prefect** | What a Prefect **task** and **flow** are. Wrapping read, classify, enrich, and load in `@task` functions and calling them from a `@flow(log_prints=True)`. Retries, the Prefect UI, and scheduling come in Week 11. |
| **5. (Optional) Practicum AWS Bridge, Part 3: The Lambda Handler** | Part of the ungraded AWS Bridge pilot. What a Lambda handler and its `event` and `context` arguments are. The difference between an EventBridge Scheduler event and a Function URL event, whose `body` is a JSON string. Returning `statusCode`, `headers`, and `body`, and writing one JSON log line for CloudWatch Logs. |

---

## Assignment Deliverables

**Setup:** Students work in `assignments_10/`. They copy the `weather_model/` package from Week 4 and the `models/` folder with `weather_classifier.pkl` into it. Week 9 must have filled `weather_raw`. The `.env` file needs `SUPABASE_URL`, `SUPABASE_KEY`, and `OPENAI_API_KEY`.

**Grading:** The city, the predictions, and every `llm_summary` vary between students and between runs, so grade the approach and not the numbers. The reviewer cannot see a student's Supabase project, `.env` file, or video. For the video, the rubric checks only that a link is present. The two themes to check are the separation of the ML and LLM roles and correct incremental processing.

| Part | File | What students do | Concepts practiced |
|---|---|---|---|
| Warmup | `warmup_10.py` | Three ML/LLM questions: the two roles, choosing a tool for five tasks, and incremental processing. Two prompt questions: a two-sentence prompt with its validation change, and `call_with_retry(client, messages, max_retries=3)`. | Lessons 1–3 |
| Project, Steps 1–4 | `transform_10.py` | Incremental read with three printed counts, ML transform with `WeatherClassifier`, LLM transform with `gpt-4o-mini`, a fallback string, and a progress print every 50 records, then an upsert. | Incremental processing, the component, prompt design, upsert |
| Project, Step 5 | `transform_10.py` | Prints the row count, five sample rows, and the good-day count, and comments on one strong and one weak summary. | Checking LLM output |
| Project, Step 6 | `verify_10.sql` | Query 1 uses a `LEFT JOIN ... WHERE ... IS NULL` to list the dates with no enrichment, run before and after the transform. Query 2 counts days with `GROUP BY good_for_running`. A closing comment explains the results. | SQL review from Python for Data Analysis |
| Project, Step 7 | `transform_10.py` | Wraps read, classify, enrich, and load as `@task` functions inside a `@flow(log_prints=True)`. | Prefect tasks and flows |
| Project, Step 8 and Video | `transform_10.py` | A reflection on using the model for another city, whether the LLM can override the classifier, and scaling to 50,000 records. A video link goes at the top of the file. | Model limits, cost and latency |

**Optional:** Part 3, the Practicum AWS Bridge, adds `handler.py`, `test_handler.py`, and `handler_notes.md` in an `aws_bridge/` folder. It is an ungraded pilot. Never ask for revisions because a student skipped it.

**Submission:** A pull request from the student's branch into `main` in their `python200-homework` repository. The `weather_model/` and `models/` folders need to be committed.

---

## Key Concepts

These short explanations cover the ideas students ask about most this week. Expand any one you need.

<details>
<summary><strong>The double transform: why the classifier and the LLM each do one job</strong></summary>

The classifier makes the good-or-skip decision. It uses four numeric features and has a labeled training set, so it is fast, cheap, and gives the same answer every time. An LLM could make the same decision, but it would be slower, cost money for each row, and could change its answer between runs.

The LLM writes the recommendation. The classifier returns only a label and a probability, and it cannot explain them in a sentence that a runner can use.

The order matters. The LLM receives the prediction and the confidence in its prompt, so it describes a decision that has already been made. It cannot override the classifier. If the classifier is wrong, the LLM writes a confident sentence about a wrong prediction. This is the topic of reflection question 2. The confidence is in the prompt so that a borderline day, such as 0.51, gets a more careful recommendation than a day at 0.95.

</details>

<details>
<summary><strong>Incremental processing, and how the SQL check shows it</strong></summary>

Before classifying, the script collects every date already in `weather_enriched` and keeps only the rows from `weather_raw` whose dates are not in that set. On the first run, every row is processed. On a second run, zero rows are processed. This means a re-run makes no new OpenAI calls and does not repeat work that is already finished.

Step 6 shows the same idea in SQL. Query 1 joins `weather_raw` to `weather_enriched` with a `LEFT JOIN` and keeps the rows where `e.date IS NULL`. These are the dates that still need work. Before the first transform, it returns every date in `weather_raw`. That is usually 366 rows, because the Week 9 CRUD Question 1 test record is still in the table. After the transform, it returns zero rows, and the SQL Editor shows "Success. No rows returned." That empty result is the correct answer.

An LLM failure does not leave a gap, because the fallback string still produces a row.

</details>

<details>
<summary><strong>Prefect tasks and flows, the light version</strong></summary>

A **task** is one unit of work, marked with `@task`. In this pipeline there are four tasks: read the new records, classify them, enrich them with the LLM, and load them. A **flow** is the function that calls the tasks in order and tracks the run as a whole. It is marked with `@flow`.

The code inside each task is the same code students wrote in Lessons 2 and 3. Prefect adds tracking: it records when each task starts, whether it completes, and whether the flow succeeds. `log_prints=True` makes Prefect capture every `print()` as part of the run's log.

This week, students run the flow with `python transform_10.py` and read the summary in the terminal. They do not add retries, scheduling, or the Prefect UI. If a student adds retries anyway, that is fine, but it is not required. Week 11 adds retries, `get_run_logger()`, and the UI on top of this same structure.

</details>

---

## FAQs and Common Trouble Spots

**1. "Python cannot find `weather_model`, or it cannot find the model file."**
Check that `weather_model/` and `models/weather_classifier.pkl` were both copied into `assignments_10/`. The path `models/weather_classifier.pkl` is relative, so the student needs to run the script from inside `assignments_10/`. If the `.pkl` file is lost, the student can re-run the Week 3 training script to create it again.

**2. "How much will the OpenAI calls cost?"**
The cost is small. The lesson estimates under $0.02 for 365 calls to `gpt-4o-mini`, and the run takes a few minutes. The lesson code reads `os.environ["OPENAI_API_KEY"]`, so if a student copied that pattern, a missing key in `.env` stops the script at startup with a `KeyError`. Remind students that deleting rows from `weather_enriched` to re-run means paying for those calls again.

**3. "My second run processed zero records. Is my script broken?"**
No, this is the incremental check working as intended, and the answer key expects 0 on a second run. To process some dates again, a student deletes those rows from `weather_enriched` and runs the script again.

**4. "I already ran my transform, so I cannot get a 'before' result for Query 1."**
The assignment allows an expected result with an explanation instead. The usual expected result is 366 rows, or 365 if the student deleted the Week 9 test record. If Query 1 always returns zero rows, check three common mistakes in the answer key. The query might join from `weather_enriched` instead of `weather_raw`, check `r.date IS NULL` instead of `e.date`, or use an inner `JOIN`.

**5. "Query 1 still returns dates after the transform finished."**
The run probably crashed partway through, or the incremental logic in Step 1 has a bug. LLM errors alone do not cause this, because the fallback string still produces a row. Ask the student to read the terminal output from the last run.

**6. "Almost every day is predicted as skip, or almost every day as good."**
First, check whether the model was trained on the same city that Week 9 loaded. A model trained on one climate can be less accurate on another, which is the topic of reflection question 1. The lesson says that for Charlotte, NC, in 2023, about 30–40% of days should be good.

**7. "Do I have to do Part 3, the AWS Bridge?"**
No, it is an optional, ungraded pilot. For students who try it, the most common mistake is `event["body"]["week"]`, which raises a `TypeError` because the body is a JSON string. The fix is `json.loads(event["body"])`. The answer key lists the expected rates for each week from `submissions.json`.
