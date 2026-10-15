# Working with Tables using supabase-py

Now that Python can talk to Supabase, you need somewhere to put data. This lesson introduces the two-table schema you will use for the rest of the course, walks through creating those tables in the Supabase SQL editor, and covers the full set of read/write operations with `supabase-py`.

## Learning Objectives

By the end of this lesson, you will be able to:

- Explain the two-table design and why raw and enriched data are kept separate
- Create tables in Supabase using the SQL editor
- Use `supabase-py` to insert, select, upsert, and delete rows
- Write a filter query using `.eq()` and interpret the result

## The Two-Table Design

The pipeline you are building this week has two distinct stages: loading raw weather data, and enriching it with ML predictions and LLM output. It is tempting to put everything in one table and fill in the enrichment columns later — but keeping raw and enriched data in separate tables is a better design for three reasons.

**Raw data should be immutable.** Once you load a day's weather record from the API, you should not overwrite or mutate it. If the enrichment step has a bug and produces wrong output, you want to be able to re-run it against the original data. If everything is in one table with nullable enrichment columns, it is easy to accidentally modify raw records. Two tables make the boundary explicit.

**Each stage is independently queryable.** With two tables, you can ask "how many records have been enriched?" or "which dates are in `weather_raw` but not yet in `weather_enriched`?" with a simple query. With a single table, distinguishing processed from unprocessed records requires checking multiple nullable columns.

**The separation mirrors the pipeline stages.** In Week 11 you will orchestrate this as a Prefect flow with distinct extract, transform, and load tasks. The two-table design maps directly onto that structure: the extract task writes to `weather_raw`, the transform task reads from it and writes to `weather_enriched`.

## Creating the Tables

> **Did you do this in Week 8?** The Week 8 assignment asked you to create both tables and disable RLS on them. If you did, do **not** run the `CREATE TABLE` statements below again. Postgres will return an error such as `relation "weather_raw" already exists`. Open the **Table Editor** instead and check that both tables are there with the columns shown below. Then read the notes after the SQL, because they explain the design, and continue with "CRUD Operations with supabase-py". If you have not created the tables yet, run both SQL blocks in this section.

Open your Supabase project dashboard and navigate to the **SQL Editor** (the `</>` icon in the left sidebar). Run the following SQL to create both tables:

```sql
CREATE TABLE weather_raw (
  date                  date        PRIMARY KEY,
  temperature_2m_max    numeric,
  temperature_2m_min    numeric,
  precipitation_sum     numeric,
  wind_speed_10m_max    numeric,
  loaded_at             timestamptz DEFAULT now()
);

CREATE TABLE weather_enriched (
  date              date        PRIMARY KEY REFERENCES weather_raw(date),
  good_for_running  boolean,
  confidence        numeric,
  llm_summary       text,
  enriched_at       timestamptz DEFAULT now()
);
```

A few things worth noting:

- `date` is the primary key in both tables. Because weather data is one record per day, the date is a natural, unique identifier — no auto-increment ID is needed.
- `weather_enriched.date` references `weather_raw.date` with a foreign key. This constraint enforces that you can only add an enriched record for a date that already exists in `weather_raw`. The database will reject any enrichment of data that was not first loaded.
- `loaded_at` and `enriched_at` use `DEFAULT now()`, which means Postgres automatically records the timestamp of insertion — you do not need to set these in your Python code.
- The column names (`temperature_2m_max`, etc.) match the field names from the Open-Meteo API response, which in turn match the feature names the ML classifier was trained on in Week 3. Keeping them consistent means no renaming is needed when you pass records to the classifier later.

After running the SQL, navigate to the **Table Editor** to confirm both tables appear with the correct columns.

### Disabling Row Level Security

Supabase enables RLS on new tables by default. For this course, disable it on both tables so your scripts can read and write freely without configuring access policies:

```sql
ALTER TABLE weather_raw     DISABLE ROW LEVEL SECURITY;
ALTER TABLE weather_enriched DISABLE ROW LEVEL SECURITY;
```

Run this in the SQL Editor immediately after creating the tables.

## CRUD Operations with supabase-py

The `supabase-py` SDK uses a fluent (method-chaining) style. Every operation ends with `.execute()`, which sends the request and returns a response object. The actual data is in `response.data` — a list of dictionaries.

### Inserting Rows

```python
record = {
    "date":               "2023-01-01",
    "temperature_2m_max": 12.3,
    "temperature_2m_min": 4.1,
    "precipitation_sum":  0.0,
    "wind_speed_10m_max": 18.5,
}

response = supabase.table("weather_raw").insert(record).execute()
print(response.data)
```

You can also insert a list of records in a single call, which is far more efficient than inserting one row at a time:

```python
records = [
    {"date": "2023-01-01", "temperature_2m_max": 12.3, ...},
    {"date": "2023-01-02", "temperature_2m_max": 9.7, ...},
]

response = supabase.table("weather_raw").insert(records).execute()
print(f"Inserted {len(response.data)} rows")
```

### Selecting Rows

```python
response = supabase.table("weather_raw").select("*").execute()
rows = response.data  # list of dicts

for row in rows[:3]:
    print(row)
```

To select specific columns rather than all of them, pass a comma-separated string:

```python
response = supabase.table("weather_raw").select("date, temperature_2m_max").execute()
```

### Filtering with .eq()

To retrieve a specific row, chain a filter before `.execute()`:

```python
response = (
    supabase.table("weather_raw")
    .select("*")
    .eq("date", "2023-01-15")
    .execute()
)
print(response.data)  # list with zero or one item
```

`.eq("column", value)` is the equality filter. Other useful filters include `.gte()` (≥), `.lte()` (≤), `.neq()` (≠), and `.in_("column", [list])`. You can chain multiple filters and they are combined with AND.

### Upsert: Insert or Update on Conflict

Plain `insert` raises an error if a row with the same primary key already exists. This is a problem for pipelines that may run more than once on the same data. The solution is `upsert`, which inserts a new row if the key is new and updates the existing row if it is not:

```python
response = (
    supabase.table("weather_raw")
    .upsert(records, on_conflict="date")
    .execute()
)
```

`on_conflict="date"` tells Supabase which column to check for conflicts. With upsert, re-running the pipeline on data you have already loaded is safe — the rows will be updated in place rather than duplicated or erroring. This property — where running a pipeline multiple times produces the same result as running it once — is called **idempotency**, and it is a key quality of robust data pipelines.

### Deleting Rows

```python
response = (
    supabase.table("weather_raw")
    .delete()
    .eq("date", "2023-01-01")
    .execute()
)
```

Always pair `delete()` with a filter. Without one, Supabase will delete every row in the table.

## Putting It Together: A Complete CRUD Script

```python
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Insert a test record
record = {
    "date":               "2023-06-15",
    "temperature_2m_max": 28.4,
    "temperature_2m_min": 17.2,
    "precipitation_sum":  0.0,
    "wind_speed_10m_max": 12.1,
}
supabase.table("weather_raw").insert(record).execute()
print("Inserted.")

# Read it back
response = supabase.table("weather_raw").select("*").eq("date", "2023-06-15").execute()
print("Retrieved:", response.data)

# Upsert (update the max temp — same date, different value)
updated = {**record, "temperature_2m_max": 29.0}
supabase.table("weather_raw").upsert(updated, on_conflict="date").execute()

# Confirm the update
response = supabase.table("weather_raw").select("*").eq("date", "2023-06-15").execute()
print("After upsert:", response.data[0]["temperature_2m_max"])  # 29.0

# Clean up
supabase.table("weather_raw").delete().eq("date", "2023-06-15").execute()
print("Deleted.")
```

## Check for Understanding

1. You call `supabase.table("weather_raw").insert(record).execute()` and get an error saying the date already exists. What is the right fix?

    - A. Delete the existing row first, then insert
    - B. Use `.upsert(record, on_conflict="date")` instead of `.insert()`
    - C. Change the primary key to an auto-increment integer
    - D. Set `overwrite=True` in the insert call

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. <code>upsert</code> with <code>on_conflict</code> handles the case where the row may or may not already exist. It inserts if new, updates if not — no delete-then-insert required.
    </details>

2. You run `supabase.table("weather_raw").delete().execute()` with no filter. What happens?

    - A. Nothing — delete requires a filter to run
    - B. Supabase raises an error requiring at least one `.eq()` call
    - C. Every row in the table is deleted
    - D. The most recently inserted row is deleted

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: C. Without a filter, <code>delete()</code> removes all rows. Always pair <code>delete()</code> with a filter unless you intentionally want to empty the table.
    </details>

3. Why does `weather_enriched.date` have a foreign key reference to `weather_raw.date`?

    - A. To automatically copy data from `weather_raw` when a new enriched record is inserted
    - B. To enforce that enriched records can only be created for dates that already exist in `weather_raw`
    - C. To allow faster queries by sharing an index between the two tables
    - D. To prevent duplicate dates in `weather_raw`

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. The foreign key is a data integrity constraint. It prevents the enrichment step from writing results for a date that was never loaded into <code>weather_raw</code> — catching bugs in pipeline ordering at the database level rather than in application code.
    </details>

## Lesson Wrap-Up

The two-table schema — `weather_raw` for API data, `weather_enriched` for classifier and LLM output — keeps raw data immutable and makes each pipeline stage independently queryable. `supabase-py` wraps all database operations in a clean fluent API: insert, select, upsert, delete. Upsert with `on_conflict` is the right default for pipeline writes — it makes your load step idempotent and safe to re-run.

In the next lesson, you will call the Open-Meteo API to fetch a full year of daily weather data and load it into `weather_raw` using everything you have learned in the last two lessons.
