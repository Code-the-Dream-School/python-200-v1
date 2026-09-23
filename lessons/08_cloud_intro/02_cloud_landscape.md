# The Cloud Provider Landscape

The previous lesson covered the conceptual landscape of cloud computing — what it is, how service models are organized, and what changes when you move from a laptop to a data center. Now it's worth asking: whose data center? There are dozens of cloud providers, and the right answer depends on the problem you're solving, the organization you're working in, and what tradeoffs you're willing to make. This lesson gives you a working map of that landscape, so you can orient yourself when you encounter a new provider or evaluate a new tool.

## The Big Three Hyperscalers

"Hyperscaler" is the industry term for cloud providers that operate at planetary scale — hundreds of data centers across every major region, hundreds of services covering almost every imaginable use case. There are three:

**Amazon Web Services (AWS)** is the oldest and largest, with over a third of the cloud market. AWS pioneered the cloud infrastructure model starting in 2006 and has the broadest service catalog of any provider. If you're working in a large enterprise, a startup, or a nonprofit with engineering staff, AWS is probably in the mix. Notable services: EC2 (compute), S3 (object storage), RDS (managed databases), SageMaker (ML platform), Lambda (serverless functions).

**Google Cloud Platform (GCP)** is strongest in data and machine learning. Google built many of the foundational ideas in modern distributed systems (MapReduce, Bigtable, Dremel — the precursor to BigQuery) and GCP reflects that heritage. If you're working on large-scale analytics or ML infrastructure, GCP is often the preferred environment. Notable services: BigQuery (data warehouse), Vertex AI (ML platform), Cloud Run (serverless containers), Pub/Sub (event streaming).

**Microsoft Azure** is the dominant provider in enterprise and government settings, largely because of its deep integration with Windows, Active Directory, and Microsoft 365. Many large nonprofits and public-sector organizations are already Azure customers through existing Microsoft agreements. Notable services: Azure VMs (compute), Blob Storage (object storage), Azure SQL / Cosmos DB (databases), Azure OpenAI Service (LLM API access), Azure Machine Learning.

All three offer roughly equivalent capabilities for most workloads. The main reasons to choose one over another are:
- What your organization already uses (switching costs are real)
- Where the relevant data or team expertise already lives
- Specific services with no equivalent elsewhere (e.g., BigQuery on GCP, Azure OpenAI access)
- Pricing for your specific usage pattern

## Developer-Tier Platforms

Between the hyperscalers and running your own servers, there's a tier of providers that trade breadth for simplicity. They typically offer fewer services but make what they do offer much easier to set up and reason about.

**DigitalOcean** popularized simple, predictable cloud pricing — a $6/month "Droplet" (VM) that behaves like a basic Linux server, with clear pricing and good documentation aimed at developers rather than enterprise architects. DigitalOcean also offers managed databases and Kubernetes (its "App Platform") for teams that want to move past bare VMs without the full complexity of AWS.

**Render** and **Fly.io** take this further — they'll take a Dockerfile or a Git repo, infer what kind of service it is, and deploy it automatically. Managed Postgres is first-class on both. These are popular choices for small teams that want deployment to feel like `git push`.

**Cloudflare** occupies a different niche. It started as a CDN (content delivery network) and DDoS protection layer, but has expanded into compute (Workers, a serverless JavaScript/WASM runtime that runs at the network edge), object storage (R2, which is S3-compatible and has no egress fees), and key-value stores. It's increasingly relevant for AI applications that need low-latency inference at the edge.

## Backend-as-a-Service (BaaS)

Backend-as-a-service platforms sit at a higher abstraction layer than any of the above. Rather than giving you raw infrastructure to configure, they give you application-level primitives — database, authentication, file storage, realtime subscriptions — pre-wired and accessible via API.

**Firebase** (Google) is the dominant BaaS. It provides a NoSQL document database (Firestore), authentication, cloud functions, and hosting, all integrated and managed. It's especially popular for mobile apps and frontend-heavy web applications. The tradeoff is that Firestore's data model (document/collection) diverges sharply from relational databases, which can be limiting for data-heavy work.

**Supabase** is the open-source Firebase alternative built on PostgreSQL. Where Firebase gives you a document store, Supabase gives you a real relational database with SQL, indexes, foreign keys, and joins — plus an automatically generated REST API on top, authentication, and file storage. Because it's Postgres under the hood, anything you learn working with Supabase transfers directly to raw database work.

Supabase is what we'll use for the hands-on portion of this course, starting in Week 9.

## Why Supabase for This Course

The version of this course originally used Microsoft Azure. We moved to Supabase for three practical reasons:

**Access.** Azure requires organizational provisioning — joining a tenant, waiting for an invitation, configuring authentication. Students who join late, or who run into tenant-level configuration problems, can be blocked for days. Supabase accounts are self-provisioned at supabase.com in under two minutes and the free tier is sufficient for everything in this course.

**Pedagogical fit.** Azure Blob Storage — the main Azure service we used — stores data as opaque files, organized by path. Supabase stores data as rows and columns in a relational database. A relational database is more transferable: querying, filtering, and reasoning about structured data is a skill you'll use in almost every data role. The pipeline you'll build in weeks 9–11 maps naturally onto tables and queries.

**Pipeline coherence.** The ETL pipeline you build in weeks 9–11 has a raw zone and an enriched zone. In Supabase, these are two tables with a clear relationship between them. That structure reinforces the data model concepts introduced in this week and makes the pipeline stages easy to inspect and debug. You can query either table at any point to verify what's in it.

This is not a statement that Supabase is the right tool for every job — or even for most jobs at scale. But for learning the concepts that carry across all cloud data work (idempotent writes, data model design, credential management, structured storage), it's a good fit.

## A Service Taxonomy

When you encounter a new cloud provider, it helps to know what categories of services to look for. Most data-focused cloud work involves some combination of these:

| Category | What it does | AWS | GCP | Azure | Supabase |
|---|---|---|---|---|---|
| **Compute** | Run code on a server | EC2 | Compute Engine | Virtual Machines | — |
| **Serverless compute** | Run functions without managing servers | Lambda | Cloud Functions | Azure Functions | Edge Functions |
| **Object storage** | Store files by key | S3 | Cloud Storage | Blob Storage | Storage |
| **Managed relational DB** | Hosted SQL database | RDS | Cloud SQL | Azure SQL | ✓ (core product) |
| **Data warehouse** | Analytical queries at scale | Redshift | BigQuery | Synapse Analytics | — |
| **LLM API** | Access to large language models | Bedrock | Vertex AI | Azure OpenAI | — |
| **ML platform** | Train and deploy models | SageMaker | Vertex AI | Azure ML | — |

Most projects don't use one provider for everything. A common pattern: GCP BigQuery for analytics, Supabase for the application database, Cloudflare for edge compute, OpenAI directly for LLM access. Knowing the service taxonomy helps you read job descriptions, evaluate architectural decisions, and ask good questions when you join a new team.

### A Preview of the Practicum's AWS Stack

The hands-on work in *this* course uses Supabase, and you do not need an AWS account for anything here. The practicum that follows this course, however, deploys a pipeline on AWS using a small set of serverless services. It is worth knowing what each one does before you get there, so the names are familiar rather than new. You will not set any of these up in this course -- this is orientation, not a task.

- **Lambda** runs your code without a server you manage. You hand AWS a function, and it runs on demand and bills only for the time the function is actually executing. This is the serverless compute from the taxonomy table above, and it is where the practicum runs its pipeline code.
- **EventBridge** triggers a Lambda on a schedule, for example "run this every morning at 6 a.m." It is what turns a function into a pipeline that runs on its own.
- **IAM** (Identity and Access Management) controls *permissions*: which service is allowed to do what. Instead of passwords, AWS services are given *roles* that grant specific, limited access, such as "this Lambda may read from this one storage bucket and nothing else."
- **CloudWatch** collects logs and metrics, so you can see what a Lambda did and whether it failed. It is the cloud equivalent of reading your program's output.
- **Parameter Store** holds configuration and secrets, such as an API key, so they are not hard-coded into your function.

You will see the same ideas in a different form during weeks 9 through 11, where Supabase stores your data and Prefect schedules and logs your pipeline. The concepts -- run code on demand, schedule it, control access, log what happened, store secrets safely -- carry across every cloud provider.

## What Comes Next

Weeks 9–11 are hands-on with Supabase. By the end of week 11, you'll have a complete ETL pipeline that:

- Fetches weather data from an external API
- Loads it into a `weather_raw` table in Supabase
- Runs an ML classifier and an LLM enrichment step on each record
- Writes the enriched output to a `weather_enriched` table
- Orchestrates all of this as a Prefect flow with retries, logging, and idempotent writes

In Week 9, you'll create your Supabase project, set up the two tables, and write your first load script. All of the setup is self-contained — no invitations, no tenant configuration, no waiting.
