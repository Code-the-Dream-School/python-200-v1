# Week 9 Mentor Summary: Data in the Cloud

**Lesson files:** `lessons/09_cloud_AI.md` (overview) and four lessons in `lessons/09_cloud_data/`, one of them optional
**Assignment file:** `assignments/09_cloud_AI.md`
**Answer key:** `mentor-guidebook/answer-key/assignment_09_key.md`
**Slides:** `mentor-guidebook/slides/09_cloud_data.pdf`

**Learning objective:** Students connect a Python script to a Supabase cloud database with credentials loaded from a `.env` file. They read and write rows with the `supabase-py` SDK, and they build an Extract + Load pipeline that fetches a year of daily weather from Open-Meteo and upserts it into `weather_raw`. They then check the loaded data twice, once with Python and once with SQL.

**Where this fits:** Students use the Supabase project and the two tables they created in Week 8. The Open-Meteo request and its four weather variables come from the Week 3 project, and the SQL review comes from Python for Data Analysis. In Week 10, students read `weather_raw`, run the Week 4 `WeatherClassifier` and an LLM on each row, and write the results to `weather_enriched`. Week 11 runs the whole pipeline as a Prefect flow. Students need to keep their `weather_raw` data.

---

## Lesson Overview

The lessons use Charlotte, NC, and the 2023 calendar year, which gives 365 rows. In the assignment, each student chooses their own city.

| Lesson | What students learn |
|---|---|
| **1. Connecting to Supabase from Python** | Supabase as a hosted PostgreSQL database that stores rows and columns. The Project URL and the anon key. Storing them in `.env`, excluding `.env` with `.gitignore`, and loading them with `python-dotenv` and `os.getenv()`. Creating a client with `create_client` and checking it against a small test table. A first note on Row Level Security (RLS). |
| **2. Working with Tables using supabase-py** | The two-table design: `weather_raw` for API data and `weather_enriched` for model output. The `date` primary key and the foreign key between the tables. The SQL to create the tables and disable RLS. CRUD operations: `insert`, `select`, `.eq()` and other filters, `upsert` with `on_conflict="date"`, and `delete`. The definition of **idempotency**. |
| **3. The Extract + Load Pipeline** | Calling the Open-Meteo archive API with `raise_for_status()`. Converting the columnar response (parallel lists) into a list of row dictionaries. Handling missing values. Upserting all rows and checking the result with `count="exact"` and spot checks. A complete script labeled Extract, Transform, and Load. |
| **4. (Optional) Practicum AWS Bridge, Part 2: Settings and Secrets** | The difference between a setting and a secret. Lambda environment variables and AWS Parameter Store, with `String` and `SecureString` parameters. Reading a parameter with `boto3`, using `WithDecryption=True`, and catching `ParameterNotFound`. Testing without an AWS account by using `moto`'s `mock_aws` and pytest's `monkeypatch` fixture. |

---

## Assignment Deliverables

**Setup:** Students work in `assignments_09/` and install `supabase`, `python-dotenv`, and `requests`. Their Week 8 tables must already exist, and their `.env` file must be listed in `.gitignore` before they commit.

**Grading:** Weather values differ for every student, because each student chooses a city. The function names (`get_client`, `insert_test_record`, `get_records_by_date_range`, `safe_upsert`), the table name, and the column names must be exactly as written, because Weeks 10 and 11 depend on them. A row count of 365 or 366 is correct, as long as the student explains it. The answer key says that the video is not assessed. The theme to check throughout is idempotency: the pipeline must be safe to run again.

| Part | File | What students do | Concepts practiced |
|---|---|---|---|
| Warmup: Connection Q1–Q3 | `warmup_09.py` | Explains the two connection values and why they are never hardcoded, writes `get_client()` with a clear error for a missing variable, and explains RLS | `.env`, `python-dotenv`, RLS |
| Warmup: CRUD Q1–Q3, Idempotency Q1 | `warmup_09.py` | Inserts a test row with today's date, queries a date range with `.gte()` and `.lte()`, compares `insert` and `upsert`, writes `safe_upsert`, and explains idempotency with a crash-and-restart example | CRUD, upsert, idempotency |
| Project, Steps 1–3 | `project_09.py` | Fetches 2023 daily weather for a chosen city, reshapes it into row dictionaries, upserts it into `weather_raw`, and runs the script again to show that the row count does not change | Extract + Load |
| Project, Step 4 | `project_09.py` | Prints the row count, the earliest and latest dates, and the `2023-07-04` row | Verifying a load in Python |
| Project, Step 5 | `verify_09.sql` | Writes two queries in the SQL Editor: one with `COUNT`, `MIN`, and `MAX`, and one that counts rows with a `NULL` in any weather column. Pastes each result as a `--` comment and explains any unexpected row count. | SQL review, `IS NULL` |
| Video | link at the top of `project_09.py` | A video (target 3 minutes, maximum 5) that shows the script running, the table with rows, and the verification output | Navigating cloud tools |
| (Optional) Part 3: AWS Bridge | `aws_bridge/` | Writes `alert_settings.py`, tests it with `moto` in `test_alert_settings.py`, and answers three questions in `settings_notes.md` | `boto3`, `moto`, `monkeypatch` |

**Optional:** Part 3 is an ungraded pilot, and students may skip it with no effect on their grade. It does not depend on the Week 8 bridge. If a student attempts it, give feedback using the notes at the end of the answer key. Files carried over from Week 8 are expected in `aws_bridge/`.

**Submission:** A pull request from the student's branch into `main` in their `python200-homework` repository. The `.env` file must not be committed.

---

## Key Concepts

These short explanations cover the ideas students ask about most this week. Expand any one you need.

<details>
<summary><strong>Idempotency, and why the load step uses upsert</strong></summary>

An operation is **idempotent** when running it many times gives the same result as running it once. Pipelines fail and are run again, so the load step must be idempotent.

Plain `insert` raises an error when a row with the same primary key already exists. Because `date` is the primary key of `weather_raw`, a second run of an `insert`-based script fails on the first date that is already in the table. This is the answer to CRUD Question 1.

`upsert(records, on_conflict="date")` inserts a row when its date is new and updates the existing row when it is not. Running the script twice therefore leaves exactly one row per date. Step 3 asks students to prove this by running the script again and showing that the row count stays the same.

For Idempotency Question 1, a good example is an `insert` script that crashes halfway and is restarted. The restarted run either fails on the rows that were already inserted or, in a table without a unique key, creates duplicates.

</details>

<details>
<summary><strong>Two tables, a primary key, and a foreign key</strong></summary>

The course keeps raw data and model output in separate tables. Lesson 2 gives three reasons:

- **Raw data should stay unchanged.** If the enrichment step has a bug, students can run it again against the original data.
- **Each stage can be queried on its own.** For example, a query can list the dates in `weather_raw` that are not yet in `weather_enriched`. Week 10 uses this query for incremental processing.
- **The tables match the pipeline stages.** In the Week 11 Prefect flow, one task writes to `weather_raw`, and the transform task reads from it.

`date` is the primary key in both tables, because there is one record per day. `weather_enriched.date` is also a foreign key that references `weather_raw.date`. The database therefore rejects an enriched row for any date that was never loaded.

The column names match the Open-Meteo field names and the classifier's features, so Week 10 can pass rows to the model without renaming any columns.

</details>

<details>
<summary><strong>The SQL check: IS NULL, and PostgreSQL compared with SQLite</strong></summary>

Step 5 reviews SQL from Python for Data Analysis, which used SQLite. The only new syntax is `IS NULL`. `NULL` means "no value," and it is never equal to anything, not even another `NULL`. A condition such as `precipitation_sum = NULL` therefore never matches, and the count is always 0. Students must write `IS NULL`, and they must join the four column checks with `OR`. Using `AND` counts only the rows where all four columns are missing.

Supabase runs PostgreSQL, which differs from SQLite in two ways that matter here. Text and dates go in single quotes, as in `WHERE date = '2023-07-04'`. PostgreSQL reads double quotes as a column name, so `"2023-07-04"` causes an error. Boolean columns, such as `good_for_running` in Week 10, are compared with `true` or `false`, not with `1` or `0`.

The assignment's collapsible syntax reminder covers all of this, and Weeks 10 and 11 refer back to it.

</details>

---

## FAQs and Common Trouble Spots

**1. "Do I create the tables again in Lesson 2? I already created them in Week 8."**
No. Lessons 1 and 2 now tell students who finished the Week 8 setup to skip project creation and the `CREATE TABLE` step. Running `CREATE TABLE` again gives an error saying that the table already exists, which is harmless. Students do not need a second Supabase project.

**2. "My connection test prints an empty list, but I added the row."**
Supabase turns RLS on for new tables, and the anon key cannot read rows from a table with RLS on and no access rules. Lesson 1 now creates `connection_test` with SQL that disables RLS and inserts the row. An empty list usually means the student created the table in the Table Editor instead, or skipped the `ALTER TABLE` line. Ask them to run the `ALTER TABLE ... DISABLE ROW LEVEL SECURITY` line for `connection_test` and try again.

**3. "`os.getenv("SUPABASE_URL")` returns `None`."**
The `.env` file is usually in a different folder from the one where the script runs, or a variable name has a typo. The `get_client()` function in Connection Question 2 should raise a clear error in this case, so the problem is easy to find.

**4. "I expected 365 rows, but I have 366, and the latest date is today."**
This result is expected. The extra row is the test record from CRUD Question 1, which used today's date, and the assignment never asks students to delete it. A student who deleted it will see 365 rows, and both results are correct. The answer key says that the important thing is whether the student explains the extra row.

**5. "The SQL Editor shows only one of my results," or "My NULL count is 0, but I used `= NULL`."**
When several queries run at once, the SQL Editor shows only the result of the last one. Students should highlight one query and click **Run**. A 0 from `= NULL` is correct only by accident, so point out the fix to `IS NULL`. Query 2 should return 0, because the 2023 archive data is complete.

**6. "My column names are slightly different. Does that matter?"**
Yes. The dictionary keys must exactly match the `weather_raw` column names, because Week 10 passes these rows to the classifier without renaming them. A misspelled key makes Supabase reject the upsert, because that column does not exist. A NULL count above 0 in Query 2 usually means that the code left a key out of some row dictionaries.

**7. "(Optional bridge) My token comes back as a long random string," or "My tests pass on my computer but fail on someone else's."**
A long random-looking string means `WithDecryption=True` is missing, so AWS returned the encrypted `SecureString`. Python raises no error in that case. Tests that behave differently on different computers usually read `GRADEBOOK_TOKEN` or `SUBMISSION_THRESHOLD` from the shell. The provided fixture removes these variables with `monkeypatch.delenv`, so ask the student to use it.
