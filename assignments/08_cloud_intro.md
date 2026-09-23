# Week 8 Assignments

This week's assignments cover the cloud computing concepts from the two Week 8 lessons:

- Core cloud concepts: what cloud computing is, how services are delivered, and when it makes sense
- The cloud provider landscape: hyperscalers, developer platforms, and backend-as-a-service

The warmup is a check for understanding — short written answers, no code. The project introduces the video format used for the rest of the cloud weeks, and gets your Supabase project set up so you're ready to write code in Week 9.

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_08/`. Inside that folder, create two files:

1. `warmup_08.md` — for the warmup questions
2. `project_08.md` — for the Supabase setup notes and cost analysis write-up, plus your video link

When finished, commit and open a PR as described in the [assignments README](README.md).

# Part 1: Warmup — Cloud Concepts

Answer each question in your own words in `warmup_08.md`. A sentence or two is enough for most questions — you are demonstrating that you understood the concept, not writing an essay. Try to do this without AI assistance.

These questions are based on the [Cloud Overview](../lessons/08_cloud_intro/01_cloud_overview.md) lesson.

### Cloud Concepts Question 1

What is the core economic model of cloud computing, and how does it differ from owning your own servers?

### Cloud Concepts Question 2

What is the difference between vertical scaling and horizontal scaling? Give a concrete example of when you might choose each.

Then, for the three scenarios below, write one sentence saying which type of scaling applies and why.

- A web app that normally handles 1,000 users per day suddenly needs to handle 100,000 after a viral product launch.
- A data scientist's model training job is running too slowly, and they want a machine with a faster GPU and more RAM.
- A data pipeline that processes 10 files per run now needs to process 10,000 files per run, and the work can be split across machines.

### Cloud Concepts Question 3

Before writing your definitions, classify each item in the list below as **IaaS**, **PaaS**, **SaaS**, or **BaaS**. One sentence of reasoning is enough for each.

- Gmail
- Azure Virtual Machines
- AWS S3 (Simple Storage Service)
- GitHub Codespaces
- Snowflake
- Supabase

Now describe IaaS, PaaS, and SaaS in your own words. For each, give one example (from the lesson or the list above) and describe what you, as the developer, are responsible for managing.

### Cloud Concepts Question 4

What is a managed data platform like Databricks or Snowflake, and how does it differ from using a cloud provider like AWS or GCP directly? What do you gain, and what do you give up?

### Cloud Concepts Question 5

The lesson describes a situation where the cloud is probably not the right choice. What is that situation?

---

# Part 2: Warmup — Cloud Landscape

These questions are based on the [Cloud Provider Landscape](../lessons/08_cloud_intro/02_cloud_landscape.md) lesson.

### Cloud Landscape Question 1

Name the three hyperscalers. For each, write one sentence describing its primary strength and the type of organization most likely to use it.

### Cloud Landscape Question 2

The lesson explains why this course switched from Microsoft Azure to Supabase. It gives three concrete reasons. Summarize each reason in your own words — one sentence each.

Then add your own reflection: what does this suggest about how you should evaluate a cloud tool when starting a new project?

### Cloud Landscape Question 3

For each of the four scenarios below, identify which service category from the taxonomy table applies (e.g., "object storage", "managed relational DB", "LLM API", "serverless compute") and name one specific provider or product that offers it.

1. You need to store 10 TB of image files and retrieve them by filename from any machine.
2. You need to run an ML training job on a GPU for four hours, then shut it down.
3. You need to host a web API that automatically scales up when traffic spikes and scales down when it quiets.
4. You need to send structured data to a large language model and get a text response back.

### Cloud Landscape Question 4

The lesson says most projects don't use one provider for everything. Describe a simple data project of your own design (one or two sentences is fine) and sketch a plausible stack using services from at least two different providers or products from the taxonomy table. Then answer: is there a benefit to consolidating to one provider, and what would you give up if you did?

---

# Part 3: Project

This week's project has two parts: setting up your Supabase project (which you'll use for the hands-on work in weeks 9–11), and exploring cloud infrastructure costs using the AWS Pricing Calculator.

## A Note on Cloud Assignments

Starting this week, each cloud assignment includes a short video. If you took Python 100, you've done this before.

Cloud proficiency is different from Python proficiency. It is not *primarily* about writing code — it is about navigating an ecosystem: finding the right resources, understanding what things cost, knowing which lever to pull. Videos are a much easier way for you to demonstrate that you know your way around.

Please keep it short. The target is 3 minutes; the **hard limit** is 5.

## Part A: Supabase Setup

Create your Supabase project now so you arrive at Week 9 ready to write code.

### Step 1: Create Your Account and Project

1. Go to [supabase.com](https://supabase.com) and sign up for a free account. No credit card required.
2. Click **New project**. Name it `python200`, choose a region close to you, and set a database password (save it somewhere — you won't need it in this course, but useful to have).
3. Wait for the project to finish provisioning (usually 30–60 seconds).

### Step 2: Locate Your Credentials

In your project dashboard, click the gear icon (Project Settings) in the left sidebar, then **API**. You will see:

- **Project URL** — in the form `https://<project-id>.supabase.co`
- **anon (public) key** — a long string under "Project API keys"

You'll need both of these in Week 9. Keep the tab open for now.

### Step 3: Create a .env File

In a local project folder (or wherever you plan to keep your Week 9 code), create a file called `.env`.

Example — replace the placeholders with your own Project URL and anon key:

```
SUPABASE_URL=https://<your-project-id>.supabase.co
SUPABASE_KEY=<your-anon-key>
```

Immediately add `.env` to your `.gitignore` so it is never committed. API keys committed to a public repository can be scraped within minutes.

### Step 4: Create the Tables

In your Supabase project dashboard, click the **SQL Editor** icon (`</>`) in the left sidebar. Run the following SQL to create the two tables you'll use in weeks 9–11. Use exactly as written — Weeks 9–11 depend on these table and column names:

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

Then run this to disable Row Level Security on both tables. Use exactly as written:

```sql
ALTER TABLE weather_raw     DISABLE ROW LEVEL SECURITY;
ALTER TABLE weather_enriched DISABLE ROW LEVEL SECURITY;
```

### Step 5: Confirm

Navigate to the **Table Editor** in the left sidebar. You should see both `weather_raw` and `weather_enriched` listed. Click each one to confirm the columns are correct.

In `project_08.md`, write a sentence confirming your project is set up (or note any issues you ran into).

---

## Part B: Cloud Cost Analysis

The [AWS Pricing Calculator](https://calculator.aws/) lets you estimate the cost of running infrastructure on AWS without signing in. Building estimates like this is a real, practical skill — in many work contexts you'll be asked to scope infrastructure costs before committing to a design.

The way it works: search for a service, configure it (compute type, storage size, hours of use), and add it to your estimate. The running total accumulates at the bottom.

Before recording your video, build estimates for the two scenarios below, then feel free to explore further. There are hundreds of services — throw in whatever looks interesting and see what happens to the total.

**Scenario A — Lightweight compute:** A `t3.micro` EC2 instance (1 vCPU, 1 GB RAM), on-demand pricing, running 8 hours per day, 5 days per week (approximately 160 hours per month). Use the US East (N. Virginia) region.

**Scenario B — Heavy analytics workload:** A `p3.2xlarge` EC2 instance (8 vCPU, 1 V100 GPU), running 24/7 for the full month (730 hours); an RDS `db.m5.large` instance (2 vCPU, 8 GB RAM); and an S3 Standard storage bucket with 1 TB of data. Use US East (N. Virginia).

In `project_08.md`, write a short summary (a few sentences to a paragraph) covering:

- What each scenario costs, and whether the numbers surprised you.
- (Optional) Anything interesting you found while exploring the calculator beyond the two required scenarios — include this only if you chose to explore further.
- A sentence on how the two scenarios compare — what does the cost difference tell you about when a GPU instance is or isn't worth it?

---

## The Video

Record a single video (target: 3 minutes, max: 5) with audio. Briefly narrate what you are showing as you go.

Post your video somewhere accessible (whatever you used in Python 100) and paste the link in `project_08.md`.

Show the following:

1. **Supabase dashboard** — your project overview, both tables visible in the Table Editor, and the API settings page with your Project URL and anon key visible.
2. **AWS Pricing Calculator** — your completed estimates for both scenarios. Briefly walk through what each scenario costs and mention anything that surprised you.

---

<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

**General grading notes:**

- This assignment is largely short written answers plus a video and a Supabase / AWS Pricing Calculator exploration. The specific numbers, cities, regions, cost estimates, and example stacks a student produces will vary. Do **not** fail a student for differing from any reference answer, from another student, or from your own expectation.
- The reviewer cannot verify the video, the student's Supabase dashboard, or their filesystem. Grade the written deliverables in `warmup_08.md` and `project_08.md`. Do **not** fail on unverifiable external artifacts — a missing-looking video link, dashboard state, the `.env` file, or the `assignments_08/` folder and file names are conventions, not pass/fail conditions.
- Exact-vs-example: the SQL `CREATE TABLE` / `ALTER TABLE` blocks in Part A are `Use exactly as written` — Weeks 9–11 depend on the `weather_raw` / `weather_enriched` table and column names. The `.env` contents and the cost scenarios/values are `Example — adapt to your own values`; grade the reasoning, not the exact figures.

### Required Deliverables/Tasks

- **Warmup Part 1 — Cloud Concepts (Q1–Q5)** — short written answers in `warmup_08.md`, in the student's own words. Q1: the pay-as-you-go / operational-vs-capital model vs owning servers. Q2: vertical vs horizontal scaling, with a concrete example of each, plus a one-sentence call on each of the three scenarios (viral traffic → horizontal; faster GPU/more RAM → vertical; split-able file pipeline → horizontal). Q3: classifies the six items (Gmail, Azure VMs, AWS S3, GitHub Codespaces, Snowflake, Supabase) as IaaS/PaaS/SaaS/BaaS with one sentence of reasoning, then defines IaaS/PaaS/SaaS with an example and what the developer manages for each. Q4: what a managed data platform (Databricks/Snowflake) is and the gain/give-up vs raw AWS/GCP. Q5: names the situation where cloud is not the right choice. Accept reasonable variation in wording and examples; do not require exact category labels to match a key as long as reasoning is sound.
- **Warmup Part 2 — Cloud Landscape (Q1–Q4)** — short written answers in `warmup_08.md`. Q1: names the three hyperscalers (AWS, Azure/Microsoft, GCP/Google) with a strength and likely user for each. Q2: summarizes the three reasons the course moved from Azure to Supabase, one sentence each, plus a short personal reflection. Q3: for the four scenarios, names a service category and one concrete provider/product each. Q4: describes a small data project of the student's own design and sketches a stack using services from at least two providers, then discusses consolidation trade-offs. The reviewer cannot see the lesson; grade whether the answer is coherent and on-topic, not whether it matches specific lesson wording.
- **Supabase setup confirmation** — in `project_08.md`, a sentence confirming the `python200` project is set up (or noting issues). `Example — adapt to your own values` for the region, project details, URL, and keys. Do not fail on the dashboard being unverifiable.
- **Cloud cost analysis write-up** — in `project_08.md`, a short summary covering what each scenario (A: `t3.micro`, ~160 hrs/month; B: `p3.2xlarge` 24/7 + RDS `db.m5.large` + 1 TB S3 Standard) costs, whether the numbers surprised them, and a sentence comparing the two on when a GPU instance is/isn't worth it. `Example — adapt to your own values`: dollar figures vary with the calculator and must not be failed for differing from a reference.
- **Video link** — a link to a short (target 3 min, hard max 5) narrated video posted somewhere accessible, pasted in `project_08.md`, showing the Supabase dashboard/tables/API settings and the two completed AWS calculator estimates. The reviewer cannot open or verify the video; grade only that a link is present, and do not fail for length or content that cannot be inspected.

### Optional Deliverables/Tasks

- **Exploring the AWS Pricing Calculator beyond the two required scenarios** — the assignment invites the student to "feel free to explore further" and "throw in whatever looks interesting," and the corresponding write-up bullet is marked (Optional). Do **not** fail a student who only completed Scenarios A and B and did not report additional exploration.

</details>
