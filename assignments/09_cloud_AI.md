# Week 9 Assignments

This week you connected Python to a cloud database, learned to read and write rows with `supabase-py`, and built an Extract + Load pipeline that pulls weather data from the Open-Meteo API and stores it in Supabase. The warmup checks your understanding of those concepts and gives you practice with the SDK. The project has you build the pipeline end-to-end.

---

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_09/`. Inside that folder, create:

1. `warmup_09.py` — warmup exercises (conceptual answers as comments, code as runnable Python)
2. `project_09.py` — the Extract + Load pipeline
3. `verify_09.sql` — your SQL verification queries, with their results pasted as comments
4. `.env` — your Supabase credentials (**add `.env` to your `.gitignore` before committing**)

If you choose to do the optional Practicum AWS Bridge in Part 3, also create an `aws_bridge/` folder inside `assignments_09/`. Part 3 lists the files that go in it.

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

## Step 5: Verify with SQL

In Step 4, you checked your data with Python. In this step, you check the same data with SQL. This is a review of the SQL you learned in Python for Data Analysis. The only new piece of syntax is `IS NULL`, which the syntax reminder below explains.

In Week 8, you used the Supabase **SQL Editor** (the `</>` icon in the left sidebar) to create your tables. You can also use the SQL Editor to query those tables. Create a file called `verify_09.sql` and write two queries in it:

1. **Row count and date range.** Write one query that returns the total number of rows in `weather_raw`, the earliest `date`, and the latest `date`. Use `COUNT`, `MIN`, and `MAX`.
2. **Missing values.** Write one query that counts how many rows in `weather_raw` have a `NULL` value in at least one of the four weather columns. Use `IS NULL` and `OR`.

<details>
<summary><strong>SQL syntax reminder (click to expand)</strong></summary>

It has been a few months since you last wrote SQL. For a full review, reread [Python for Data Analysis Lesson 9: Introduction to Databases and SQL](https://github.com/Code-the-Dream-School/python-essentials-v2/blob/main/lessons/09Introduction%20to%20Databases%20and%20SQL.md) and [Python for Data Analysis Lesson 10: Advanced SQL and Database Integration](https://github.com/Code-the-Dream-School/python-essentials-v2/blob/main/lessons/10Advanced%20SQL%20and%20Database%20Integration.md).

The table below lists the SQL you need for Weeks 9, 10, and 11. The examples use the `customers`, `orders`, `employees`, and `departments` tables from Python for Data Analysis, not your weather tables.

| To do this | Use this pattern |
|---|---|
| Count rows, and find the smallest and largest value | `SELECT COUNT(*), MIN(salary), MAX(salary) FROM employees;` |
| Give a result column a name | `SELECT COUNT(*) AS total_orders FROM orders;` |
| Keep only rows that match every condition | `WHERE salary > 50000 AND department_id = 2` |
| Keep rows that match at least one condition | `WHERE department_id = 1 OR department_id = 2` |
| Find rows where a value is missing (**new**) | `SELECT * FROM departments WHERE manager_id IS NULL;` |
| Keep every row from the left table, matched or not | `FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id` |
| Find left-table rows with no match (**new**) | Add `WHERE o.order_id IS NULL` to the `LEFT JOIN` above |
| Count rows in each group | `SELECT department_id, COUNT(*) FROM employees GROUP BY department_id;` |
| Use the result of one query inside another | `WHERE salary = (SELECT MAX(salary) FROM employees)` |
| Round a number | `ROUND(AVG(salary), 1)` |
| Sort the results | `ORDER BY salary` (add `DESC` for largest first) |

The two rows marked **new** use `IS NULL`, which Python for Data Analysis did not cover. `NULL` means "no value." You cannot check for it with `=`, because `NULL` is never equal to anything, not even another `NULL`. Always write `IS NULL`, or `IS NOT NULL` for the opposite.

**Python for Data Analysis used SQLite. Supabase uses PostgreSQL.** Almost all the SQL above works the same way in both. Two differences matter for these exercises:

- Put text and dates in **single quotes**, such as `WHERE date = '2023-07-04'`. PostgreSQL reads double quotes as the name of a column, so `"2023-07-04"` causes an error.
- `good_for_running` is a **boolean** column. Compare it with `true` or `false`, such as `WHERE good_for_running = true`. In SQLite you may have used `1` and `0`, but PostgreSQL raises an error if you compare a boolean to a number.

</details>

Run each query in the SQL Editor. Then paste the result below the query as a SQL comment. A SQL comment is any line that starts with `--`. Use this format:

```sql
-- Query 1: Row count and date range
SELECT ...
FROM weather_raw;

-- Result:
-- total_rows | earliest_date | latest_date
-- ...        | ...           | ...
```

**Tip:** Run one query at a time. To do this, highlight the query and click **Run**. If you run several queries at once, the SQL Editor shows only the result of the last one.

At the bottom of `verify_09.sql`, add a comment that answers these questions:

- Do your SQL results match your Python results from Step 4?
- Is the row count exactly what you expected for one year of daily data? Is the latest date what you expected? If either one is different, explain why. Look back at every place in this assignment where you wrote rows to `weather_raw`.

## Video

Record a short video (target: 3 minutes, max: 5). Show:

1. The script running in your terminal with no errors
2. The `weather_raw` table in your Supabase dashboard with rows visible
3. Your verification output printed to the terminal

Paste the video link in a comment at the top of `project_09.py`.

---

# Part 3: (Optional) Practicum AWS Bridge — Settings and Secrets

> **This entire part is optional.** The Practicum AWS Bridge is a pilot this term. You can skip all of Part 3 without any effect on your grade.

This part goes with the optional lesson [Practicum AWS Bridge, Part 2: Settings and Secrets](../lessons/09_cloud_data/04_aws_bridge_secrets.md). The bridge builds an automatic alert that tells the Code the Dream teaching team when fewer than 80% of students submit their weekly assignment. This week, you write the code that loads the alert's two settings, first from environment variables and then from AWS Parameter Store. You test it with `moto`, which runs a fake AWS on your computer. You do not need an AWS account.

Plan for about two hours, in addition to the optional lesson.

## Task 1: (Optional) Set Up the Folder

Create a folder called `aws_bridge/` inside `assignments_09/`.

If you did the bridge in Week 8, copy everything from `assignments_08/aws_bridge/` into the new folder. **This week adds files to that folder. Keep your Week 8 files**, because Week 11 uses them again. If you skipped Week 8, start with an empty folder. Nothing this week depends on Week 8.

Install the two new libraries in your course environment:

```bash
uv pip install boto3 "moto[ssm]"
```

## Task 2: (Optional) Write the Settings Loader

Create `aws_bridge/alert_settings.py` with the three items below.

Use exactly as written: the file name `alert_settings.py`, the names `MissingSettingError`, `get_setting`, and `get_alert_settings`, their parameters, the two setting names `gradebook_token` and `submission_threshold`, and the parameter prefix `/ctd/submission-alert/`. Weeks 10 and 11 of the bridge import this code by name.

1. **`MissingSettingError`** is an exception class that inherits from `Exception`.

2. **`get_setting(name, ssm_client=None)`** returns one setting as a string. It follows these steps in order:
    1. Read the environment variable whose name is `name` in uppercase. For example, `get_setting("gradebook_token")` reads `GRADEBOOK_TOKEN`. If the variable exists and is not an empty string, return its value.
    2. Otherwise, read the Parameter Store parameter `/ctd/submission-alert/` + `name`, with `WithDecryption=True`, and return its value. If `ssm_client` is `None`, create a client with `boto3.client("ssm", region_name="us-east-1")`. Create the client only in this step, so that step 1 never contacts AWS.
    3. If the parameter does not exist, catch `ssm_client.exceptions.ParameterNotFound` and raise `MissingSettingError` instead. The error message includes the setting's name, the environment variable's name, and the parameter's full name, so that the reader knows how to fix the problem.

3. **`get_alert_settings(ssm_client=None)`** returns a dictionary with two keys. Pass `ssm_client` through to `get_setting` for both settings.
    - `"gradebook_token"`: the value of the `gradebook_token` setting, as a string
    - `"threshold"`: the value of the `submission_threshold` setting, converted to a `float`

## Task 3: (Optional) Test the Settings Loader

Create `aws_bridge/test_alert_settings.py`. You can use this fixture as written. It gives each test a fake, empty Parameter Store, and it removes the two environment variables, so that your own shell's settings cannot affect the tests:

```python
import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def ssm(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.delenv("GRADEBOOK_TOKEN", raising=False)
    monkeypatch.delenv("SUBMISSION_THRESHOLD", raising=False)
    with mock_aws():
        yield boto3.client("ssm", region_name="us-east-1")
```

Inside a test, create the parameters you need with `ssm.put_parameter(...)`, and set environment variables with `monkeypatch.setenv(...)`. Write tests for at least these six cases:

1. When both the environment variable and the parameter exist, the environment variable's value is returned.
2. When only the parameter exists, the parameter's value is returned.
3. A `SecureString` parameter is returned in decrypted form, so the value equals the plain text you stored.
4. An environment variable that is set to an empty string is ignored, and the parameter's value is returned.
5. When neither exists, `get_setting` raises `MissingSettingError`. Use `pytest.raises` with `match=` to check that the message contains the setting's name.
6. `get_alert_settings` returns the token as a string and the threshold as a `float`. For example, a stored `"80"` becomes `80.0`.

Run `pytest` and confirm that every test passes. If you copied your Week 8 files, their tests run too.

## Task 4: (Optional) Prove That the Environment Path Skips AWS

Add one more test that checks the promise in Task 2, step 2: when the environment variable is set, `get_setting` does not create an AWS client.

Do not use the `ssm` fixture in this test. Instead, use `monkeypatch.setattr` to replace `boto3.client` inside your module with a function that calls `pytest.fail(...)`. Then set the environment variable and call `get_setting` without a client. If your function creates a client, the test fails with your message.

Example — adapt the message to your own wording:

```python
def test_environment_path_needs_no_aws(monkeypatch):
    def no_aws(*args, **kwargs):
        pytest.fail("get_setting created an AWS client, but the environment variable was set")

    monkeypatch.setattr("alert_settings.boto3.client", no_aws)
    ...
```

## Task 5: (Optional) Short Answers

Create `aws_bridge/settings_notes.md` and answer these questions in two or three sentences each:

1. Why is `gradebook_token` a `SecureString` parameter, while `submission_threshold` can be a `String` parameter?
2. Give one situation where it is useful that `get_setting` checks the environment variable before Parameter Store.
3. A teammate removes `WithDecryption=True` from your code. What happens when the alert reads `gradebook_token`, and why is this kind of bug hard to notice?

---

<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

### Required Deliverables/Tasks

**General grading notes:**

- **Part 3 (Practicum AWS Bridge) is entirely optional.** It is a pilot this term. All of its tasks are listed under Optional Deliverables/Tasks below. Never fail a student for skipping it.

- **Student-chosen values vary.** The student picks their own city, so the specific weather values, row counts, dates, and the `2023-07-04` row contents differ. Do not fail a student for numbers that differ from any reference. A full year is ~365 rows.
- **External artifacts cannot be inspected.** The reviewer cannot see the student's Supabase project, their `.env`, the video, or their filesystem. Grade the submitted code and written answers; do not fail a student for a Supabase dashboard, a video, or a file path you cannot verify. The requirement to gitignore `.env` is a real security practice, but its presence/absence is not something the reviewer can confirm.
- **Table and column names are exact.** `Use exactly as written (Weeks 10–11 read these exact names)`: the table `weather_raw` and its columns `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `wind_speed_10m_max`, `date`. These must match the Open-Meteo API field names because later weeks feed these rows to the classifier without renaming.
- **SQL queries vary.** Accept any query in `verify_09.sql` that answers the question asked. For example, `COUNT(*)` and `COUNT(date)` are both correct, and column aliases are the student's choice. The pasted results vary by city. Many students will see 366 rows and a latest date in the current year, because the CRUD Q1 test row (today's date) is still in `weather_raw`. This is expected. Credit a student who notices it and explains it.
- **Function names are exact where the assignment specifies them.** `Use exactly as written`: `get_client`, `insert_test_record`, `get_records_by_date_range`, `safe_upsert`. `Example — adapt to your own values`: the chosen city, latitude/longitude, and sample record values.
- **Video link** — a link to a short narrated video posted somewhere accessible, pasted in a comment at the top of `project_09.py`. The reviewer cannot open or verify the video; grade only that a link is present, and do not fail for length or content that cannot be inspected.

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

**`verify_09.sql`:**

- **Step 5 — Verify with SQL** — a `verify_09.sql` file with two queries, each followed by its pasted result as a `--` comment: (1) one query returning the row count, earliest date, and latest date of `weather_raw` using `COUNT`, `MIN`, and `MAX`; (2) one query counting rows with a `NULL` in any of the four weather columns using `IS NULL` and `OR`. A closing comment says whether the SQL results match the Step 4 Python results, and explains any unexpected row count or latest date.
- **Video** — a link at the top of `project_09.py` to a short video showing the script running, the `weather_raw` table with rows, and the verification output.

### Optional Deliverables/Tasks

- **Part 3 — (Optional) Practicum AWS Bridge: Settings and Secrets.** This entire part is an optional pilot. Do **not** fail or ask for revisions from a student who skipped any or all of Part 3, and do not count a missing `aws_bridge/` folder against them. If the student attempted Part 3, give feedback on what they submitted, using the notes below. A partial attempt is acceptable.
    - **Task 1 (setup)** — an `aws_bridge/` folder. Files carried over from Week 8 (`iam_checker.py`, `test_iam_checker.py`, `submission_alert_policy.json`, `policy_notes.md`) are expected and must not be flagged as extra files. A student who skipped Week 8 will not have them, which is also fine.
    - **Task 2 (`alert_settings.py`)** — `MissingSettingError`, `get_setting(name, ssm_client=None)`, and `get_alert_settings(ssm_client=None)`. `Use exactly as written (later tasks depend on these names)`: the file name, these three names and their parameters, the setting names `gradebook_token` and `submission_threshold`, the prefix `/ctd/submission-alert/`, and the dictionary keys `"gradebook_token"` and `"threshold"`. Behavior to check: the uppercase environment variable is used when it is non-empty; otherwise the parameter is read with `WithDecryption=True`; a client is created only when Parameter Store is needed; `ParameterNotFound` is turned into `MissingSettingError` with a helpful message; the threshold is returned as a `float`.
    - **Task 3 (`test_alert_settings.py`)** — tests for the six listed cases, using moto. The provided fixture may be used exactly as given. `Example — adapt to your own layout`: test names, parameter values, and the order of the tests.
    - **Task 4 (no-AWS test)** — a test that replaces `boto3.client` with `monkeypatch.setattr` and confirms that `get_setting` returns the environment variable's value without creating a client. `Example — adapt to your own layout`: the failure message.
    - **Task 5 (`settings_notes.md`)** — (1) the token is a secret that would give access to student data, so it is stored encrypted, while the threshold is not sensitive; (2) any reasonable situation, such as running the code locally without AWS, running tests, or overriding one value on a deployed function; (3) without decryption, AWS returns the encrypted text, the code continues without an error, and the gradebook rejects the token later, so the error appears far from its cause. Accept any reasonable wording.

</details>
