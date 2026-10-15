# Week 8 Mentor Summary: Introduction to Cloud Computing

**Lesson files:** `lessons/08_cloud_intro.md` (overview) and three lessons in `lessons/08_cloud_intro/`, one of them optional
**Assignment file:** `assignments/08_cloud_intro.md`
**Answer key:** `mentor-guidebook/answer-key/assignment_08_key.md`
**Slides:** `mentor-guidebook/slides/08_cloud_intro.pdf`

**Learning objective:** Students learn the core ideas of cloud computing: renting resources instead of owning them, vertical and horizontal scaling, and the IaaS, PaaS, and SaaS service models. They survey the cloud provider landscape, set up the Supabase project and tables for Weeks 9–11, and estimate infrastructure costs with the AWS Pricing Calculator.

**Where this fits:** Week 8 opens the four cloud weeks. It builds on the weather work from Weeks 3 and 4, because the `weather_raw` columns use the same four feature names as the classifier. The Supabase project and the two tables that students create this week are used directly in Weeks 9, 10, and 11. This week also starts the video format that every cloud assignment uses.

---

## Lesson Overview

The two required lessons are conceptual and need no code. The optional lesson is the first part of the Practicum AWS Bridge pilot.

| Lesson | What students learn |
|---|---|
| **1. Cloud Overview** | Cloud computing as renting infrastructure and paying for what you use. Regions. Scalability (vertical and horizontal) and reliability. The IaaS, PaaS, and SaaS spectrum, organized by how much the provider manages. Limitations: a steep learning curve, fast-changing platforms, and costs that grow quickly if resources are left running. Managed data platforms, such as Databricks and Snowflake, compared with using a cloud provider directly. |
| **2. The Cloud Provider Landscape** | The three hyperscalers (AWS, GCP, Azure) and their strengths. Developer-tier platforms (DigitalOcean, Render, Fly.io, Cloudflare). Backend-as-a-service (BaaS) platforms, Firebase and Supabase. Three reasons the course moved from Azure to Supabase: access, pedagogical fit, and pipeline coherence. A service taxonomy table across providers. A preview of the practicum's AWS services: Lambda, EventBridge, IAM, CloudWatch, and Parameter Store. |
| **3. (Optional) Practicum AWS Bridge, Part 1: IAM Permissions** | The bridge mini-project, an alert for when fewer than 80% of students submit an assignment. IAM principals, policies, and roles. Reading a policy statement (`Effect`, `Action`, `Resource`), ARNs, and wildcards. How AWS decides: explicit deny, then allow, then implicit deny. The principle of least privilege. Using `json` and `fnmatchcase` to check a policy in Python. |

---

## Assignment Deliverables

**Setup:** Students work in `assignments_08/` and create two Markdown files. No Python files are required. They create a free Supabase account, and they use the AWS Pricing Calculator, which does not need a sign-in.

**Grading:** Most answers are short and written in the student's own words, so wording, examples, and cost figures vary. Grade the reasoning against the answer key's intended answers. The SQL in Part A must be run exactly as written, because Weeks 9–11 depend on the table and column names. The answer key treats the tables existing, with RLS disabled, as the real check for Part A, and the video is where mentors can see them. The AirHub rubric cannot see the dashboard, so it grades only the confirmation sentence.

| Part | File | What students do | Concepts practiced |
|---|---|---|---|
| Part 1: Cloud Concepts | `warmup_08.md` | Five questions: the pay-as-you-go model, vertical and horizontal scaling with three scenarios, classifying six services as IaaS, PaaS, SaaS, or BaaS, managed data platforms, and when the cloud is the wrong choice | Lesson 1 |
| Part 2: Cloud Landscape | `warmup_08.md` | Four questions: the three hyperscalers, the three reasons for the move to Supabase, a service category and product for four scenarios, and a stack that uses at least two providers | Lesson 2 |
| Part 3A: Supabase Setup | `project_08.md` | Creates the `python200` project, finds the Project URL and anon key, writes `.env` and adds it to `.gitignore`, runs the provided SQL to create both tables and disable RLS, and confirms the setup in one sentence | Credentials, SQL Editor, schema |
| Part 3B: Cloud Cost Analysis | `project_08.md` | Estimates Scenario A (a `t3.micro` for about 160 hours) and Scenario B (a `p3.2xlarge` GPU instance all month, an RDS `db.m5.large`, and 1 TB of S3), then compares them | Cost estimation |
| Video | link in `project_08.md` | A narrated video (target 3 minutes, maximum 5) that shows the Supabase tables and API settings and both cost estimates | Navigating cloud tools |
| (Optional) Part 4: AWS Bridge | `aws_bridge/` | Copies the policy file, writes `policy_notes.md`, writes `iam_checker.py` with four functions, and tests it in `test_iam_checker.py` | IAM, pytest |

**Optional:** Part 4 is an ungraded pilot, and students may skip it with no effect on their grade. Exploring the calculator beyond the two scenarios is also optional. If a student attempts Part 4, give feedback using the notes at the end of the answer key. Partial attempts are acceptable.

**Submission:** A pull request from the student's branch into `main` in their `python200-homework` repository. The `.env` file must not be committed.

---

## Key Concepts

These short explanations cover the ideas students ask about most this week. Expand any one you need.

<details>
<summary><strong>IaaS, PaaS, SaaS, and BaaS: who manages what</strong></summary>

The lesson organizes the service models around one question: how much does the provider manage for you?

- **IaaS:** The provider supplies raw machines, storage, and networking. The developer manages everything from the operating system up. Examples are AWS EC2 and Azure Virtual Machines.
- **PaaS:** The developer brings code and configuration, and the platform runs and scales it. Examples are AWS Elastic Beanstalk and Google App Engine.
- **SaaS:** The user logs in to a finished application, such as Gmail, and manages almost nothing.
- **BaaS:** Defined in Lesson 2. The platform provides ready-made application building blocks, such as a database, authentication, and file storage, through an API. Firebase and Supabase are the examples.

For Concepts Question 3, the answer key's intended labels are Gmail as SaaS, Azure Virtual Machines and S3 as IaaS, GitHub Codespaces as PaaS, Snowflake as SaaS, and Supabase as BaaS. S3 and Snowflake cause the most debate. Accept a different label when the student's reasoning about who manages what is sound.

</details>

<details>
<summary><strong>Row Level Security, the anon key, and the .env file</strong></summary>

Supabase identifies a client with two values: the Project URL and an API key. The course uses the anon (public) key. The Week 9 lesson explains that this key can read and write tables when Row Level Security is disabled.

Row Level Security (RLS) is a PostgreSQL feature that controls which rows a client can read or write. An example rule is "a user can only read their own rows." Supabase turns RLS on for new tables by default. Writing access rules adds complexity, so students disable RLS with the two `ALTER TABLE` statements.

This choice is reasonable for a course with one trusted user and no login system. In a real application with many users, RLS should stay on. Week 9 Connection Question 3 asks students to explain this.

Because the anon key can read and write the unprotected tables, students keep it in `.env` and add `.env` to `.gitignore` before their first commit. The database password must never be committed.

</details>

<details>
<summary><strong>(Optional bridge) How IAM makes a decision</strong></summary>

An IAM policy is a JSON list of statements. Each statement has an `Effect` (`"Allow"` or `"Deny"`), an `Action`, and a `Resource`. A statement matches a request when both its action and its resource match. AWS then applies three rules in order:

1. If any matching statement is a Deny, the result is an **explicit deny**.
2. Otherwise, if any matching statement is an Allow, the request is **allowed**.
3. Otherwise, the result is an **implicit deny**. Everything starts out denied.

The order of the statements in the file does not matter. In the course policy, `ReadAlertSettings` allows reading every setting under `/ctd/submission-alert/`, and `BlockAdminSettings` denies everything under `/ctd/submission-alert/admin/`. A read of `admin/override` matches both, so the Deny wins.

Two details cause most bugs. Actions are case-insensitive, and ARNs are case-sensitive. Also, `Action` and `Resource` can each be a single string or a list. The answer key says that students who understand the evaluation order usually write the code without trouble.

</details>

---

## FAQs and Common Trouble Spots

**1. "Is Snowflake SaaS or PaaS? Is S3 really IaaS?"**
The answer key lists Snowflake as SaaS and S3 as IaaS, but it accepts well-reasoned alternatives for both. Ask the student what the developer manages and what the provider manages. If the answer to that question supports their label, give credit.

**2. "When do I create my Supabase project?"**
This week. The assignment and the Week 8 lessons both ask students to create the project and both tables in Week 8, so that they arrive at Week 9 ready to write code. Students should use the provided SQL exactly as written, including the table and column names.

**3. "I created the tables but did not run the `ALTER TABLE` statements. Does it matter?"**
Yes. RLS stays on, and the Week 9 scripts that use the anon key will not be able to read or write rows normally. Ask the student to run the two `ALTER TABLE ... DISABLE ROW LEVEL SECURITY` statements in the SQL Editor. Then check the tables in the Table Editor.

**4. "Should I commit my `.env` file?"**
No. Students add `.env` to `.gitignore` before their first commit. If a student has already committed it to a public repository, the Week 9 lesson says to rotate the key in the Supabase dashboard right away. The database password should never be committed.

**5. "My cost estimates do not match my classmates' numbers."**
AWS prices change, so grade the reasoning, not exact dollar amounts. The answer key's rough anchors are a few dollars a month for Scenario A and about $2,300–2,500 a month for Scenario B. The GPU instance is about $2,200 of Scenario B. A strong write-up notes that the GPU dominates the cost, so it is worth paying for only when it is busy.

**6. "Is the video graded?"**
Only the link is graded. The rubric and the answer key both require a video link in `project_08.md`. The AirHub reviewer cannot watch the video, so its content is not graded. Mentors can still watch it to confirm the Supabase tables and to give feedback. Do not fail a student for video length or content.

**7. "(Optional bridge) My checker says every request is an explicit deny," or "The admin request comes back allowed."**
Every row returning `"explicit deny"` usually means the code loops over a single string such as `"ssm:*"`. That loop produces single characters, and the lone `*` matches everything. An `"allowed"` result for `admin/override` usually means the code returns on the first matching statement instead of checking all of them. The answer key lists these and other common mistakes.
