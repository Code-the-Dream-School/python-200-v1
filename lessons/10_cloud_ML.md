# Week 10: LLMs in Pipelines

In weeks 5 through 7, you used language models interactively — building chatbots, augmenting them with retrieved knowledge, and wiring them into agents. In week 9, you stored structured weather data in Supabase. This week you connect those two skills, and add a third: the `WeatherClassifier` component you packaged in week 4.

The transform step you build this week is a **double transform**: first the weather classifier predicts whether each day's conditions are good for running, then an LLM generates a short natural-language recommendation explaining why. Both steps read from `weather_raw`; together they write to `weather_enriched`. The conceptual shift is treating both models — the sklearn Pipeline behind the component and the LLM — as data-processing components rather than interactive tools. Then, in the final lesson, you wrap the whole double-transform into a Prefect flow, your first look at the orchestration tool that Week 11 builds on.

## Topics

1. [The Double-Transform Pattern](10_llm_pipelines/01_double_transform.md)
Frames the week conceptually. Covers where ML models and LLMs each belong in an ETL pipeline, what kinds of tasks they do well versus poorly, and how the `WeatherClassifier` component from week 4 plugs into a pipeline. Also covers the prompt-design principles that apply when an LLM is a batch processing step rather than a conversational partner.

2. [ML Inference on Database Records](10_llm_pipelines/02_ml_inference.md)
The hands-on ML step. Reads rows from `weather_raw`, runs them through the `WeatherClassifier` component, and produces labels and confidence scores for each record, handling incremental processing — skipping dates already present in `weather_enriched`. Ends with a set of enrichment records ready to pass to the LLM step.

3. [LLM Enrichment and Writing to weather_enriched](10_llm_pipelines/03_llm_enrichment.md)
The hands-on LLM step. Designs a constrained prompt that receives each day's weather features, ML prediction, and confidence score, calls the OpenAI API, validates the response, and writes complete enrichment records to `weather_enriched`. Closes with a spot-check query to confirm the output looks right.

4. [Orchestrating with Prefect](10_llm_pipelines/04_orchestration.md)
Introduces Prefect, the tool that turns the linear double-transform script into a tracked *flow*. You wrap each step into an `@task` and combine them in a `@flow`. This is the light version — retries, logging, scheduling, and the Prefect UI come in Week 11, which builds directly on this lesson.

## Week 10 Assignments

Once you finish the lessons, scroll down to the coding assignment below to get more hands-on practice with the material.
