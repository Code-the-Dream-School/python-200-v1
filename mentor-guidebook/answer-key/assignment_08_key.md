# Assignment 8 Answer Key: Cloud Intro

**Mentor note:** Week 8 is conceptual — there is **no Python code** this week. Deliverables are two Markdown files (warmup answers + project write-up), a Supabase project setup, an AWS cost analysis, and a short video. Per course policy the **video is not assessed here** — focus on the written answers and that the Supabase tables were actually created. Many warmup questions are conceptual with clear intended answers (given below); a few are open reflection. Where the answer depends on the specific lesson text (e.g. "the two situations where cloud isn't right"), I've given the standard answer but flag that you should check it against the student's own lesson.

---

## Expected File Setup

Assignment lives in `assignments_08/`:

```
assignments_08/
├── warmup_08.md     # cloud concepts + landscape written answers
└── project_08.md    # Supabase setup confirmation + AWS cost write-up + video link
```

Submitted as a PR. No `.py` files this week.

---

# Part 1: Warmup — Cloud Concepts (`warmup_08.md`)

### Cloud Concepts Q1 — **Subjective**
Core economic model = **pay-as-you-go / rent vs. own** (operating expense vs. capital expense).
- Good answer: cloud converts large upfront hardware purchases (capex) into on-demand rental (opex); you pay only for what you use and can scale up/down without buying servers.
- Weak answer: "it's cheaper" with no mention of the capex→opex shift or elasticity.

### Cloud Concepts Q2 — **Objective** (scaling classifications)
Definitions: **vertical** = a bigger machine (more CPU/RAM/GPU on one node); **horizontal** = more machines working in parallel.
The three scenarios:
- Viral launch 1k→100k users → **horizontal** (spread load across many servers).
- Faster GPU + more RAM for training → **vertical** (one more powerful machine).
- 10→10,000 files, splittable across machines → **horizontal** (parallelize the work).

### Cloud Concepts Q3 — **Objective** (service model classifications)
Most likely intended classifications:
- Gmail → **SaaS** (finished application)
- Azure Virtual Machines → **IaaS** (raw compute you manage)
- AWS S3 → **IaaS** (storage infrastructure)
- GitHub Codespaces → **PaaS** (managed dev environment/platform)
- Snowflake → **SaaS** (managed data platform; accept PaaS-leaning reasoning)
- Supabase → **BaaS** (backend-as-a-service)
Then IaaS/PaaS/SaaS described in own words with an example and who-manages-what: the key gradient is how much the developer manages — **IaaS** (you manage OS/runtime/app, provider manages hardware), **PaaS** (you manage just your app/code, provider manages the platform), **SaaS** (you manage nothing but your data/usage). Snowflake and S3 are the two most likely to spark debate — accept well-reasoned alternatives.

### Cloud Concepts Q4 — **Subjective**
Managed data platform (Databricks/Snowflake) = a fully-managed analytics/data system built *on top of* raw cloud.
- Gain: less setup/ops, built-in scaling, integrated tooling, faster time-to-value.
- Give up: some control, flexibility, and cost (markup over raw infra), plus potential vendor lock-in.

### Cloud Concepts Q5 — **Subjective** (check against lesson)
The lesson names a situation where cloud isn't the right choice.
- From the lesson: If your dataset fits comfortably on a single machine and you do not have massive compute demands, local processing is often faster and cheaper. This is often the best approach when setting up an initial prototype.

---

# Part 2: Warmup — Cloud Landscape (`warmup_08.md`)

### Cloud Landscape Q1 — **Objective + Subjective**
The three hyperscalers: **AWS, Microsoft Azure, Google Cloud (GCP)**. One-sentence strength each (reasonable answers):
- AWS — broadest/most mature service catalog; startups to large enterprises.
- Azure — deep Microsoft/enterprise integration; orgs already on Microsoft stack.
- GCP — strength in data/analytics/ML and Kubernetes; data-heavy and ML-focused orgs.

### Cloud Landscape Q2 — **Subjective** (check against lesson)
Three reasons the course switched Azure→Supabase (summarize each). Typical: Supabase is **simpler/faster to onboard**, **free tier with no credit card**, and **more approachable for beginners** (less enterprise complexity). Reflection should land on: match the tool to the project's scale and the team's skill — don't default to the biggest/most complex provider.

### Cloud Landscape Q3 — **Objective** (category + provider)
1. Store 10 TB images, retrieve by filename → **object storage** → AWS S3 (or GCS / Azure Blob).
2. GPU job for 4 hours then shut down → **compute / IaaS VM (GPU)** → AWS EC2 (e.g. p3), GCP Compute Engine.
3. Auto-scaling web API → **serverless compute** → AWS Lambda, Google Cloud Run.
4. Structured data → LLM → text back → **LLM API** → OpenAI API (or Anthropic).

### Cloud Landscape Q4 — **Subjective**
A student-designed project with a multi-provider stack (e.g. S3 for storage + OpenAI for LLM + Supabase for DB). Reflection: consolidating to one provider gains **simpler billing/integration/security**, but gives up **best-of-breed tools** and increases **lock-in**. Any coherent stack drawing from ≥2 providers is fine.

---

# Part 3: Project (`project_08.md`)

### Part A: Supabase Setup — **Objective (pass/fail)**
- A sentence confirming the `python200` project is set up.
- The real check: both `weather_raw` and `weather_enriched` tables exist with the correct columns, and RLS is disabled. The video should show them in the Table Editor. If the student notes issues, see whether they resolved them.
- Security note: `.env` (with the anon key) should be gitignored — the anon key is public-ish but good hygiene still applies; the DB password must never be committed.

### Part B: Cloud Cost Analysis — **Subjective (ballpark anchors)**
AWS prices change over time, so grade the *reasoning*, not exact dollars. Rough US-East on-demand anchors for sanity:
- **Scenario A** (t3.micro, ~160 hrs/mo): only a **few dollars/month** (~$2–8 incl. minimal storage).
- **Scenario B** (p3.2xlarge 24/7 + db.m5.large + 1 TB S3): roughly **$2,300–2,500/month**, and the GPU instance alone is ~$2,200 of it (the RDS ~$125, S3 ~$23).
Good write-up notes: Scenario B is ~1000× Scenario A; the **GPU dominates** the cost; a GPU running 24/7 is only worth it if heavily utilized — otherwise run it only for the hours needed (or use spot). Any estimates in the right order of magnitude with sound reasoning pass.

### The Video — **Not assessed** (per course policy)
Should exist and be linked in `project_08.md`, showing the Supabase dashboard and AWS estimates. Not graded for code.
