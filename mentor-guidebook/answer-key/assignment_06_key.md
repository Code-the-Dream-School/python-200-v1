# Assignment 6 Answer Key: AI Augmentation (RAG)

**Mentor note:** This key covers Week 6 warmups (RAG concepts, keyword RAG, semantic RAG concepts, LlamaIndex) and the Groundwork Coffee Q&A mini-project. **Reproducibility caveat:** the LlamaIndex sections call live embedding/LLM APIs, so answer text and exact similarity scores vary — grade approach and reasoning. However, several pieces are fully deterministic and given exactly below: the keyword-RAG traces (the function is fixed), the pipeline-ordering question, and the concept-matching scenarios. The keyword-RAG questions have a deliberate "gotcha" (Q3) worth knowing before you review.

---

## Expected File Setup

Assignment lives in `assignments_06/`:

```
assignments_06/
├── warmup_06.py     # all warmup exercises
├── project_06.py    # mini-project
└── .env             # OPENAI_API_KEY — not committed
```

Requires `pip install openai pypdf python-dotenv "llama-index-core==0.14.10" llama-index-embeddings-openai`. Note the version pin on `llama-index-core`. Paths to the PDF/doc folders are relative and may need adjusting per student setup — don't penalize a reasonable path difference.

---

# Part 1: Warmup Exercises (`warmup_06.py`)

## RAG Concepts

### Concepts Q1 — **Objective** (clear best answer per scenario)
- **Scenario A** (hundreds of PDFs, updated quarterly): **RAG** — large, frequently-changing knowledge base; you want retrieval from current docs, not retraining.
- **Scenario B** (specific brand voice, 3,000 examples): **Fine-tuning** — teaching a consistent *style/behavior* with many examples is what fine-tuning is for.
- **Scenario C** (single 2-page report, one-off): **Prompt engineering** — just paste the report into the context window; no infrastructure needed.
- Wrong answers usually swap A and B (using fine-tuning for a changing document set, or RAG to teach style).

### Concepts Q2 — **Subjective**
- Correct: a *confident* wrong answer is more harmful because users are more likely to trust and act on it without verifying; an "I'm not sure" signals the need to check.
- Should give a concrete harm example (medical, legal, financial advice acted on directly).
- Should connect **tone** to trust — fluent, authoritative phrasing makes errors harder to catch.

### Concepts Q3 — **Objective** (exact order)
Correct ordering:
1. Extract text from source documents
2. Split text into chunks
3. Convert text chunks into embeddings
4. Receive the user's query
5. Embed the user's query
6. Retrieve the most relevant chunks
7. Inject retrieved chunks into the prompt
8. Generate a response from the LLM
Key logic: steps 1–3 are the **indexing/offline** phase (done once, ahead of time); 4–8 are the **query/runtime** phase. A common error is putting "receive the query" first or embedding the query before the documents.

## Keyword RAG (deterministic — function is fixed)

### Keyword Q1 — **Objective**
Query "What are your hours on weekends?" → filtered tokens `{hours, weekends, what, your}` (`are` is a stopword). Only **hours.txt** contains "weekends" (overlap = 1). **Selected: hours.txt.** Correct — this is the ideal case where the keyword literally appears.

### Keyword Q2 — **Objective + Subjective**
Query "Do you have anything without caffeine?" → filtered tokens `{anything, caffeine, do, have, without}` (`you` is a stopword). **No document contains any of these words** → the function prints "No overlapping keywords found" and returns the "None found" placeholder.
- Correct analysis: keyword RAG **fails** here — the menu (decaf-relevant) doesn't contain the literal word "caffeine." A **semantic/embedding** approach would match on meaning and do better.

### Keyword Q3 — **Objective (the gotcha) + Subjective**
Query "How do I sign up for rewards?" → filtered tokens `{how, do, i, sign, up, rewards}` (`for` is a stopword). Most students **predict loyalty.txt** — but loyalty.txt says "Join our loyalty program… Redeem points," never the words "sign," "up," or "rewards." **Overlap is 0 for every document → "No overlapping keywords found."**
- The surprise is the point: keyword matching misses obvious **synonyms** ("rewards"≈"loyalty", "sign up"≈"join"). A correct comment identifies this as the core weakness keyword RAG has and semantic RAG solves.

## Semantic RAG Concepts

### Semantic Q1 — **Subjective**
In the student's own words:
1. An embedding is a vector of numbers capturing the *meaning* of text; similar meanings → similar vectors.
2. The **0.85** chunk is more relevant; higher cosine similarity = closer in meaning.
3. Semantic search matches on meaning, not exact words, so synonyms/paraphrases still score high even with no shared words.
- Weak answer copies lesson definitions verbatim or says the 0.30 chunk is more relevant.

### Semantic Q2 — **Objective** (table fill-in)
Right column, Semantic RAG:
- What is compared? → **Meaning / vector (embedding) similarity**
- What is retrieved? → **The most relevant chunk(s), not the whole document**
- Can it handle synonyms? → **Yes**
- Storage format → **Vector store / embeddings index**
- Relevance score → **Cosine similarity (−1 to 1)**

## LlamaIndex (live API — approach + reasoning)

### LlamaIndex Q1 — **Objective (approach) + Subjective**
Builds an in-memory index over the Brightleaf PDFs, runs both queries with `similarity_top_k=3`. For each: prints question, answer, and for the 3 source nodes the similarity score + first 150 chars. Comments should assess whether retrieved chunks look relevant and note the **tone** (confident/specific vs hedging). Both benefits and security questions should retrieve on-topic chunks.

### LlamaIndex Q2 — **Objective (approach) + Subjective**
Same query at `top_k=1` vs `top_k=5`; prints responses and node scores. Comment: more context is **not always better** — extra chunks can add noise or dilute the answer, and cost more tokens. A good answer notes the response may be similar with 1 well-matched chunk.

### LlamaIndex Q3 — **Subjective**
A deliberately hard query (vague, cross-document, or not in the docs). Comment covers expectation vs actual and a concrete improvement (better chunking, more `top_k`, metadata filtering, a "not found" guard). Key insight to look for: when info is absent, the model may still answer confidently — a hallucination risk.

### LlamaIndex Q4 — **Objective (approach) + Subjective**
Instantiates `FaithfulnessEvaluator` and `RelevancyEvaluator` with `gpt-4o-mini`; runs on the good query and a likely-bad one; prints both scores. Comment block:
- **Faithfulness 1.0** = the answer is fully supported by the retrieved context (no hallucination); **0.0** = not supported / made up.
- **Relevancy** measures whether the answer (and retrieved context) actually addresses the *query* — different from faithfulness, which is about grounding in the source.
- Scores likely drop on the out-of-scope query; a good answer explains why (weak/irrelevant retrieval → unsupported or off-topic answer).
- **LLM-as-a-judge**: using an LLM to score open-ended responses because there's no single exact "correct" string to match — a rigid accuracy metric can't evaluate free-form generated text.

---

# Part 2: Mini-Project — Groundwork Coffee Q&A Assistant (`project_06.py`)

**Overall check:** a working LlamaIndex RAG assistant over the Groundwork docs — loads docs, builds a `VectorStoreIndex`, queries in a loop, and reflects on a failure case. Grade structure and reasoning; answer text varies.

### Step 1: Setup — **Objective (approach)**
Imports at top; API key loaded with a confirmation print; an `assert` that the docs directory exists before use.

### Step 2: Load Documents — **Objective (approach)**
`SimpleDirectoryReader` loads all docs; prints the count and each `metadata["file_name"]`.

### Step 3: Build Index — **Objective (approach)**
`VectorStoreIndex.from_documents(...)`, query engine with `similarity_top_k=3`, confirmation message printed.

### Step 4: Query in a Loop — **Objective (approach) + Subjective**
Runs the 5 questions in a **loop** (not 5 copy-pasted blocks). For each: prints question, answer, and top source node (doc name, score, first 200 chars). All five are answerable from the docs, so answers should be confident and on-topic. Comment reflects on accuracy/surprises.

### Step 5: Find a Failure — **Subjective**
A deliberately hard question (vague, cross-document, or absent info). Prints full response + **all three** source nodes. Comment covers: what was asked and why it's hard; what went wrong (bad retrieval / missing info / model guessed); whether the **tone stayed confident even when wrong** (the key trust lesson); and a proposed fix. This is the most important reflection — look for genuine engagement with the hallucination-confidence problem.

### Step 6: Reflection — **Subjective**
1. LlamaIndex line-count vs manual RAG — should note the framework replaced many lines with a few; value = less boilerplate, fewer bugs.
2. A different real use case (not coffee) — internal HR/policy Q&A, customer support docs, legal/medical knowledge bases, etc.
3. A failure mode RAG can't fully prevent even with good retrieval — e.g. the model misreading/mis-synthesizing correct chunks, or confidently over-generalizing; retrieval quality doesn't guarantee generation quality.

### Optional Extensions (A/B/C) — **Not required**
Keyword-vs-semantic comparison, adding a new document (demonstrates RAG updates without retraining — a good fine-tuning contrast), and the pgvector persistent store (needs Docker). Grade lightly if attempted.
