# LLM Enrichment and Writing to weather_enriched

The ML step produced a binary label and a confidence score for each day. That is useful data, but it is not something you could hand to a user directly — a boolean and a probability don't tell a runner what to expect or why. This is where the LLM step earns its place: it takes the weather features and the model's prediction and produces a short, human-readable recommendation.

By the end of this lesson you will have a complete double-transform script that reads from `weather_raw`, runs the ML classifier, enriches each record with an LLM recommendation, and writes the results to `weather_enriched`.

## Learning Objectives

By the end of this lesson, you will be able to:

- Design a constrained prompt that accepts structured inputs and returns a parseable sentence
- Iterate over enrichment records, call the OpenAI API, and handle unexpected responses gracefully
- Insert complete enrichment records (ML predictions + LLM summaries) into `weather_enriched`
- Spot-check the loaded data with a Supabase query

## Designing the Prompt

The LLM receives two kinds of information: the raw weather features for the day, and the ML model's prediction. The goal is a single sentence that a runner could act on — direct, practical, no padding.

```python
SYSTEM_PROMPT = (
    "You are writing a one-sentence running recommendation for a daily weather summary app. "
    "You will receive weather conditions for a single day and a machine learning prediction "
    "about whether the day is good for running. "
    "Write exactly one sentence — direct, practical, and specific to the conditions. "
    "Do not use bullet points, headers, or phrases like 'Based on the data'."
)

def make_user_message(row, good_for_running, confidence):
    prediction_text = "good for running" if good_for_running else "not ideal for running"
    return (
        f"Date: {row['date']}\n"
        f"High: {row['temperature_2m_max']}°C, Low: {row['temperature_2m_min']}°C\n"
        f"Precipitation: {row['precipitation_sum']} mm\n"
        f"Max wind speed: {row['wind_speed_10m_max']} km/h\n"
        f"Model prediction: {prediction_text} (confidence: {confidence:.0%})"
    )
```

Passing the model's confidence to the LLM is intentional: a low-confidence prediction is worth flagging in the recommendation ("borderline conditions — the model is uncertain"). A high-confidence positive is worth expressing more clearly.

## Calling the OpenAI API

With enrichment records from the ML step in hand, iterate over them and call the API:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# raw_rows is the original list of dicts from weather_raw
# enrichment_records is the list from the ML step, indexed in the same order

for i, record in enumerate(enrichment_records):
    raw_row = next(r for r in to_classify if r["date"] == record["date"])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": make_user_message(
                    raw_row,
                    record["good_for_running"],
                    record["confidence"],
                ),
            },
        ],
        max_tokens=100,
    )

    summary = response.choices[0].message.content.strip()
    record["llm_summary"] = summary

    if (i + 1) % 50 == 0:
        print(f"  Enriched {i + 1} / {len(enrichment_records)} records...")
```

`max_tokens=100` caps the response length. One sentence should never need more than 50 tokens, but a generous cap prevents runaway completions without cutting off legitimate output.

## Handling Unexpected Responses

Even with a tight prompt, models occasionally return output that is empty, unusually long, or multi-sentence. Validate before accepting:

```python
def validate_summary(text):
    text = text.strip()
    if not text:
        return None
    # Reject if more than two sentences (simple heuristic)
    sentences = [s for s in text.split(".") if s.strip()]
    if len(sentences) > 2:
        return None
    return text

for i, record in enumerate(enrichment_records):
    raw_row = next(r for r in to_classify if r["date"] == record["date"])

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": make_user_message(
                    raw_row, record["good_for_running"], record["confidence"]
                )},
            ],
            max_tokens=100,
        )
        raw_summary = response.choices[0].message.content
        summary = validate_summary(raw_summary) or "Recommendation unavailable."
    except Exception as e:
        print(f"  API error on {record['date']}: {e}")
        summary = "Recommendation unavailable."

    record["llm_summary"] = summary
```

The `try/except` catches network errors and API failures. Recording `"Recommendation unavailable."` rather than crashing means the pipeline can finish and you can investigate failed records afterward. Robustness matters more than perfection in automated pipelines.

## Writing to weather_enriched

Once all records have an `llm_summary`, upsert them into `weather_enriched`:

```python
response = (
    supabase.table("weather_enriched")
    .upsert(enrichment_records, on_conflict="date")
    .execute()
)
print(f"Upserted {len(response.data)} rows into weather_enriched")
```

The `weather_enriched` schema accepts `None` for `llm_summary` (it is a nullable `text` column), so records where enrichment failed will still insert correctly.

## Spot-Checking the Output

Query `weather_enriched` to confirm the results look right:

```python
check = supabase.table("weather_enriched").select("*").limit(5).execute()
for row in check.data:
    print(f"{row['date']} | good={row['good_for_running']} | conf={row['confidence']:.2f}")
    print(f"  {row['llm_summary']}")
    print()

# Count how many were classified as good
good_count = (
    supabase.table("weather_enriched")
    .select("date", count="exact")
    .eq("good_for_running", True)
    .execute()
)
print(f"Good-for-running days in weather_enriched: {good_count.count}")
```

You can also inspect the table directly in the Supabase dashboard. At this point, `weather_enriched` should have one row per day in `weather_raw`, each with a binary label, a confidence score, and a one-sentence LLM recommendation.

## The Complete Double-Transform Script

Here is the full workflow from reading `weather_raw` to writing `weather_enriched`:

```python
import os
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI
from weather_model import WeatherClassifier

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Load the Week 4 component
classifier = WeatherClassifier("models/weather_classifier.pkl")

SYSTEM_PROMPT = (
    "You are writing a one-sentence running recommendation for a daily weather summary app. "
    "You will receive weather conditions for a single day and a machine learning prediction "
    "about whether the day is good for running. "
    "Write exactly one sentence — direct, practical, and specific to the conditions. "
    "Do not use bullet points, headers, or phrases like 'Based on the data'."
)

def make_user_message(row, good_for_running, confidence):
    prediction_text = "good for running" if good_for_running else "not ideal for running"
    return (
        f"Date: {row['date']}\n"
        f"High: {row['temperature_2m_max']}°C, Low: {row['temperature_2m_min']}°C\n"
        f"Precipitation: {row['precipitation_sum']} mm\n"
        f"Max wind speed: {row['wind_speed_10m_max']} km/h\n"
        f"Model prediction: {prediction_text} (confidence: {confidence:.0%})"
    )

# --- Read ---
raw_rows = supabase.table("weather_raw").select("*").execute().data
already_done = {r["date"] for r in supabase.table("weather_enriched").select("date").execute().data}
to_classify = [r for r in raw_rows if r["date"] not in already_done]
print(f"Records to process: {len(to_classify)}")

if not to_classify:
    print("Nothing to do — all records already enriched.")
    exit()

# --- ML Transform ---
predictions = classifier.predict(to_classify)

enrichment_records = [
    {
        "date":             row["date"],
        "good_for_running": pred.label == "good",
        "confidence":       round(pred.probability, 4),
        "llm_summary":      None,
    }
    for row, pred in zip(to_classify, predictions)
]

# --- LLM Transform ---
for i, record in enumerate(enrichment_records):
    raw_row = to_classify[i]
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": make_user_message(
                    raw_row, record["good_for_running"], record["confidence"]
                )},
            ],
            max_tokens=100,
        )
        summary = response.choices[0].message.content.strip()
        record["llm_summary"] = summary or "Recommendation unavailable."
    except Exception as e:
        print(f"  API error on {record['date']}: {e}")
        record["llm_summary"] = "Recommendation unavailable."

    if (i + 1) % 50 == 0:
        print(f"  Processed {i + 1} / {len(enrichment_records)}")

# --- Load ---
db_response = (
    supabase.table("weather_enriched")
    .upsert(enrichment_records, on_conflict="date")
    .execute()
)
print(f"Upserted {len(db_response.data)} rows into weather_enriched")

# --- Spot-check ---
sample = supabase.table("weather_enriched").select("*").limit(3).execute()
for row in sample.data:
    print(f"\n{row['date']} | good={row['good_for_running']} | conf={row['confidence']:.2f}")
    print(f"  {row['llm_summary']}")
```

## Check for Understanding

1. The `make_user_message` function includes the ML model's confidence in the LLM prompt. Why?

    - A. The LLM uses the confidence to recalculate the classification
    - B. A low confidence score is meaningful context: it signals borderline conditions that the recommendation should acknowledge
    - C. The confidence score is required by the OpenAI API
    - D. It prevents the LLM from overriding the ML prediction

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. The LLM cannot change the ML prediction — that is already computed. But the confidence level is useful context for generating a recommendation. A day with 0.51 confidence deserves a different recommendation than one with 0.95 confidence, even if both are classified as "good."
    </details>

2. The pipeline catches API exceptions and inserts `"Recommendation unavailable."` instead of crashing. What is the tradeoff of this approach?

    - A. There is no tradeoff — this is always the right pattern
    - B. The pipeline is more robust and completes even with partial failures, but failed records need to be reviewed and re-processed separately
    - C. Using a fallback string causes `weather_enriched` to reject the insert because `llm_summary` is a non-nullable column
    - D. The fallback prevents the incremental processing check from working correctly on the next run

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. Robustness and completeness come at the cost of needing to identify and re-process failed records. In practice, engineers monitor for <code>"Recommendation unavailable."</code> values and re-run failed batches. The incremental check still works correctly because the date is written to <code>weather_enriched</code> regardless of whether the LLM succeeded.
    </details>

3. After running the complete double-transform script, you query `weather_enriched` and find 290 rows, but `weather_raw` has 365. What is the most likely explanation?

    - A. The upsert failed silently for 75 rows
    - B. 75 rows were already in `weather_enriched` before this run; the incremental check skipped them and they were not re-inserted
    - C. The LLM returned `"Recommendation unavailable."` for 75 rows, which were not inserted
    - D. The foreign key constraint rejected 75 rows because those dates do not exist in `weather_raw`

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. If <code>weather_enriched</code> already contained 75 rows before this run, the incremental check would exclude them from <code>to_classify</code> and they would not be re-upserted. The total remains at 290 (75 existing + 290 new). If you want to re-process those 75, delete them from <code>weather_enriched</code> and re-run.
    </details>

## Lesson Wrap-Up

The double-transform is now complete. `weather_raw` holds the original API data, unchanged. `weather_enriched` holds one row per day with three fields added by the pipeline: a binary ML prediction, a confidence score, and a one-sentence LLM recommendation. The two tables together capture both the raw source and the fully enriched output, independently queryable and clearly separated.

In the next lesson, you will wrap this double-transform script into a Prefect *flow* — your first look at the orchestration tool that runs and monitors pipelines. Then in Week 11, you will combine it with the Week 9 Extract + Load into a single production pipeline with retries, structured logging, and idempotent writes.
