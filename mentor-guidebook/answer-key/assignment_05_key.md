# Assignment 5 Answer Key: AI Intro (LLMs & Prompt Engineering)

**Mentor note:** This key covers Week 5 warmups (Chat Completions API, system messages, prompt engineering, Ollama) and the Job Application Helper chatbot mini-project. **Reproducibility caveat:** almost everything here calls a live LLM, so exact text output will differ for every student and every run. Grade the *technique and code pattern*, not the model's wording. The one fully deterministic answer is the chain-of-thought math (Prompt Q4) — that final number should be correct. The assignment's own reviewer rubric (the hidden block at the bottom of the lesson) lists deliverables by section (API Question 1–4, System Question 1–2, Prompt Question 1–6, Ollama Question 1) and does not assign point values. The point weightings shown below are a suggested guide for mentors, not part of the assignment.

---

## Expected File Setup

Assignment lives in `assignments_05/`:

```
assignments_05/
├── warmup_05.py     # all warmup exercises
├── project_05.py    # mini-project chatbot
└── .env             # OPENAI_API_KEY — must NOT be committed
```

**Check first:** `.env` should be gitignored, not in the PR. If you see an API key in the committed files, flag it — the student needs to rotate the key. Uses `load_dotenv()` before any API call.

---

# Part 1: Warmup Exercises (`warmup_05.py`)

## The Chat Completions API

### API Q1 — **Objective (approach)**
Correct access patterns are the point:
- Response text: `response.choices[0].message.content`
- Model name: `response.model`
- Token count: `response.usage.total_tokens`
Each printed with a label. Common errors: printing the whole response object, or using `.text` / `.content` directly on the response.

### API Q2 — **Objective (approach) + Subjective**
Same prompt at temperature 0, 0.7, 1.5, each labeled. Comment should observe: higher temperature = more varied/creative (and at 1.5, sometimes odd) output; lower = more focused/repetitive. For reproducibility, **temperature 0** is the right choice.

### API Q3 — **Objective (approach)**
`n=3`, `temperature=1.0`, iterates `response.choices` and prints all three (`choice.message.content`). Should yield three different fun facts from one call.

### API Q4 — **Objective (approach) + Subjective**
`max_tokens=15` cuts the response off mid-thought. Comment should note the output is truncated, and that `max_tokens` controls cost/latency and prevents runaway-length responses in production.

## System Messages and Personas

### System Q1 — **Objective (approach) + Subjective**
Two different `system` messages, same user question, both responses printed. Comment notes the tone/personality shifted with the system message. Any two distinct personas are fine.

### System Q2 — **Objective (approach) + Subjective**
Sends the pre-built 4-message conversation; model correctly answers "Jordan." Comment must explain statelessness correctly: the API has **no memory** — the model "knows" the name only because the prior turns are re-sent in the `messages` list each call.

## Prompt Engineering

### Prompt Q1 — Zero-Shot — **Objective (approach) + Subjective**
Classifies the 3 reviews with no examples. Expected sensible labels: (1) positive, (2) negative, (3) mixed. Minor wording/format variation is fine with no examples given.

### Prompt Q2 — One-Shot — **Objective (approach) + Subjective**
Same task with one `mixed` example. Comment should note the single example nudged the **format** toward a consistent one-word label (e.g. just "mixed" instead of a sentence).

### Prompt Q3 — Few-Shot — **Objective (approach) + Subjective**
Three examples (≥1 each of positive/negative/mixed). Comment compares all three approaches: zero-shot for simple/obvious tasks, one/few-shot when you need a specific format or the task is ambiguous. More examples = more consistency but more tokens.

### Prompt Q4 — Chain of Thought — **Objective (the math) + Subjective**
This one has a correct number. $85,000 × 1.12 = **$95,200** (post-raise); + $7,500 = **$102,700** final salary. The response should show step-by-step reasoning and land on **$102,700**. (The "6 months later" is a distractor — it does not change the annual salary.) Comment should explain that step-by-step reasoning improves accuracy by breaking the problem into smaller, checkable steps instead of jumping to an answer.

### Prompt Q5 — Structured Output — **Objective (approach) + Subjective**
Prompt asks for JSON only with keys `sentiment`, `confidence` (float), `reason`. Prints raw response, then `json.loads()` and prints each field. Must have a `try/except` that prints the raw response on parse failure. For the sample review, expect sentiment "mixed" with a moderate-to-high confidence.

### Prompt Q6 — Delimiters — **Objective (approach) + Subjective**
Uses triple backticks around `user_text`. First prompt (pasta steps) → a numbered list. Second prompt (non-instructional prose) → exactly `"No steps provided."`. Comment should explain delimiters prevent **prompt injection / instruction confusion** — they keep the model from treating user-supplied text as new instructions.

## Local Models with Ollama

### Ollama Q1 — **Objective (approach) + Subjective**
Ollama CLI output pasted as a comment; the equivalent OpenAI call made and printed. Comment compares the two and gives one advantage (privacy, no API cost, offline, no rate limits) and one disadvantage (smaller/weaker model, slower on modest hardware, lower quality) of running locally. Any reasonable pair is fine.

---

# Part 2: Mini-Project — Job Application Helper (`project_05.py`)

**Overall check:** a working chatbot that accumulates conversation history, routes to a bullet-rewriter and cover-letter generator, runs a moderation check before each turn, and exits cleanly. Because it is LLM-driven, grade the structure and prompt-engineering technique. The point values shown are a suggested weighting for mentors.

### Task 1: Setup and System Prompt — **Objective (approach) + Subjective** (10 pts)
- `get_completion()` helper as given; client initialized after `load_dotenv()`.
- System prompt is **specific**: role (job application coach), audience (career changers), and the three required constraints (stay on-topic, remind user to review/edit output, acknowledge it may not know industry norms).
- A comment explains at least one deliberate design choice.
- Weak answer: a vague one-liner system prompt that could apply to any assistant.

### Task 2: Bullet Point Rewriter — **Objective (approach) + Subjective** (15 pts)
- `rewrite_bullets()` uses **delimiters** around the bullets, requests a **JSON list** with `original`/`improved` keys, parses it, and prints both versions side by side.
- Should handle the "model added a preamble" failure (e.g. instruction to return only JSON, or a try/except).
- Comment identifies why the starter bullets are weak (vague, no metrics, passive) and what the model improved (strong action verbs, specifics). Improvements should be meaningful, not just reworded.

### Task 3: Cover Letter Generator — **Objective (approach) + Subjective** (10 pts)
- `generate_cover_letter()` uses **few-shot prompting** with ≥2 example openings before the real request.
- Output should be tailored to the input (the teacher→data-engineer example) and not invent credentials.
- Comment explains the example choices and that few-shot controls **tone/style/format**.
- Red flag: generic "I am excited to bring my unique skills" output that doesn't adapt to input.

### Task 4: Moderation Check — **Objective (approach)** (5 pts)
- `is_safe()` calls `client.moderations.create(model="omni-moderation-latest", ...)`, returns `True`/`False` from `result.results[0].flagged`, prints a respectful message when flagged.
- Tested with one passing and one flagged input, both printed.

### Task 5: The Chatbot Loop — **Objective (approach) + Subjective** (15 pts)
Fills in the five marked sections correctly:
- Bullet branch: collects lines until "DONE", calls `rewrite_bullets()`.
- Cover-letter branch: collects job title + background, calls `generate_cover_letter()`.
- Regular-chat branch: **appends user message → calls `get_completion(messages)` → prints → appends assistant reply**. This last append is the most common miss — without it, the bot loses memory across turns.
- Moderation runs before processing; empty input skipped; `quit`/`exit` breaks cleanly.
- Verify: history accumulates (the name-recall test in the lesson's checklist confirms it).

### Task 6: Ethics Reflection — **Subjective** (10 pts)
Comment block (or video link) addressing ≥2 of the 3 questions. Good answers show genuine engagement:
- **Bias:** training data over-represents certain writing styles/industries/backgrounds; the tool may favor conventional, Western, formal business English and disadvantage other voices.
- **Submitting unreviewed output:** hallucinated or exaggerated credentials, generic tone, factual errors — could cost the applicant credibility or the job.
- **Guardrail:** any concrete design choice (disclaimer, mandatory review step, moderation filter, "don't invent facts" instruction, usage policy).
- Weak answer: surface-level ("AI can be biased") with no specifics.

### Code Quality (5 pts)
Outputs labeled, sections comment-marked, runs without errors.

### Optional Extensions — **Not required**
Token tracker, Ollama swap, resume file upload, confidence field, top-p experiment. Grade lightly if attempted.
