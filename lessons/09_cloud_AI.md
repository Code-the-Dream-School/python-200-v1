# Week 9: Data in the Cloud

In Week 8 you learned how cloud platforms work: the IaaS/PaaS/SaaS model, the economics of managed services, and the conceptual difference between compute and storage. This week you put that into practice by writing Python that stores and retrieves data in the cloud.

The service you will use is [Supabase](https://supabase.com) — a hosted Postgres database with a clean Python SDK. By the end of the week you will be able to connect a Python script to a cloud database, design a schema, read and write rows using the supabase-py SDK, and build an Extract + Load pipeline that pulls a year of daily weather data from a public API and upserts it into the cloud. The data you load this week feeds directly into the transform and enrichment steps in weeks 10 and 11.

## Topics

1. [Connecting to Supabase from Python](https://github.com/Code-the-Dream-School/python-200-v1/blob/88c2853c4caaee120b8ac229ab5d8fe78ff92c91/lessons/09_cloud_data/01_connecting_supabase.md)
Python scripts need credentials to talk to a cloud database — but those credentials must never be hardcoded in source code. This lesson introduces Supabase, walks through creating a project and retrieving your credentials, and shows how to store secrets safely using environment variables. You will verify your connection with a simple Python script.

2. [Working with Tables using supabase-py](https://github.com/Code-the-Dream-School/python-200-v1/blob/88c2853c4caaee120b8ac229ab5d8fe78ff92c91/lessons/09_cloud_data/02_supabase_tables.md)
With a connection established, you need somewhere to put data. This lesson introduces the two-table schema for the rest of the course — `weather_raw` for raw API data and `weather_enriched` for ML classifier and LLM output — and walks through the full set of CRUD operations using the supabase-py fluent API. All writes use `upsert` with `on_conflict="date"` so every pipeline run is idempotent.

3. [The Extract + Load Pipeline](https://github.com/Code-the-Dream-School/python-200-v1/blob/88c2853c4caaee120b8ac229ab5d8fe78ff92c91/lessons/09_cloud_data/03_loading_pipeline.md)
Puts it all together: fetch a year of daily weather data from the Open-Meteo historical archive API, shape the records, and upsert them into `weather_raw`. This is the Extract + Load skeleton you will build on in weeks 10 and 11, when the double-transform step is added.

4. (Optional, Recommended) [Practicum AWS Bridge, Part 2: Settings and Secrets](https://github.com/Code-the-Dream-School/python-200-v1/blob/main/lessons/09_cloud_data/04_aws_bridge_secrets.md)
The second of four optional lessons that prepare you for the AWS work in the practicum. It explains where a Lambda function keeps its settings and secrets, introduces AWS Parameter Store and the `boto3` library, and shows how to test AWS code on your own computer with `moto`. This lesson is a pilot this term, and you can skip it without any effect on your grade.

## Week 9 Assignments

Scroll down to see the Coding Assignment instruction and get more hands-on practice with the material. Also, don't forget to take your weekly quiz in AIRHub this week!

