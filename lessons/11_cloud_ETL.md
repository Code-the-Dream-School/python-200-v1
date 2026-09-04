# Week 11: Cloud ETL

You have built all the pieces. In week 4 you packaged a trained weather classifier into a reusable component. In week 9 you extracted weather data from a REST API and loaded it into Supabase. In week 10 you added the double-transform step — the classifier predicted running conditions for each record, an LLM generated a natural-language recommendation, and the enriched output went into `weather_enriched` — and you wrapped that transform into your first Prefect flow. The only thing missing is a single orchestrated flow that runs all four steps (extract, load, transform, enrich) in sequence, reports what happened, and handles failures gracefully.

That is what this week is about. The three lessons take you from a brief Prefect refresher, through wiring the complete pipeline with real cloud tasks, to the production patterns that separate a working prototype from something reliable enough to run on a schedule. By the end, you will have a cloud ETL pipeline you built from scratch — extract, load, transform, orchestrated, and observable.

## Topics

1. [Prefect, Revisited](https://github.com/Code-the-Dream-School/python-200-v1/blob/3fe449c9e0b7eab8a885c1721e004eb581410cbe/lessons/11_cloud_ETL/01_prefect_revisited.md)
A quick bridge from the week 10 Prefect introduction to the full cloud ETL context. Reviews the core concepts (`@task`, `@flow`) from Week 10, introduces the Prefect UI, and shows what changes when your tasks do real cloud I/O instead of local operations. Introduces the four-task skeleton for this week's pipeline: `extract`, `load_raw`, `transform`, and `load_enriched`.

2. [Building the Pipeline](https://github.com/Code-the-Dream-School/python-200-v1/blob/3fe449c9e0b7eab8a885c1721e004eb581410cbe/lessons/11_cloud_ETL/02_build_pipeline.md)
Fills in the skeleton with the real tasks from weeks 9 and 10: extract from Open-Meteo, upsert raw records into `weather_raw`, run the double-transform (ML classifier + LLM enrichment), and write enriched records to `weather_enriched` — all wired together in a single `@flow`. Covers how to run it end-to-end and how to read a successful (and a failed) run in the Prefect UI.

3. [Making Pipelines Production-Ready](https://github.com/Code-the-Dream-School/python-200-v1/blob/3fe449c9e0b7eab8a885c1721e004eb581410cbe/lessons/11_cloud_ETL/03_production_ready.md)
Introduces four patterns that separate a working pipeline from a reliable one: retries for transient failures, `raise_for_status()` for clean error propagation, structured logging, and idempotent writes via `upsert` with `on_conflict` combined with the incremental processing check. Closes with a brief look at what comes next — scheduling, Prefect Cloud, and parameterized deployments.

## Week 11 Assignment

Once you finish the lessons, scroll down to the Coding Assignment instructions below for details on the capstone project.
