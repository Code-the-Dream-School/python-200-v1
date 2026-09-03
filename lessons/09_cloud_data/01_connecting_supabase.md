# Connecting to Supabase from Python

Everything you have built so far has run entirely on your local machine — reading files from disk, processing them, and writing results back to disk or to memory. That work is real, but when a script finishes, its output lives in a local folder on your laptop. If you deleted the folder, ran the script on a different machine, or wanted another script to pick up where it left off, you had a problem.

This week you fix that by moving data storage to the cloud. The service you will use is **Supabase** — a hosted Postgres database with a Python SDK that makes inserting and querying rows as simple as calling a method on an object. By the end of this lesson, you will have a Supabase project connected to a Python script and ready to receive data.

## Learning Objectives

By the end of this lesson, you will be able to:

- Explain what Supabase is and how it differs from file-based cloud storage
- Create a Supabase project and locate your project URL and API key
- Store credentials safely in a `.env` file and load them with `python-dotenv`
- Connect to Supabase from Python using `supabase-py` and verify the connection

## What Is Supabase?

Supabase is a hosted PostgreSQL database with a set of tools built around it: a web dashboard for managing tables, a REST API for reading and writing data, and official client libraries for Python, JavaScript, and other languages. The Python library — `supabase-py` — is what you will use throughout this course.

Unlike Azure Blob Storage (which stores arbitrary files), Supabase stores **rows and columns**. If your data is structured — records with defined fields, like the daily weather observations you will be working with — a relational database is the right tool. You can query by field value, filter by date, join tables, and enforce that every row has the required columns. None of that is possible with file-based storage.

Supabase has a generous free tier that is more than sufficient for this course. You do not need to provide a credit card.

## Creating a Project

1. Go to [supabase.com](https://supabase.com) and sign up for a free account.
2. Click **New project**. Give it a name (e.g., `python200`), choose a region close to you, and set a database password. Save that password somewhere — you will not need it for this course, but it is useful to have.
3. Wait for the project to finish provisioning (usually 30–60 seconds).

Once the project is ready, you will land on the project dashboard. Everything you need is here.

## Getting Your Credentials

Supabase uses two pieces of information to identify and authenticate a client:

- **Project URL** — a unique URL for your project, in the form `https://<project-id>.supabase.co`. This is the address your Python script talks to.
- **API key (anon key)** — a long string that identifies your application. Supabase exposes two keys: the `anon` (public) key and the `service_role` (secret) key. For this course you will use the `anon` key, which has read and write access to tables by default when Row Level Security is disabled.

To find them: in your project dashboard, click the gear icon (Project Settings) in the left sidebar, then **API**. You will see both keys listed under "Project API keys" and the URL under "Project URL".

## Storing Credentials Safely

API keys must never appear in source code. If you commit a key to a public GitHub repository, it can be scraped within minutes by automated bots. The standard practice is to store secrets in a `.env` file that is excluded from version control.

Create a `.env` file in your project directory:

```text
SUPABASE_URL=https://<your-project-id>.supabase.co
SUPABASE_KEY=<your-anon-key>
```

Then add `.env` to your `.gitignore` file:

```text
.env
```

This ensures the file is never committed. The `.env` file is only ever on your local machine.

To load the values from `.env` into your Python script, use `python-dotenv`:

```bash
uv pip install python-dotenv supabase
```

`python-dotenv` reads the file and sets the variables as environment variables, which your script can then read with `os.getenv()`:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env and sets environment variables

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
```

If either value is `None`, you either forgot to create the `.env` file or misspelled the variable name. Double-check both before debugging further.

## Connecting with supabase-py

With your credentials loaded, creating a client is one line:

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
```

The `supabase` object is your entry point for all database operations. It holds the connection details and exposes methods for reading and writing tables.

## Verifying the Connection

The simplest way to confirm that everything is working is to make a request to a table that exists. In the next lesson you will create the `weather_raw` table, but first let's verify the client itself is configured correctly.

In your project dashboard, navigate to the **Table Editor** and create a small test table called `connection_test` with a single column `message` (type: text). Insert one row with the text `"hello"`.

Then run this script:

```python
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

response = supabase.table("connection_test").select("*").execute()
print(response.data)
```

You should see:

```python
[{'id': 1, 'message': 'hello'}]
```

If you get an empty list, the table exists but is empty. If you get an error, check your URL and key in `.env`. Once this works, you can delete the `connection_test` table from the dashboard — it was only for verification.

## A Note on Row Level Security

Supabase enables Row Level Security (RLS) on new tables by default. RLS lets you define fine-grained access policies — for example, "a user can only read their own rows." It is an important production feature, but it adds complexity during development. For this course, you will **disable RLS** on your tables after creating them. The next lesson shows exactly how to do this in the SQL editor.

## Check for Understanding

1. You accidentally commit your `.env` file to a public GitHub repository. What is the immediate risk, and what should you do?

    - A. Nothing — `.env` files are automatically encrypted by Git
    - B. Your API key may be scraped by automated bots; you should rotate the key immediately in the Supabase dashboard
    - C. The file will be ignored because it is listed in `.gitignore`
    - D. The risk is low because API keys only work from the original machine

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. API keys committed to public repositories are frequently harvested within minutes. Rotate the key immediately: in your Supabase dashboard, go to Project Settings → API and generate a new anon key. The old key will stop working.
    </details>

2. You call `os.getenv("SUPABASE_URL")` and get `None`. What are the two most likely causes?

    - A. The environment variable is set correctly; `None` is the expected return value for URL strings
    - B. The `.env` file does not exist in the directory where the script is run, or the variable name in `.env` does not match exactly
    - C. `supabase-py` requires a different method to load environment variables
    - D. The Supabase project is still provisioning

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. <code>os.getenv()</code> returns <code>None</code> when the variable is not set. The two common causes are: the <code>.env</code> file is in a different directory than where you are running the script, or the variable name has a typo (e.g., <code>SUPABASE_url</code> instead of <code>SUPABASE_URL</code>).
    </details>

## Lesson Wrap-Up

Supabase gives you a hosted Postgres database reachable from any Python script. Your project URL and anon key identify and authenticate you; storing them in `.env` keeps them out of source code. The `supabase-py` client wraps all database operations in a clean Python API — you will use it heavily for the rest of the course.

In the next lesson, you will create the two tables that the pipeline will use — `weather_raw` and `weather_enriched` — and learn the full set of read/write operations that `supabase-py` provides.
