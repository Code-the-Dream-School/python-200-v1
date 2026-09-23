# Week 9 Assignments

This week you connected Python to a cloud database, learned to read and write rows with `supabase-py`, and built an Extract + Load pipeline that pulls weather data from the Open-Meteo API and stores it in Supabase. The warmup checks your understanding of those concepts and gives you practice with the SDK. The project has you build the pipeline end-to-end.

---

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_09/`. Inside that folder, create:

1. `warmup_09.py` — warmup exercises (conceptual answers as comments, code as runnable Python)
2. `project_09.py` — the Extract + Load pipeline
3. `.env` — your Supabase credentials (**add `.env` to your `.gitignore` before committing**)

When finished, commit and open a PR as described in the [assignments README](README.md).

**Setup reminder:** Make sure your `.env` file is present and your Supabase tables exist before running any scripts.

```bash
uv pip install supabase python-dotenv requests
```

---

# Part 1: Warmup

Put all warmup answers in `warmup_09.py`. Use comments to label each section and question (e.g., `# --- Supabase Connection ---` and `# Q1`). For conceptual questions, write your answer as a comment block. For code questions, write working Python that connects to your actual Supabase project.

## Supabase Connection

### Connection Question 1

In a comment block, answer: what are the two pieces of information `supabase-py` needs to connect to your project? Where do you find them in the Supabase dashboard, and why should they never be hardcoded in a Python script?

### Connection Question 2

Write a function `get_client()` that:
1. Loads your credentials from environment variables using `python-dotenv`
2. Creates and returns a Supabase client

The function should raise a clear error if either environment variable is missing.

### Connection Question 3

In a comment block, answer: what is Row Level Security (RLS), and why did you disable it on your tables for this course? In what kind of real-world application would you want to keep it enabled?

## supabase-py CRUD

### CRUD Question 1

Write a function `insert_test_record(supabase)` that inserts a single row into `weather_raw` with today's date and plausible values for all four weather columns. Run it to confirm it works, then add a comment: what would happen if you ran the function twice? How would you change the call to make it safe to run multiple times?

### CRUD Question 2

Write a function `get_records_by_date_range(supabase, start, end)` that returns all rows from `weather_raw` where `date >= start` and `date <= end`. The function should return the list of row dictionaries. Test it with a date range that includes the row you inserted in Q1 and print the result.

### CRUD Question 3

In a comment block, explain the difference between `insert` and `upsert` in `supabase-py`. Give a concrete example of when you would choose each. Then write a function `safe_upsert(supabase, records)` that upserts a list of records into `weather_raw` using `date` as the conflict key and prints the number of rows affected.

## Idempotency

### Idempotency Question 1

"Idempotency" means that running an operation multiple times produces the same result as running it once. In a comment block, explain why idempotency matters for a data pipeline. Give one concrete example of what goes wrong in a non-idempotent pipeline when the script crashes halfway through and is restarted.

---

# Part 2: Project — Extract + Load Pipeline

Build `project_09.py`, a script that implements a complete Extract + Load pipeline: it fetches 2023 daily weather data from the Open-Meteo API for a city of your choice and loads it into your Supabase `weather_raw` table.

This is the same kind of data the classifier you built in Weeks 3–4 was trained on. In later weeks, you will use these rows as the input to the transform step — so make sure your column names match what the model expects.

## Step 1: Extract

Call the Open-Meteo historical archive API to retrieve daily weather data for your chosen city for the full year 2023 (start: `2023-01-01`, end: `2023-12-31`). Use these four daily variables:

- `temperature_2m_max`
- `temperature_2m_min`
- `precipitation_sum`
- `wind_speed_10m_max`

Use `response.raise_for_status()` to catch errors early. Print a summary of the response once it arrives.

## Step 2: Transform

Convert the API response from columnar format into a list of row dictionaries. Each dictionary should have keys that exactly match the column names in `weather_raw`.

Print the first and last record to confirm the transformation looks correct. Add a comment: how many records do you expect for a full year, and how many did you get? If the numbers differ, what might explain the discrepancy?

## Step 3: Load

Upsert all records into `weather_raw`. Print a confirmation message showing how many rows were upserted.

Run the script a second time and confirm the row count in `weather_raw` does not change. Add a comment: what does this tell you about idempotency?

## Step 4: Verify

After upserting, run a verification query that:
1. Prints the total number of rows in `weather_raw`
2. Prints the earliest and latest dates in the table
3. Prints the row for `2023-07-04` (or the nearest date if that date is missing)

You can also verify directly in the Supabase Table Editor — take a screenshot for the video below.

## Video

Record a short video (target: 3 minutes, max: 5). Show:

1. The script running in your terminal with no errors
2. The `weather_raw` table in your Supabase dashboard with rows visible
3. Your verification output printed to the terminal

Paste the video link in a comment at the top of `project_09.py`.

---

<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

### Required Deliverables/Tasks

**General grading notes:**

- **Student-chosen values vary.** The student picks their own city, so the specific weather values, row counts, dates, and the `2023-07-04` row contents differ. Do not fail a student for numbers that differ from any reference. A full year is ~365 rows.
- **External artifacts cannot be inspected.** The reviewer cannot see the student's Supabase project, their `.env`, the video, or their filesystem. Grade the submitted code and written answers; do not fail a student for a Supabase dashboard, a video, or a file path you cannot verify. The requirement to gitignore `.env` is a real security practice, but its presence/absence is not something the reviewer can confirm.
- **Table and column names are exact.** `Use exactly as written (Weeks 10–11 read these exact names)`: the table `weather_raw` and its columns `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `wind_speed_10m_max`, `date`. These must match the Open-Meteo API field names because later weeks feed these rows to the classifier without renaming.
- **Function names are exact where the assignment specifies them.** `Use exactly as written`: `get_client`, `insert_test_record`, `get_records_by_date_range`, `safe_upsert`. `Example — adapt to your own values`: the chosen city, latitude/longitude, and sample record values.

**Part 1 — `warmup_09.py`:**

- **Connection Q1** — a comment naming the two connection pieces (Project URL and API key), where to find them in the dashboard, and why they should never be hardcoded.
- **Connection Q2** — a `get_client()` that loads credentials via `python-dotenv`, returns a Supabase client, and raises a clear error if either environment variable is missing.
- **Connection Q3** — a comment explaining Row Level Security, why it was disabled for this course, and a real-world case where it should stay enabled.
- **CRUD Q1** — an `insert_test_record(supabase)` that inserts one row into `weather_raw` with today's date and plausible values for the four weather columns; a comment on what running it twice does and how to make it safe to repeat.
- **CRUD Q2** — a `get_records_by_date_range(supabase, start, end)` returning the matching row dictionaries, tested over a range that includes the inserted row and printed.
- **CRUD Q3** — a comment on `insert` vs `upsert` with a concrete example, plus a `safe_upsert(supabase, records)` that upserts using `date` as the conflict key and prints the number of rows affected.
- **Idempotency Q1** — a comment defining idempotency and giving one concrete failure example for a non-idempotent pipeline that crashes and restarts.

**Part 2 — `project_09.py`:**

- **Step 1 — Extract** — fetches full-year 2023 daily weather (the four variables) for the chosen city, uses `response.raise_for_status()`, and prints a summary.
- **Step 2 — Transform** — converts the columnar response into a list of row dictionaries whose keys match the `weather_raw` columns; prints the first and last record; a comment on the expected vs actual record count.
- **Step 3 — Load** — upserts all records into `weather_raw`, prints the number upserted, and confirms that a second run does not change the row count, with a comment on idempotency.
- **Step 4 — Verify** — prints the total row count, the earliest and latest dates, and the `2023-07-04` row (or nearest date).
- **Video** — a link at the top of `project_09.py` to a short video showing the script running, the `weather_raw` table with rows, and the verification output.

### Optional Deliverables/Tasks

**None.**

</details>
