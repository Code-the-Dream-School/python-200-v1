# Assignment 9 Answer Key: Cloud AI (Extract + Load to Supabase)

**Mentor note:** Week 9 connects Python to Supabase and builds an Extract + Load pipeline (Open-Meteo → `weather_raw`). Warmups mix conceptual comment-answers with runnable `supabase-py` code; the project is the E+L pipeline. Code is checkable for correct patterns (client setup, upsert, idempotency); exact weather values vary by city/run. The **video is not assessed**. The recurring theme mentors should verify is **idempotency** — the pipeline must be safely re-runnable.

---

## Expected File Setup

Assignment lives in `assignments_09/`:

```
assignments_09/
├── warmup_09.py     # conceptual answers (comments) + runnable code
├── project_09.py    # Extract + Load pipeline (video link in a top comment)
├── verify_09.sql    # SQL verification queries, results pasted as -- comments
└── .env             # SUPABASE_URL + SUPABASE_KEY — must be gitignored
```

Students who do the **optional** Practicum AWS Bridge (Part 3) also have an `aws_bridge/` folder. It holds `alert_settings.py`, `test_alert_settings.py`, and `settings_notes.md`, plus their Week 8 bridge files if they did Week 8.

Requires `supabase python-dotenv requests`. Tables from Week 8 must already exist. **Check `.env` is not committed.**

---

# Part 1: Warmup (`warmup_09.py`)

## Supabase Connection

### Connection Q1 — **Objective (concept)**
Two pieces needed: the **Project URL** and the **anon (public) API key**, both found in Project Settings → API. Should never be hardcoded because committing keys to a public repo exposes them (can be scraped in minutes) — load from environment/`.env` instead.

### Connection Q2 — **Objective (approach)**
`get_client()` loads env vars via `python-dotenv`, creates and returns `create_client(url, key)`, and **raises a clear error if either var is missing**. Reference:
```python
def get_client():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment.")
    return create_client(url, key)
```
Common miss: no error handling (returns a broken client, fails cryptically later).

### Connection Q3 — **Subjective**
RLS = **Row Level Security**, Postgres policies controlling which rows a user can read/write. Disabled here for course simplicity (single trusted user, no auth layer). Should stay **enabled** in any real multi-user app where users must only see their own data (e.g. a SaaS app with per-user records).

## supabase-py CRUD

### CRUD Q1 — **Objective (approach) + Subjective**
`insert_test_record` inserts one row into `weather_raw` with today's date + plausible values. Comment: running it **twice fails** — `date` is the PRIMARY KEY, so the second insert violates the unique constraint. Fix = use **upsert** (on conflict `date`) instead of insert.

### CRUD Q2 — **Objective (approach)**
`get_records_by_date_range` returns rows where `date` is between start and end. Correct pattern:
```python
resp = supabase.table("weather_raw").select("*").gte("date", start).lte("date", end).execute()
return resp.data
```
Returns the list of dicts; test prints the inserted row.

### CRUD Q3 — **Objective (concept + approach)**
- `insert` adds new rows and **errors on a duplicate key**; `upsert` inserts or **updates** if the key already exists.
- Use insert for guaranteed-new records; upsert when re-running or when the row may already exist.
- `safe_upsert` upserts a list with `on_conflict="date"` and prints the affected row count:
```python
resp = supabase.table("weather_raw").upsert(records, on_conflict="date").execute()
print(f"Upserted {len(resp.data)} rows")
```

## Idempotency

### Idempotency Q1 — **Subjective**
Idempotency = running the operation N times has the same effect as running it once. Matters because pipelines fail/retry and re-run. Concrete non-idempotent failure: a script using `insert` crashes halfway, is restarted, and either **errors on the already-inserted rows** or **creates duplicates** — corrupting the table. Upsert (or a pre-check) makes re-runs safe.

---

# Part 2: Project — Extract + Load Pipeline (`project_09.py`)

**Overall check:** fetches full-year 2023 weather for a chosen city and upserts it into `weather_raw`, safely re-runnable. Column names must exactly match `weather_raw` (this data feeds the Weeks 3–4 classifier later).

### Step 1: Extract — **Objective (approach)**
Calls Open-Meteo archive API for 2023-01-01 to 2023-12-31 with the four daily variables; uses `response.raise_for_status()`; prints a response summary.

### Step 2: Transform — **Objective (approach) + Subjective**
Converts the columnar response into a list of row dicts with keys **exactly matching** `weather_raw` columns (`date`, `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `wind_speed_10m_max`). Prints first + last record. Comment on expected count: **365 records** for 2023 (not a leap year). A mismatch might come from missing days or API gaps — a student getting exactly 365 is the clean case.

### Step 3: Load — **Objective (approach) + Subjective**
Upserts all records into `weather_raw`, prints the upserted count. Running a **second time keeps the row count at 365** (no duplicates) — the idempotency proof. Comment should connect this to upsert-on-conflict.

### Step 4: Verify — **Objective (approach)**
A verification query printing: total row count (365), earliest + latest dates (2023-01-01 / 2023-12-31), and the `2023-07-04` row (or nearest). Values vary by city. If the CRUD Q1 test row is still in the table, expect 366 rows and a latest date of the day the student ran the warmup (see Step 5).

### Step 5: Verify with SQL (`verify_09.sql`) — **Objective (approach) + Subjective**
A SQL cross-check of Step 4, run in the Supabase SQL Editor. This is SQL review from Python for Data Analysis (Lessons 9 and 10), apart from `IS NULL`, which Python for Data Analysis did not cover. The assignment includes a collapsible SQL syntax reminder that explains `IS NULL` and links to the Python for Data Analysis lessons. Weeks 10 and 11 link back to it. Accept any query that answers the question; aliases and `COUNT(*)` vs `COUNT(date)` are the student's choice. Sample answers:
```sql
-- Query 1: Row count and date range
SELECT
  COUNT(*)  AS total_rows,
  MIN(date) AS earliest_date,
  MAX(date) AS latest_date
FROM weather_raw;

-- Query 2: Rows with a missing weather value
SELECT COUNT(*) AS rows_with_nulls
FROM weather_raw
WHERE temperature_2m_max IS NULL
   OR temperature_2m_min IS NULL
   OR precipitation_sum  IS NULL
   OR wind_speed_10m_max IS NULL;
```
**Expected results:**
- Query 1: **366 rows**, earliest `2023-01-01`, latest = **the date the student ran CRUD Q1**. The extra row is the CRUD Q1 test record (today's date), which the assignment never asks students to delete. If the student deleted it, expect 365 rows and a latest date of `2023-12-31`. Both are correct.
- Query 2: **0**. Open-Meteo's archive data for 2023 is complete. A non-zero count usually means a transform bug, such as a row dictionary that left out one of the weather keys. (A *misspelled* key does not cause NULLs. Supabase rejects the upsert instead, because the column does not exist.)

**Closing comment:** The SQL and Python results should match, because they read the same table. The key thing to look for is whether the student explains the 366th row (the CRUD Q1 test record). A student who says "I expected 365 but got 366" without explaining it has missed the point of the check. Point them back to the warmup.

**Common trouble spots:**
- Running both queries at once and only seeing the second result. The SQL Editor shows only the last result, so highlight one query and run it on its own.
- Writing `= NULL` instead of `IS NULL`. `= NULL` never matches, so the count is always 0 even if values are missing. If a student got 0 with `= NULL`, the answer is correct by accident; point out the fix.
- Using `AND` instead of `OR` in Query 2. That counts only rows where *all four* columns are NULL.
- Using double quotes for a date, such as `WHERE date = "2023-07-04"`. Python for Data Analysis used SQLite, which accepts this, but PostgreSQL reads double quotes as a column name and raises an error. Use single quotes. The syntax reminder in the assignment covers this.

### Video — **Not assessed**
Linked in a top comment; shows the script running, the populated table, and verification output. Not graded for code.

---

# Part 3: (Optional) Practicum AWS Bridge — Settings and Secrets

**Mentor note:** This part is an **optional pilot** this term. Never ask a student to revise because they skipped it. It goes with the optional lesson `lessons/09_cloud_data/04_aws_bridge_secrets.md`. Students write a function that loads the alert's two settings, `gradebook_token` (a secret) and `submission_threshold` (a setting). It reads the environment first and then Parameter Store, and it is tested with `moto`, a fake AWS that runs locally. No AWS account is needed. The expected time is about two hours plus the lesson. Week 9 does **not** depend on the Week 8 bridge part.

New libraries: `boto3` (the AWS SDK) and `moto[ssm]`. Both are in the course `requirements.txt`.

### Task 1: Setup — **Not assessed**
Week 8 bridge files carried forward are expected. Do not tell students to delete them.

### Task 2: `alert_settings.py` — **Objective (approach)**
Names are exact, because Weeks 10 and 11 import them. Reference solution:

```python
"""Load the submission alert's settings from the environment or Parameter Store."""

import os

import boto3

PARAMETER_PREFIX = "/ctd/submission-alert/"
REGION = "us-east-1"


class MissingSettingError(Exception):
    """Raised when a setting is in neither the environment nor Parameter Store."""


def get_setting(name, ssm_client=None):
    """Return one setting as a string.

    Check the environment variable NAME (uppercase) first. If it is missing or
    empty, read the Parameter Store parameter PARAMETER_PREFIX + name.
    """
    value = os.environ.get(name.upper())
    if value:
        return value

    # Create the client only when we need it, so that the environment-variable
    # path never contacts AWS.
    if ssm_client is None:
        ssm_client = boto3.client("ssm", region_name=REGION)

    try:
        response = ssm_client.get_parameter(Name=PARAMETER_PREFIX + name, WithDecryption=True)
    except ssm_client.exceptions.ParameterNotFound:
        raise MissingSettingError(
            f"Setting '{name}' was not found. Set the environment variable "
            f"{name.upper()} or create the parameter {PARAMETER_PREFIX + name}."
        ) from None
    return response["Parameter"]["Value"]


def get_alert_settings(ssm_client=None):
    """Return the two settings the alert needs, with the threshold as a float."""
    return {
        "gradebook_token": get_setting("gradebook_token", ssm_client),
        "threshold": float(get_setting("submission_threshold", ssm_client)),
    }
```

Common mistakes:
- **Using `os.environ[name.upper()]`**, which raises `KeyError` when the variable is missing, instead of `os.environ.get(...)`.
- **Using `if value is not None:`**, which returns an empty string instead of falling back. Test case 4 catches this.
- **Forgetting `WithDecryption=True`.** In moto, as in AWS, the `SecureString` then comes back as encrypted text, so test case 3 fails with a long string that looks random. This is the most useful bug for a student to see, because it is silent in production.
- **Creating the client at the top of the module** (`ssm = boto3.client(...)` at import time). The Task 4 test does **not** catch this, because the client already exists before the test replaces `boto3.client`. A module-level client can also escape moto, because it may be created before `mock_aws` starts. Lambda code often creates clients at module level to reuse them between calls, so this pattern is not wrong for production. For this exercise, though, the spec asks for the client to be created only when needed.
- **Catching every exception** (`except Exception:`) and turning it into `MissingSettingError`. This hides real problems, such as missing permissions. Suggest catching only `ParameterNotFound`.

### Task 3: `test_alert_settings.py` — **Objective (approach)**
Six cases, using moto. Reference tests, including the Task 4 test:

```python
import boto3
import pytest
from moto import mock_aws

from alert_settings import MissingSettingError, get_alert_settings, get_setting


@pytest.fixture
def ssm(monkeypatch):
    """A fake Parameter Store. No AWS account or network is used."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    # Make sure the real environment cannot leak into the tests.
    monkeypatch.delenv("GRADEBOOK_TOKEN", raising=False)
    monkeypatch.delenv("SUBMISSION_THRESHOLD", raising=False)
    with mock_aws():
        yield boto3.client("ssm", region_name="us-east-1")


def put(ssm, name, value, secure=False):
    ssm.put_parameter(
        Name="/ctd/submission-alert/" + name,
        Value=value,
        Type="SecureString" if secure else "String",
    )


def test_environment_variable_wins(ssm, monkeypatch):
    put(ssm, "gradebook_token", "from-parameter-store", secure=True)
    monkeypatch.setenv("GRADEBOOK_TOKEN", "from-environment")
    assert get_setting("gradebook_token", ssm) == "from-environment"


def test_falls_back_to_parameter_store(ssm):
    put(ssm, "submission_threshold", "80")
    assert get_setting("submission_threshold", ssm) == "80"


def test_secure_string_is_decrypted(ssm):
    put(ssm, "gradebook_token", "gb-test-token", secure=True)
    assert get_setting("gradebook_token", ssm) == "gb-test-token"


def test_empty_environment_variable_is_ignored(ssm, monkeypatch):
    put(ssm, "submission_threshold", "75")
    monkeypatch.setenv("SUBMISSION_THRESHOLD", "")
    assert get_setting("submission_threshold", ssm) == "75"


def test_missing_setting_raises_clear_error(ssm):
    with pytest.raises(MissingSettingError, match="gradebook_token"):
        get_setting("gradebook_token", ssm)


def test_get_alert_settings_converts_threshold(ssm):
    put(ssm, "gradebook_token", "gb-test-token", secure=True)
    put(ssm, "submission_threshold", "80")
    assert get_alert_settings(ssm) == {"gradebook_token": "gb-test-token", "threshold": 80.0}


def test_creates_its_own_client_when_none_given(ssm):
    put(ssm, "submission_threshold", "80")
    assert get_setting("submission_threshold") == "80"


def test_environment_path_needs_no_aws(monkeypatch):
    def no_aws(*args, **kwargs):
        pytest.fail("get_setting created an AWS client, but the environment variable was set")

    monkeypatch.setattr("alert_settings.boto3.client", no_aws)
    monkeypatch.setenv("GRADEBOOK_TOKEN", "from-environment")
    assert get_setting("gradebook_token") == "from-environment"
```

If a student's tests pass on their machine but fail for someone else, check whether the fixture removes `GRADEBOOK_TOKEN` and `SUBMISSION_THRESHOLD`. The provided fixture does this.

### Task 4: No-AWS test — **Objective (approach)**
The `monkeypatch.setattr("alert_settings.boto3.client", ...)` path works only if the module uses `import boto3`. If the student wrote `from boto3 import client`, the path to replace is `"alert_settings.client"`. Either is fine, as long as the test fails when the function creates a client. A good way to check a student's test is to ask them to move the client creation above the environment check and confirm that the test fails.

### Task 5: `settings_notes.md` — **Subjective**
1. The token gives access to every student's submission history, so it is stored encrypted, and only roles with permission can read it in plain text. The threshold is not sensitive.
2. For example: running or testing the code locally without AWS, or overriding one value on a deployed function without editing Parameter Store.
3. AWS returns the encrypted text, and the code raises no error. The failure appears later, when the gradebook rejects the token, so the error message points far away from the real cause.
