# The Extract + Load Pipeline

You have a Supabase project, two tables, and a working Python client. Now you will put them to use: fetch a year of daily weather data from the Open-Meteo API and load it into `weather_raw`. This is the Extract + Load pattern — the first two legs of the ETL pipeline you will complete in Weeks 10 and 11.

## Learning Objectives

By the end of this lesson, you will be able to:

- Fetch daily weather data from the Open-Meteo historical API
- Transform an API response into a list of records suitable for database insertion
- Upsert records into `weather_raw` and verify the load with a select query
- Explain why upsert is preferred over insert for pipeline load steps

## The Open-Meteo Historical API

You used the Open-Meteo API in Week 3 to train the weather classifier. The same API, the same four variables, and the same date range will feed the pipeline here. Using the same data ensures that when Week 10 runs the saved classifier against `weather_raw`, the feature values match what the model was trained on.

A quick review of the API call for Charlotte, NC:

```python
import requests

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude":  35.23,
    "longitude": -80.84,
    "start_date": "2023-01-01",
    "end_date":   "2023-12-31",
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "wind_speed_10m_max",
    ],
    "timezone": "America/New_York",
}

response = requests.get(url, params=params)
response.raise_for_status()
data = response.json()
```

`raise_for_status()` raises an exception immediately if the server returned a 4xx or 5xx response. Call it on every API request in a pipeline — silent failures are much harder to debug than explicit ones.

## Transforming the Response into Records

The API returns data in a columnar format: a dictionary of parallel lists, one per field. To insert it into Supabase, you need to convert it into a list of row dictionaries — one dictionary per day.

```python
daily = data["daily"]

records = [
    {
        "date":               daily["time"][i],
        "temperature_2m_max": daily["temperature_2m_max"][i],
        "temperature_2m_min": daily["temperature_2m_min"][i],
        "precipitation_sum":  daily["precipitation_sum"][i],
        "wind_speed_10m_max": daily["wind_speed_10m_max"][i],
    }
    for i in range(len(daily["time"]))
]

print(f"Prepared {len(records)} records")
print("First record:", records[0])
```

For the 2023 date range, this produces 365 records. The `date` field comes from the `"time"` key in the API response — Open-Meteo uses `"time"` as the field name, but the value is a plain date string (`"2023-01-01"`), which maps directly to the `date` column in Postgres.

### Handling Missing Values

Weather stations occasionally fail to record a reading, and Open-Meteo represents missing values as `null` in JSON (which becomes `None` in Python). The `numeric` columns in Supabase accept `NULL`, so `None` values will be inserted as-is without error. If you want to exclude incomplete records:

```python
records = [r for r in records if all(v is not None for v in r.values())]
print(f"Records after dropping nulls: {len(records)}")
```

Whether to drop or keep incomplete records is a design decision — for this course, either approach is fine. Just be consistent.

## Loading into weather_raw

With records prepared, upsert them into `weather_raw`:

```python
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

response = (
    supabase.table("weather_raw")
    .upsert(records, on_conflict="date")
    .execute()
)

print(f"Upserted {len(response.data)} rows into weather_raw")
```

Using `upsert` rather than `insert` means you can run this script as many times as you like — on the first run it inserts all 365 rows; on subsequent runs it updates them in place. The table always ends up in a consistent state.

## Verifying the Load

After inserting, confirm the data looks right before moving on:

```python
# Row count
count_response = supabase.table("weather_raw").select("date", count="exact").execute()
print(f"Rows in weather_raw: {count_response.count}")

# Spot-check: first and last record
first = supabase.table("weather_raw").select("*").eq("date", "2023-01-01").execute()
last  = supabase.table("weather_raw").select("*").eq("date", "2023-12-31").execute()
print("First record:", first.data)
print("Last record: ", last.data)
```

The `count="exact"` parameter tells Supabase to return the total number of matching rows in `response.count` alongside the data. You should see 365 rows.

You can also verify directly in the Supabase dashboard: open the Table Editor and click `weather_raw`. You should see all 365 rows with dates from January 1 to December 31, 2023.

## The Complete Extract + Load Script

Here is the full pipeline as a single script:

```python
import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

LATITUDE  = 35.23
LONGITUDE = -80.84

# --- Extract ---
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude":   LATITUDE,
    "longitude":  LONGITUDE,
    "start_date": "2023-01-01",
    "end_date":   "2023-12-31",
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "wind_speed_10m_max",
    ],
    "timezone": "America/New_York",
}

response = requests.get(url, params=params)
response.raise_for_status()
daily = response.json()["daily"]
print(f"Fetched {len(daily['time'])} daily records from Open-Meteo")

# --- Transform ---
records = [
    {
        "date":               daily["time"][i],
        "temperature_2m_max": daily["temperature_2m_max"][i],
        "temperature_2m_min": daily["temperature_2m_min"][i],
        "precipitation_sum":  daily["precipitation_sum"][i],
        "wind_speed_10m_max": daily["wind_speed_10m_max"][i],
    }
    for i in range(len(daily["time"]))
]

# --- Load ---
db_response = (
    supabase.table("weather_raw")
    .upsert(records, on_conflict="date")
    .execute()
)
print(f"Upserted {len(db_response.data)} rows into weather_raw")

# --- Verify ---
count_response = supabase.table("weather_raw").select("date", count="exact").execute()
print(f"Total rows in weather_raw: {count_response.count}")
```

Notice the comment labels: `Extract`, `Transform`, and `Load`. The transform step here is minimal — just reshaping the API response into row dictionaries — but the structure is already in place. In Weeks 10 and 11, the transform step grows substantially: it will run the ML classifier on each row and then enrich the output with an LLM.

## Check for Understanding

1. The Open-Meteo API returns data in columnar format (a dictionary of parallel lists). Why do you need to convert it to row format before upserting?

    - A. Supabase only accepts data as CSV, not JSON
    - B. The `supabase-py` insert and upsert methods expect a list of row dictionaries, one per record
    - C. Columnar data would exceed the Supabase row size limit
    - D. The conversion is optional — Supabase can accept either format

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. <code>supabase-py</code>'s insert and upsert methods accept a single dictionary (one row) or a list of dictionaries (multiple rows). Each dictionary maps column names to values for one record.
    </details>

2. You run the Extract + Load script twice in the same day. What happens to `weather_raw` on the second run?

    - A. The second run fails with a primary key conflict error
    - B. All 365 rows are duplicated, resulting in 730 rows
    - C. The existing rows are updated in place; the row count stays at 365
    - D. The table is emptied and re-loaded from scratch

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: C. <code>upsert</code> with <code>on_conflict="date"</code> updates existing rows rather than inserting duplicates. Re-running the script is safe — the table always ends up with exactly one row per date.
    </details>

3. You forget to call `response.raise_for_status()` after the API request. The Open-Meteo server returns a 429 (Too Many Requests) error. What happens next?

    - A. The script raises an exception immediately and stops
    - B. The script continues and tries to upsert the error response, which will likely fail with a confusing database error
    - C. `requests` automatically retries the request up to three times
    - D. The response body is empty, so the script inserts zero rows

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. Without <code>raise_for_status()</code>, a failed HTTP response is treated as a normal response. The script will try to parse the error body as weather data, fail with a <code>KeyError</code> or similar, and produce a confusing traceback unrelated to the actual problem. Always call <code>raise_for_status()</code> immediately after an API request.
    </details>

## Lesson Wrap-Up

The Extract + Load pattern is straightforward: fetch data from an API, reshape it into row dictionaries, and upsert it into the database. Using `upsert` with `on_conflict` makes the load step idempotent — re-running produces the same result as running once. The 365 rows now sitting in `weather_raw` are the starting point for everything that follows.

In Week 10, you will read those rows back out, pass them through the weather classifier you trained in Week 3 and packaged in Week 4, enrich the results with an LLM, and write the output to `weather_enriched`. The pipeline is taking shape.
