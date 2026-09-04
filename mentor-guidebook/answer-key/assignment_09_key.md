# Assignment 9 Answer Key: Cloud AI (Extract + Load to Supabase)

**Mentor note:** Week 9 connects Python to Supabase and builds an Extract + Load pipeline (Open-Meteo → `weather_raw`). Warmups mix conceptual comment-answers with runnable `supabase-py` code; the project is the E+L pipeline. Code is checkable for correct patterns (client setup, upsert, idempotency); exact weather values vary by city/run. The **video is not assessed**. The recurring theme mentors should verify is **idempotency** — the pipeline must be safely re-runnable.

---

## Expected File Setup

Assignment lives in `assignments_09/`:

```
assignments_09/
├── warmup_09.py     # conceptual answers (comments) + runnable code
├── project_09.py    # Extract + Load pipeline (video link in a top comment)
└── .env             # SUPABASE_URL + SUPABASE_KEY — must be gitignored
```

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
A verification query printing: total row count (365), earliest + latest dates (2023-01-01 / 2023-12-31), and the `2023-07-04` row (or nearest). Values vary by city.

### Video — **Not assessed**
Linked in a top comment; shows the script running, the populated table, and verification output. Not graded for code.
