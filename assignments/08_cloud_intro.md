# Week 8 Assignments

This week's assignments cover the cloud computing concepts from the two Week 8 lessons:

- Core cloud concepts: what cloud computing is, how services are delivered, and when it makes sense
- The cloud provider landscape: hyperscalers, developer platforms, and backend-as-a-service

The warmup is a check for understanding — short written answers, no code. The project introduces the video format used for the rest of the cloud weeks, and gets your Supabase project set up so you're ready to write code in Week 9.

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_08/`. Inside that folder, create two files:

1. `warmup_08.md` — for the warmup questions
2. `project_08.md` — for the Supabase setup notes and cost analysis write-up, plus your video link

If you choose to do the optional Practicum AWS Bridge in Part 4, also create an `aws_bridge/` folder inside `assignments_08/`. Part 4 lists the files that go in it.

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

1. **Supabase dashboard** — your project overview, both tables visible in the Table Editor, and the API settings page with your Project URL visible. Do not show your anon key in the video. Hide or blur it before you record, or scroll so that it is not on screen. Anyone who watches the video could copy a visible key.
2. **AWS Pricing Calculator** — your completed estimates for both scenarios. Briefly walk through what each scenario costs and mention anything that surprised you.

---

# Part 4: (Optional) Practicum AWS Bridge — IAM Policy Checker

> **This entire part is optional.** The Practicum AWS Bridge is a pilot this term. You can skip all of Part 4 without any effect on your grade.

This part goes with the optional lesson [Practicum AWS Bridge, Part 1: IAM Permissions](../lessons/08_cloud_intro/03_aws_bridge_iam.md). The bridge is a four-week mini-project that is separate from the weather pipeline. Each week adds one piece to an automatic alert that tells the Code the Dream teaching team when fewer than 80% of students submit their weekly assignment. This week, you write a Python checker that reads the alert's IAM policy and decides whether the policy allows a request.

You do not need an AWS account, and you do not need to install anything new. You will use the `json` and `fnmatch` modules from the standard library, and `pytest`, which you used in Week 1.

Plan for about two hours, in addition to the optional lesson.

## Task 1: (Optional) Set Up the Folder

Create a folder called `aws_bridge/` inside `assignments_08/`. Copy the file `submission_alert_policy.json` into it. You can find this file in the course repository at `assignments/resources/aws_bridge/submission_alert_policy.json`.

You will keep adding to this folder in Weeks 9, 10, and 11.

## Task 2: (Optional) Read the Policy

Open `submission_alert_policy.json` and read its four statements. Then create `aws_bridge/policy_notes.md` and answer these questions in your own words:

1. For each of the four statements, write one sentence that says what the statement allows or denies, and on which resources. Use the statement's `Sid` as a label.
2. The `PublishSubmissionMetric` statement uses `"Resource": "*"`. Why does it use `*`, and why does this statement still follow the principle of least privilege?
3. A teammate suggests replacing the `ReadAlertSettings` and `BlockAdminSettings` statements with one simpler statement: `{"Effect": "Allow", "Action": "ssm:*", "Resource": "*"}`. The alert would still be able to read its settings. In two or three sentences, explain what risk this change adds.

## Task 3: (Optional) Write the Policy Checker

Create `aws_bridge/iam_checker.py`. Write the four functions below.

Use exactly as written: the file name `iam_checker.py`, the four function names, their parameters, and the three result strings `"allowed"`, `"explicit deny"`, and `"implicit deny"`. The Week 11 part of the bridge imports these functions by name.

1. **`load_policy(path)`** reads a JSON policy file and returns it as a dictionary.

2. **`statement_matches(statement, action, resource)`** returns `True` if one statement applies to the request, and `False` otherwise. A statement applies when **both** of these are true:
    - At least one pattern in the statement's `"Action"` matches `action`. Compare actions **without** regard to case, so `SSM:getparameter` matches `ssm:GetParameter`.
    - At least one pattern in the statement's `"Resource"` matches `resource`. Compare resources **with** regard to case.

    In both fields, `*` matches any sequence of characters and `?` matches exactly one character. Each field can be either a single string or a list of strings, and your function needs to handle both.

3. **`evaluate(policy, action, resource)`** returns one of three strings, using these rules in this order:
    - If any statement that applies has `"Effect": "Deny"`, return `"explicit deny"`.
    - Otherwise, if any statement that applies has `"Effect": "Allow"`, return `"allowed"`.
    - Otherwise, return `"implicit deny"`.

    The order of the statements in the policy does not change the result.

4. **`is_allowed(policy, action, resource)`** returns `True` if `evaluate` returns `"allowed"`, and `False` in every other case.

You do not need to support any other parts of IAM, such as `Condition`, `NotAction`, or `Principal`.

## Task 4: (Optional) Test the Checker

Create `aws_bridge/test_iam_checker.py` and write pytest tests for your checker.

Your tests should check at least the six requests in the table below against `submission_alert_policy.json`. Each request uses the account ID `123456789012` and the region `us-east-1`. Use `@pytest.mark.parametrize` so that one test function checks all six rows.

| Action | Resource | Expected result from `evaluate` |
|---|---|---|
| `ssm:GetParameter` | `arn:aws:ssm:us-east-1:123456789012:parameter/ctd/submission-alert/threshold` | `"allowed"` |
| `SSM:getparameter` | `arn:aws:ssm:us-east-1:123456789012:parameter/ctd/submission-alert/threshold` | `"allowed"` |
| `ssm:GetParameter` | `arn:aws:ssm:us-east-1:123456789012:parameter/ctd/submission-alert/admin/override` | `"explicit deny"` |
| `ssm:PutParameter` | `arn:aws:ssm:us-east-1:123456789012:parameter/ctd/submission-alert/threshold` | `"implicit deny"` |
| `cloudwatch:PutMetricData` | `*` | `"allowed"` |
| `s3:GetObject` | `arn:aws:s3:::ctd-gradebook/week07.csv` | `"implicit deny"` |

Then add **at least two tests of your own**. Choose cases that the table does not cover. Here are some ideas:

- A statement whose `"Action"` is a single string instead of a list
- A wildcard action, such as `s3:Get*`
- A resource ARN that differs from an allowed ARN only in uppercase and lowercase letters

**Tip:** Your tests need to find the policy file no matter which folder you run `pytest` from. One way to do this is `Path(__file__).parent / "submission_alert_policy.json"`, which builds the path relative to the test file.

Run `pytest` and confirm that every test passes.

---

<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

**General grading notes:**

- This assignment is largely short written answers plus a video and a Supabase / AWS Pricing Calculator exploration. The specific numbers, cities, regions, cost estimates, and example stacks a student produces will vary. Do **not** fail a student for differing from any reference answer, from another student, or from your own expectation.
- The reviewer cannot verify the video, the student's Supabase dashboard, or their filesystem. Grade the written deliverables in `warmup_08.md` and `project_08.md`. Do **not** fail on unverifiable external artifacts — a missing-looking video link, dashboard state, the `.env` file, or the `assignments_08/` folder and file names are conventions, not pass/fail conditions.
- **Part 4 (Practicum AWS Bridge) is entirely optional.** It is a pilot this term. All of its tasks are listed under Optional Deliverables/Tasks below. Never fail a student for skipping it.
- Exact-vs-example: the SQL `CREATE TABLE` / `ALTER TABLE` blocks in Part A are `Use exactly as written` — Weeks 9–11 depend on the `weather_raw` / `weather_enriched` table and column names. The `.env` contents and the cost scenarios/values are `Example — adapt to your own values`; grade the reasoning, not the exact figures.

### Required Deliverables/Tasks

- **Warmup Part 1 — Cloud Concepts (Q1–Q5)** — short written answers in `warmup_08.md`, in the student's own words. Q1: the pay-as-you-go / operational-vs-capital model vs owning servers. Q2: vertical vs horizontal scaling, with a concrete example of each, plus a one-sentence call on each of the three scenarios (viral traffic → horizontal; faster GPU/more RAM → vertical; split-able file pipeline → horizontal). Q3: classifies the six items (Gmail, Azure VMs, AWS S3, GitHub Codespaces, Snowflake, Supabase) as IaaS/PaaS/SaaS/BaaS with one sentence of reasoning, then defines IaaS/PaaS/SaaS with an example and what the developer manages for each. Q4: what a managed data platform (Databricks/Snowflake) is and the gain/give-up vs raw AWS/GCP. Q5: names the situation where cloud is not the right choice. Accept reasonable variation in wording and examples; do not require exact category labels to match a key as long as reasoning is sound.
- **Warmup Part 2 — Cloud Landscape (Q1–Q4)** — short written answers in `warmup_08.md`. Q1: names the three hyperscalers (AWS, Azure/Microsoft, GCP/Google) with a strength and likely user for each. Q2: summarizes the three reasons the course moved from Azure to Supabase, one sentence each, plus a short personal reflection. Q3: for the four scenarios, names a service category and one concrete provider/product each. Q4: describes a small data project of the student's own design and sketches a stack using services from at least two providers, then discusses consolidation trade-offs. The reviewer cannot see the lesson; grade whether the answer is coherent and on-topic, not whether it matches specific lesson wording.
- **Supabase setup confirmation** — in `project_08.md`, a sentence confirming the `python200` project is set up (or noting issues). `Example — adapt to your own values` for the region, project details, URL, and keys. Do not fail on the dashboard being unverifiable.
- **Cloud cost analysis write-up** — in `project_08.md`, a short summary covering what each scenario (A: `t3.micro`, ~160 hrs/month; B: `p3.2xlarge` 24/7 + RDS `db.m5.large` + 1 TB S3 Standard) costs, whether the numbers surprised them, and a sentence comparing the two on when a GPU instance is/isn't worth it. `Example — adapt to your own values`: dollar figures vary with the calculator and must not be failed for differing from a reference.
- **Video link** — a link to a short (target 3 min, hard max 5) narrated video posted somewhere accessible, pasted in `project_08.md`, showing the Supabase dashboard/tables/API settings and the two completed AWS calculator estimates. The reviewer cannot open or verify the video; grade only that a link is present, and do not fail for length or content that cannot be inspected.

### Optional Deliverables/Tasks

- **Exploring the AWS Pricing Calculator beyond the two required scenarios** — the assignment invites the student to "feel free to explore further" and "throw in whatever looks interesting," and the corresponding write-up bullet is marked (Optional). Do **not** fail a student who only completed Scenarios A and B and did not report additional exploration.
- **Part 4 — (Optional) Practicum AWS Bridge: IAM Policy Checker.** This entire part is an optional pilot. Do **not** fail or ask for revisions from a student who skipped any or all of Part 4, and do not count a missing `aws_bridge/` folder against them. If the student attempted Part 4, give feedback on what they submitted, using the notes below. A partial attempt is acceptable.
    - **Task 1 (setup)** — an `aws_bridge/` folder containing a copy of `submission_alert_policy.json`. `Example — adapt to your own layout`: the location the student copied the file from, and where the folder sits, are not pass/fail conditions.
    - **Task 2 (`policy_notes.md`)** — (1) one sentence per statement (`ReadAlertSettings`, `BlockAdminSettings`, `PublishSubmissionMetric`, `WriteOwnLogs`) saying what it allows or denies and on which resources; (2) an explanation that `cloudwatch:PutMetricData` does not support resource ARNs, so it must use `"Resource": "*"`, and that the statement still follows least privilege because it allows only that one action; (3) the risk of replacing the two Parameter Store statements with `ssm:*` on `*`: the alert could then change or delete *any* Parameter Store setting in the account, including the `admin/` settings that the current policy denies, so a bug or misuse could do much more damage. Accept any reasonable wording.
    - **Task 3 (`iam_checker.py`)** — the functions `load_policy(path)`, `statement_matches(statement, action, resource)`, `evaluate(policy, action, resource)`, and `is_allowed(policy, action, resource)`. `Use exactly as written (later tasks depend on these names)`: the file name, the four function names and their parameters, and the result strings `"allowed"`, `"explicit deny"`, and `"implicit deny"`. Behavior to check: actions match case-insensitively and resources case-sensitively; `*` and `?` wildcards work in both fields; `Action` and `Resource` accept a string or a list; a matching Deny always wins over a matching Allow, regardless of statement order; a request that no statement matches returns `"implicit deny"`. The implementation approach is the student's choice (for example, `fnmatch.fnmatchcase`, `re`, or hand-written matching).
    - **Task 4 (`test_iam_checker.py`)** — pytest tests that cover the six rows of the table in the assignment, using `@pytest.mark.parametrize`, plus at least two additional cases of the student's choosing. `Example — adapt to your own layout`: how the test locates the policy file (the `Path(__file__)` tip is a suggestion, not a requirement).

</details>
