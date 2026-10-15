# Assignment 8 Answer Key: Cloud Intro

**Mentor note:** Week 8 is conceptual — there is **no required Python code** this week. (The optional Practicum AWS Bridge in Part 4 has a small amount of Python; see the end of this key.) Deliverables are two Markdown files (warmup answers + project write-up), a Supabase project setup, an AWS cost analysis, and a short video. The **video link is required**, so check that a link is present. The AirHub reviewer cannot watch the video, so its content is not graded. Focus on the written answers and on whether the Supabase tables were actually created. Mentors may watch the video to confirm the tables and to give feedback. Many warmup questions are conceptual with clear intended answers (given below); a few are open reflection. Where an answer depends on the specific lesson text (for example, "the situation where cloud isn't the right choice" in Concepts Q5), the key gives the lesson's answer and marks the question "check against lesson".

---

## Expected File Setup

Assignment lives in `assignments_08/`:

```
assignments_08/
├── warmup_08.md     # cloud concepts + landscape written answers
└── project_08.md    # Supabase setup confirmation + AWS cost write-up + video link
```

Submitted as a PR. No `.py` files are required this week.

Students who do the **optional** Practicum AWS Bridge (Part 4) also have:

```
assignments_08/
└── aws_bridge/
    ├── submission_alert_policy.json   # copied from assignments/resources/aws_bridge/
    ├── policy_notes.md                # Task 2
    ├── iam_checker.py                 # Task 3
    └── test_iam_checker.py            # Task 4
```

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
- GCP — strength in data, analytics, and machine learning (the lesson names BigQuery and Vertex AI); data-heavy and ML-focused orgs. A student who also mentions Kubernetes is not wrong, but the lesson does not say it, so do not require it.

### Cloud Landscape Q2 — **Subjective** (check against lesson)
Three reasons the course switched Azure→Supabase (summarize each). The lesson gives exactly these three:
1. **Access** — Azure needs organizational provisioning (joining a tenant, waiting for an invitation), which can block students for days. Students create a Supabase account themselves in minutes, and the free tier covers the whole course.
2. **Pedagogical fit** — Azure Blob Storage stores opaque files by path. Supabase stores rows and columns in a relational database, and querying structured data is a more transferable skill.
3. **Pipeline coherence** — the raw zone and enriched zone of the Weeks 9–11 pipeline become two related tables that are easy to query, inspect, and debug.

Accept the student's own wording as long as each reason maps to one of these three. Do not require the lesson's labels. Answers such as "easier signup" or "free tier" are part of **access**; they do not count as separate reasons. Reflection should land on: match the tool to the project's scale and the team's skill — don't default to the biggest/most complex provider.

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

### The Video — **Link required; content not graded**
A link must be present in `project_08.md`. The video should show the Supabase dashboard and the AWS estimates, but the AirHub reviewer cannot watch it, so do not fail a student for its length or content. Mentors may watch it to give feedback.

---

# Part 4: (Optional) Practicum AWS Bridge — IAM Policy Checker

**Mentor note:** This part is an **optional pilot** this term. Never ask a student to revise because they skipped it. It goes with the optional lesson `lessons/08_cloud_intro/03_aws_bridge_iam.md`, which is the first of four bridge lessons (Weeks 8–11). The bridge builds a small, separate feature: a Lambda function that alerts the CTD teaching team when fewer than 80% of students submit their weekly assignment. No AWS account is needed. Week 8 uses only the standard library and pytest. The expected time is about two hours plus the lesson.

The most useful thing a mentor can do here is help students reason about the **evaluation order**: an explicit Deny wins, then an Allow, and anything else is an implicit deny. Students who understand that order usually write the code without trouble.

### Task 1: Setup — **Not assessed**
An `aws_bridge/` folder with a copy of `submission_alert_policy.json`. Where the student copied it from does not matter.

### Task 2: `policy_notes.md` — **Subjective**
1. One sentence per statement. Reference answers:
    - `ReadAlertSettings` allows reading one or several Parameter Store settings (`ssm:GetParameter`, `ssm:GetParameters`) whose names start with `/ctd/submission-alert/`.
    - `BlockAdminSettings` denies every Parameter Store action on settings under `/ctd/submission-alert/admin/`. Because a Deny wins, the alert cannot read the admin settings even though `ReadAlertSettings` covers those names.
    - `PublishSubmissionMetric` allows sending custom metrics to CloudWatch.
    - `WriteOwnLogs` allows creating log streams and writing log lines, but only in the alert's own log group, `/aws/lambda/submission-alert`.
2. `cloudwatch:PutMetricData` **does not support resource-level permissions**, so its statement has to use `"Resource": "*"`. It still follows least privilege because it allows only that one action. (In real AWS, a `cloudwatch:namespace` condition can narrow it further. The lesson leaves conditions out, so do not expect this.)
3. With `ssm:*` on `*` in place of the two Parameter Store statements, the alert could create, change, or delete **any** setting in the account, including the `admin/` settings that the current policy explicitly denies. A bug in the alert, or someone misusing it, could then overwrite or delete settings that other systems depend on. A strong answer also notes that the explicit Deny is gone, so nothing protects the admin settings anymore.

### Task 3: `iam_checker.py` — **Objective (approach)**
The names are exact, because Week 11 imports them. Any correct matching approach is fine. Reference solution:

```python
"""A simplified IAM policy checker for the submission alert."""

import json
from fnmatch import fnmatchcase


def load_policy(path):
    """Read an IAM policy document from a JSON file and return it as a dict."""
    with open(path) as f:
        return json.load(f)


def _as_list(value):
    """IAM allows a single string or a list of strings. Always return a list."""
    if isinstance(value, str):
        return [value]
    return list(value)


def statement_matches(statement, action, resource):
    """Return True if this statement covers both the action and the resource."""
    # Action names are case-insensitive in IAM; resource ARNs are case-sensitive.
    action_match = any(
        fnmatchcase(action.lower(), pattern.lower())
        for pattern in _as_list(statement["Action"])
    )
    resource_match = any(
        fnmatchcase(resource, pattern)
        for pattern in _as_list(statement["Resource"])
    )
    return action_match and resource_match


def evaluate(policy, action, resource):
    """Return "explicit deny", "allowed", or "implicit deny"."""
    matching = [s for s in policy["Statement"] if statement_matches(s, action, resource)]
    if any(s["Effect"] == "Deny" for s in matching):
        return "explicit deny"
    if any(s["Effect"] == "Allow" for s in matching):
        return "allowed"
    return "implicit deny"


def is_allowed(policy, action, resource):
    """Return True only if the policy allows this action on this resource."""
    return evaluate(policy, action, resource) == "allowed"
```

Common mistakes:
- **Treating Allow and Deny in statement order** (for example, returning on the first matching statement). The policy file puts the Allow before the Deny, so this bug returns `"allowed"` for the `admin/override` row. The Task 4 table catches it.
- **Lowercasing the resource as well as the action.** Resources are case-sensitive, so this makes an uppercase ARN match when it should not.
- **Not handling a single string.** `for pattern in "ssm:*"` loops over the characters `s`, `s`, `m`, `:`, `*`, and Python raises no error. The lone `*` matches everything, so `BlockAdminSettings` then matches every request, and **every** row of the table returns `"explicit deny"`. If a student says "everything is denied," check this first.
- **Using `fnmatch.fnmatch` instead of `fnmatchcase`.** `fnmatch` follows the operating system's case rules, so it is case-insensitive on Windows and case-sensitive on macOS and Linux. `fnmatchcase` behaves the same everywhere.
- `fnmatch` also treats `[` and `]` as special characters. Real IAM does not, but no ARN in this exercise contains brackets, so it does not matter here.

### Task 4: `test_iam_checker.py` — **Objective (approach)**
A parametrized test covering the six table rows, plus at least two cases the student chose. Reference tests (13 cases):

```python
from pathlib import Path

import pytest
from iam_checker import evaluate, is_allowed, load_policy, statement_matches

ARN_PARAM = "arn:aws:ssm:us-east-1:123456789012:parameter/ctd/submission-alert/"
ARN_LOGS = "arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/submission-alert:"


@pytest.fixture
def policy():
    return load_policy(Path(__file__).parent / "submission_alert_policy.json")


@pytest.mark.parametrize(
    "action, resource, expected",
    [
        ("ssm:GetParameter", ARN_PARAM + "threshold", "allowed"),
        ("SSM:getparameter", ARN_PARAM + "threshold", "allowed"),  # actions ignore case
        ("ssm:GetParameter", ARN_PARAM + "admin/override", "explicit deny"),  # deny wins
        ("ssm:PutParameter", ARN_PARAM + "threshold", "implicit deny"),  # never allowed
        ("ssm:GetParameter", ARN_PARAM.upper() + "THRESHOLD", "implicit deny"),  # ARNs keep case
        ("cloudwatch:PutMetricData", "*", "allowed"),
        ("logs:PutLogEvents", ARN_LOGS + "log-stream:2026/10/15", "allowed"),
        ("logs:PutLogEvents", "arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/other:x", "implicit deny"),
        ("s3:GetObject", "arn:aws:s3:::ctd-gradebook/week07.csv", "implicit deny"),
    ],
)
def test_evaluate(policy, action, resource, expected):
    assert evaluate(policy, action, resource) == expected


def test_is_allowed_matches_evaluate(policy):
    assert is_allowed(policy, "cloudwatch:PutMetricData", "*") is True
    assert is_allowed(policy, "ssm:GetParameter", ARN_PARAM + "admin/override") is False


def test_statement_accepts_string_or_list():
    single = {"Effect": "Allow", "Action": "s3:GetObject", "Resource": "arn:aws:s3:::b/*"}
    listed = {"Effect": "Allow", "Action": ["s3:GetObject"], "Resource": ["arn:aws:s3:::b/*"]}
    for statement in (single, listed):
        assert statement_matches(statement, "s3:GetObject", "arn:aws:s3:::b/file.txt")


def test_wildcard_in_action():
    statement = {"Effect": "Allow", "Action": "s3:Get*", "Resource": "*"}
    assert statement_matches(statement, "s3:GetObjectTagging", "arn:aws:s3:::b/x")
    assert not statement_matches(statement, "s3:PutObject", "arn:aws:s3:::b/x")


def test_empty_policy_denies_everything():
    assert evaluate({"Statement": []}, "s3:GetObject", "*") == "implicit deny"
```

Good additional cases test a wildcard action, an ARN that differs only in case, a single-string versus list field, or an empty policy. If a student's tests only repeat the table with different spacing, suggest a case that would catch one of the common mistakes above.
