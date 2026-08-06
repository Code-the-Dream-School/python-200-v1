# Assignment 10 Answer Key: Cloud ML (Double-Transform Pipeline)

**Mentor note:** Week 10 builds the Transform step — the Week 4 ML classifier predicts good/skip for each `weather_raw` row, then an LLM adds a one-sentence recommendation, and both land in `weather_enriched`. Warmups mix conceptual comment-answers with code; the project is the double-transform end-to-end. Grade approach, correct incremental processing, and graceful LLM error handling. LLM summary text varies. The **video is not assessed**. Two themes to verify: **ML vs. LLM role separation** and **incremental processing** (don't re-process already-enriched rows).

---

## Expected File Setup

Assignment lives in `assignments_10/`:

```
assignments_10/
├── warmup_10.py       # conceptual answers (comments) + code
├── transform_10.py    # double-transform pipeline (video link in top comment)
└── models/            # weather_classifier.pkl + metadata.json copied from Week 4
```

Requires `supabase python-dotenv joblib scikit-learn pandas openai`. Week 9 must have populated `weather_raw`; Week 4 model files must be in `models/`.

---

# Part 1: Warmup (`warmup_10.py`)

## ML vs. LLM in Pipelines

### ML/LLM Q1 — **Subjective**
Core distinction:
- The **ML classifier** produces a **structured, deterministic** output — a binary good/skip label + probability — from numeric features. Fast, cheap, consistent.
- The **LLM** produces **fluent natural-language** text (the recommendation). Good at phrasing, bad as a precise numeric classifier.
- Swapping them fails: an LLM making the binary call is slower, costlier, and non-deterministic (may vary run to run); an ML regression/classifier can't write a readable sentence. Right tool for right job.

### ML/LLM Q2 — **Objective** (tool-choice per task)
- Date string → day-of-week → **deterministic code** (`datetime`), no ML/LLM needed.
- Job posting → entry/mid/senior from freeform text → **LLM** (unstructured language understanding; no labeled training set implied).
- Customer churn from 15 numeric features + labeled data → **trained ML model** (classic supervised classification).
- Normalizing messy city names to canonical form → **LLM** (fuzzy, many variants) — accept deterministic code/lookup if the variants are bounded; reasoning matters.
- Summing a revenue column → **deterministic code** (never an LLM for arithmetic).

### ML/LLM Q3 — **Subjective**
Incremental processing = only process **new/unprocessed** records, not the whole table each run. Important because re-processing all 365 rows every run **wastes money** (repeat LLM API calls), **wastes time**, and risks overwriting/duplicating. The incremental check (skip dates already in `weather_enriched`) keeps runs cheap and idempotent.

## Prompt Design

### Prompt Q1 — **Objective (approach) + Subjective**
An alternative two-sentence system prompt (sentence 1 = prediction, sentence 2 = reasoning). Comment on validation change: the one-sentence check would need to **allow/expect two sentences** — e.g. adjust any sentence-count or length validation, or split on the two parts. Look for awareness that output-format changes require validation changes.

### Prompt Q2 — **Objective (approach)**
`call_with_retry(client, messages, max_retries=3)` calls `chat.completions.create()`, retries on **any exception** up to `max_retries` with a **2-second wait** between attempts, returns `None` on final failure:
```python
def call_with_retry(client, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return None
```
Comment: used in production to survive **transient API failures** (rate limits, timeouts, network blips) without crashing the whole pipeline.

---

# Part 2: Project — Double-Transform Pipeline (`transform_10.py`)

**Overall check:** reads unprocessed `weather_raw` rows, runs the ML model, adds an LLM sentence, upserts to `weather_enriched`. Must be incremental and must not crash on an LLM error.

### Step 1: Incremental Read — **Objective (approach)**
Loads metadata JSON; fetches all `weather_raw` rows and all dates already in `weather_enriched`; computes the difference (unprocessed dates). Prints a summary: raw count, already-enriched count, to-be-processed count. On a fresh run all 365 process; on a second run, 0.

### Step 2: ML Transform — **Objective (approach)**
Loads `weather_classifier.pkl`; builds a DataFrame selecting feature columns **in the metadata's order** (order matters — the pipeline expects it); runs `predict` and `predict_proba`. Builds records with `date`, `good_for_running`, `confidence`. Prints how many good days + confidence range. Common bug: feature columns in the wrong order → silently wrong predictions.

### Step 3: LLM Transform — **Objective (approach) + Subjective**
A system prompt + user-message function passing each day's features + the ML prediction to `gpt-4o-mini`; adds a one-sentence `llm_summary`. **Handles API errors with a fallback string** (not a crash). Progress print every 50 records. The prompt should feed the model the ML prediction so the sentence stays consistent with it.

### Step 4: Load — **Objective (approach)**
Upserts enrichment records into `weather_enriched`, prints the upserted count.

### Step 5: Verify — **Objective (approach) + Subjective**
Queries `weather_enriched`: total rows, five sample rows (`date`, `good_for_running`, `confidence`, `llm_summary`), count of good-for-running days. Comment evaluates a few summaries — a good one accurately reflects the features + prediction; a weak one might contradict the data or be generic. Look for genuine inspection.

### Step 6: Reflect — **Subjective**
5–6+ sentences on:
1. Model trained on Charlotte, NC — predictions on a different city may be **less accurate** if that city's climate differs (thresholds baked into training reflect Charlotte). Good answer engages with distribution shift.
2. The LLM is **purely additive** — it describes the prediction but can't override the classifier's good/skip decision. Implication: the ML model is the source of truth; a bad prediction produces a confident-but-wrong sentence.
3. Scaling to 50,000 records → main concern is usually **cost and latency of the per-row LLM calls** (365 → 50k is 137× the API spend/time). Fixes: batching, caching, cheaper/local model, parallelism, or only enriching a subset.

### Video — **Not assessed**
Linked in top comment. Not graded for code.
