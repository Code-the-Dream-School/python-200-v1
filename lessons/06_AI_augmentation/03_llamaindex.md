# RAG Implementation with LlamaIndex

In the previous lesson, you built a retrieval system using keyword matching — exact word overlap between a query and your documents. This lesson introduces semantic RAG, which searches by *meaning* rather than exact words. We will build it using [LlamaIndex](https://www.llamaindex.ai/), a framework that automates the steps a from-scratch implementation would require you to write yourself: loading documents, splitting them into chunks, generating embeddings, and building a searchable index. The workflow is shown in the figure below.

![LlamaIndex Workflow](resources/LlamaIndex.png)

To be clear, all steps in the "RAG Framework" box are performed in LlamaIndex. The green arrows are associated with the process of creating the vector datastore using the data sources (PDFs, text files, knowledge graphs etc.). The steps in the green flow (reading, chunking, embedding, creating the vector store index) and the green "data sources" block can be thought of as elements in the pre-use steps before generating a response to a query. The blue flow (query to embedding, to retrieving context from the vector store index and generating the response from the LLM) can be thought of as the regular steps in the usage of the RAG framework to generate the response to a query. The grey blocks are the internal steps and elements in the RAG framework provided/ performed by LlamaIndex.

LlamaIndex provides a simple API that automates the database reading, chunking, storing, context retrieval and augmentation, and response generation steps. LlamaIndex also includes support for many external data storage libraries, models, and embeddings making it a very versatile tool to develop your own custom RAG frameworks. For example, LlamaIndex supports multiple types of vector storage databases involving FAISS, pgvector and much more (depicted by the different types of vector stores in the dotted box in the figure). Also, the chunking, embedding and storing of the documents in the vector database of choice is all done through one method in LlamaIndex. Additionally, LlamaIndex includes methods to evaluate your RAG framework, which we will go over briefly towards the end of this lesson. The blue blocks in the figure (query, retrieved context, and response) are used in the RAG evaluation process.

<!-- Note the "index" in LlamaIndex refers directly to the same kind of semantic index we built manually in previous lessons. It is a package built around the concept of semantic indexes. 

LlamaIndex is a framework for building LLM-powered agents over your data with LLMs and workflows. It can use RAG pipelines. 

As LLM offers an interface between humans and data. They are pre-trained on huge public data. At the same time, Llamaindex provides us with the facility to build a use case on our own data. That is, context augmentation (eg, RAG), where we make our data available to LLM to solve the problem. 

Here, agents are LLM assistants uses tools to perform a given task, like data extraction or research.
Workflows are multi-step processes that combine one or more agents to create a complex LLM application. 

LlamaIndex can be used to ingest existing data and structured data, has helper functions for API integrations, and can also monitor apps. 

Use cases:
- Question Answering
- Chatbots
- Document Understanding and Data Extraction
- Autonomous Agents -->

Here are some additional resources to look at: [Youtube video on introduction to LlamaIndex](https://www.youtube.com/watch?v=cCyYGYyCka4), [IBM article on LlamaIndex](https://www.ibm.com/think/topics/llamaindex).

## What LlamaIndex Automates

Before writing any code, it helps to understand what LlamaIndex is doing on your behalf.

**Chunking** is the process of splitting a long document into smaller, overlapping pieces. This matters because you rarely want to retrieve an entire document in response to a query — you want the most relevant *section*. LlamaIndex's default chunk size is 1024 tokens with 200 tokens of overlap between adjacent chunks. Chunk size is a tunable parameter: smaller chunks are more precise but may cut off context; larger chunks capture more surrounding text but may retrieve irrelevant content alongside what you need.

**Embeddings** are dense numerical vectors that represent the meaning of a piece of text. An embedding model (in this course, OpenAI's `text-embedding-3-small`) reads a chunk and outputs a list of 1536 numbers. Chunks with similar meanings land near each other in this vector space. This is what allows semantic search to find a relevant chunk about "miles per gallon" in response to a query about "fuel efficiency" — no words overlap, but the embeddings are close. The closeness between two vectors is measured using **cosine similarity**, a number from -1 to 1 where scores near 1 indicate highly similar meaning.

**Indexing** builds a searchable data structure over the chunk embeddings so that, at query time, the nearest chunks can be retrieved quickly. LlamaIndex's `VectorStoreIndex` handles chunking, embedding, and indexing automatically when you call `VectorStoreIndex.from_documents(docs)`. You can swap in a different vector store backend (including a persistent PostgreSQL database via pgvector — covered in the optional extension at the end of this lesson) without changing how you query.

> **Note:** Install the following packages before running the code in this lesson:
> ```bash
> pip install "llama-index-core==0.14.10" llama-index-embeddings-openai llama-index-llms-openai llama-index-readers-file pypdf python-dotenv
> ```
> The optional pgvector extension at the end of this lesson requires two additional packages (`llama-index-vector-stores-postgres` and `psycopg2-binary`) and Docker. You do not need them for the main lesson.

We will use the same Brightleaf Solar Company example from the previous lessons. LlamaIndex's internal similarity search handles retrieval — no separate vector library required.

## In-memory Semantic RAG using LlamaIndex

As we have done for previous lessons, we will load the OpenAI API key from .env file and print `success` if it is loaded.

```python
from dotenv import load_dotenv

if load_dotenv():
    print("success")
else:
    print("oops")
```

Once the API key is loaded, we will load the Brightleaf company documents into LlamaIndex's storage index. 

<!-- Basically what we've been building toward can now be done in four lines of code:

    docs = SimpleDirectoryReader("brightleaf_pdfs").load_data()
    index = VectorStoreIndex.from_documents(docs)
    query_engine = index.as_query_engine()
    response = query_engine.query("What is BrightLeaf Solar's mission?")

This replaces almost everything we built manually in Step 2 with a framework-focused solution that handles things for you. We'll walk through these code steps below, but stripped of all the explanatory padding, it really is that simple! -->

### Read, Chunk, and Store Documents

LlamaIndex provides a default storage index called `VectorStoreIndex` to store the chunked and embedded text from the documents. The following code shows how to create the vector store index for the brightleaf documents. The code first sets the embedding model to `text-embedding-3-small`, which is the model this course uses. If you do not set it, LlamaIndex uses its own default model, `text-embedding-ada-002`.

```python
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding

# Use the same embedding model as the rest of the course
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Load documents directly from PDFs in the folder
docs = SimpleDirectoryReader("brightleaf_pdfs").load_data()

# Build a vector index automatically (handles chunking + embeddings)
index = VectorStoreIndex.from_documents(docs)
```

> **Note**: Make sure the `brightleaf_pdfs` directory is in the appropriate location, you can additionally add an `assert` statement to check the existence of the directory if it is located elsewhere.

The last two lines of code capture the document reading, chunking, embedding, and storing steps. LlamaIndex uses the inbuilt `SimpleDirectoryReader` method to read the documents and store the metadata and text into the `docs` list (the "Read" block in the figure at the start of the lesson).  

<!-- Document: LlamaIndex’s core data structure that represents one source file (like a PDF) after it’s loaded.
id_: A unique identifier automatically assigned to each document.
embedding: A numerical vector representation of the document used for semantic search; None means it hasn’t been created yet.
metadata: Descriptive information about the file (name, path, type, size, dates) used for filtering and source tracking.
excluded_embed_metadata_keys: Metadata fields that are ignored when generating embeddings to keep them semantically meaningful.
excluded_llm_metadata_keys: Metadata fields hidden from the LLM to avoid unnecessary or irrelevant context.
text_resource: The container holding the extracted text from the PDF.
MediaResource: An internal wrapper used by LlamaIndex to manage different content types (text, image, audio, video).
content / text: The raw extracted data from the PDF; in this case it shows PDF internals rather than cleaned text.
file_path / file_name / file_type: Identify where the document came from and what format it is.
Vector embeddings (later step): Used to compare documents and queries based on meaning rather than keywords. 

```python
type(docs[0])
```
    llama_index.core.schema.Document

```python
len(docs)
```
    6

Look at docs[0]: Fill this in some, don't print entire thing, look at a few attributes:

```python
docs[0].doc_id, docs[0].text[:500]
```
    ('8190b231-abe2-45d8-a2cc-05dec4840041',
     '%PDF-1.4\n% ReportLab Generated PDF document http://www.reportlab.com\n1 0 obj\n<<\n/F1 2 0 R /F2 3 0 R /F3 4 0 R /F4 5 0 R\n>>\nendobj\n2 0 obj\n<<\n/BaseFont /Helvetica /Encoding /WinAnsiEncoding /Name /F1 /Subtype /Type1 /Type /Font\n>>\nendobj\n3 0 obj\n<<\n/BaseFont /Helvetica-BoldOblique /Encoding /WinAnsiEncoding /Name /F2 /Subtype /Type1 /Type /Font\n>>\nendobj\n4 0 obj\n<<\n/BaseFont /ZapfDingbats /Name /F3 /Subtype /Type1 /Type /Font\n>>\nendobj\n5 0 obj\n<<\n/BaseFont /Helvetica-Bold /Encoding /WinAnsiEncodi') -->

Once the documents are read, the next step is to chunk the text, convert them into embeddings, and store them. `VectorStoreIndex` automatically handles the chunking, embedding and storing of the documents (the steps in the dashed box in the figure at the start of the lesson). By default, LlamaIndex stores the embeddings in a `SimpleVectorStore` object. You can check this by running the following code. Note that because we directly create the `VectorStoreIndex` from the documents, there is no need for the "Storage Context" here. We will see the usage of "Storage Context" with the persistent database semantic RAG implementation later.

```python
print(type(index._vector_store).__name__)
```
The output should say the following.

    SimpleVectorStore

Now that we have the text chunked, embedded and stored, the next step is to retrieve the relevant context based on the user query, augment it to the query and generate the response from the LLM.

<!-- ### Create index
Here we're using OpenAI for embeddings and llamaindex's default fallback vector store `SimpleVectorStore` for our vector store. When we used FAISS previously, we manually created a vector index and handled the similarity search ourselves. LlamaIndex takes care of that for us. By default, it uses a small in-memory vector store called SimpleVectorStore. You can think of this as a lightweight, Python-based version of FAISS: it stores each chunk’s embedding and performs similarity search under the hood. It isn't meant for large production systems, but is great for learning the basic RAG workflow because there’s nothing to install or configure. Later, when we want a real database-backed vector store (like pgvector), we'll need to swap out this default back end. 

```python
# Build a vector index automatically (handles chunking + embeddings)
index = VectorStoreIndex.from_documents(docs)
```

```python
# dir(index)
```
-->

### Retrieve Context, Augment, and Generate Response - The Query Engine
LlamaIndex uses a helper object called a "query engine" that wraps the entire context retrieval, augmentation, and response generation process. This contributes to further reduction in lines of code. In this sense, the query engine encompasses the "Retrieved Context," "LLM," and "Response" blocks in the figure at the start of the lesson.

LlamaIndex uses OpenAI's "gpt-3.5-turbo" model in the backend by default to generate the response to the user query. 
    
Below, we create the query engine from the vector store index and look at the responses and the retrieved contexts to three sample questions.

```python
query_engine = index.as_query_engine(similarity_top_k=3)

questions = [
    "What is BrightLeaf Solar's mission?",
    "How did profits change between 2023 and 2024?",
    "Which partner joined most recently?"
]

for q in questions:
    print(f"\nQ: {q}")
    response = query_engine.query(q)
    print("A:", response)
    
    for node_with_score in response.source_nodes:
        print(f"Node ID: {node_with_score.node.node_id}")
        print(f"Similarity Score: {node_with_score.score:.4f}")
        print(f"Text Snippet: {node_with_score.node.get_content()[:100]}...")
        print("-" * 30)
```

When creating the query engine, we define the number of retrieved chunks by setting `similarity_top_k=3`. The vector store index query engine uses cosine similarity to search through the embeddngs to obtain the most relevant chunks. We can also look at the most relevant chunks and their corresponding similarity scores through the `response` object's `source_nodes`. The output will look like the following (minus the HTTP requests).


    Q: What is BrightLeaf Solar's mission?
    A: BrightLeaf Solar's mission is to make solar power practical, affordable, and accessible to communities that have historically been left behind in the transition to clean energy. They aim to be educators, partners, and advocates for a more resilient and equitable power grid, with each installation representing an investment in long-term community well-being.
    Node ID: 6db23967-7cb2-49a8-9814-6d381ce5b69e
    Similarity Score: 0.9034
    Text Snippet: Overview
    BrightLeaf Solar was founded on the belief that renewable energy should be a right, not a p...
    ------------------------------
    Node ID: b6833bf4-3fea-487c-9843-6b52be02bedb
    Similarity Score: 0.8534
    Text Snippet: EcoVolt Energy (2022 Partnership)
    BrightLeaf's collaboration with EcoVolt Energy, established in 202...
    ------------------------------
    Node ID: 566668b4-d22b-49df-b166-1932fd899d92
    Similarity Score: 0.8440
    Text Snippet: Overview
    This report summarizes BrightLeaf Solar's financial performance from 2021 through 2025. The...
    ------------------------------

    Q: How did profits change between 2023 and 2024?
    A: Profits increased from 0.5 million USD in 2023 to 1.1 million USD in 2024.
    Node ID: 566668b4-d22b-49df-b166-1932fd899d92
    Similarity Score: 0.7936
    Text Snippet: Overview
    This report summarizes BrightLeaf Solar's financial performance from 2021 through 2025. The...
    ------------------------------
    Node ID: 6db23967-7cb2-49a8-9814-6d381ce5b69e
    Similarity Score: 0.7257
    Text Snippet: Overview
    BrightLeaf Solar was founded on the belief that renewable energy should be a right, not a p...
    ------------------------------
    Node ID: b6833bf4-3fea-487c-9843-6b52be02bedb
    Similarity Score: 0.7239
    Text Snippet: EcoVolt Energy (2022 Partnership)
    BrightLeaf's collaboration with EcoVolt Energy, established in 202...
    ------------------------------

    Q: Which partner joined most recently?
    A: SunSpan Microgrids joined most recently.
    Node ID: b6833bf4-3fea-487c-9843-6b52be02bedb
    Similarity Score: 0.7601
    Text Snippet: EcoVolt Energy (2022 Partnership)
    BrightLeaf's collaboration with EcoVolt Energy, established in 202...
    ------------------------------
    Node ID: 566668b4-d22b-49df-b166-1932fd899d92
    Similarity Score: 0.7209
    Text Snippet: Overview
    This report summarizes BrightLeaf Solar's financial performance from 2021 through 2025. The...
    ------------------------------
    Node ID: 6db23967-7cb2-49a8-9814-6d381ce5b69e
    Similarity Score: 0.7166
    Text Snippet: Overview
    BrightLeaf Solar was founded on the belief that renewable energy should be a right, not a p...
    ------------------------------

Since we only want to augment the top 3 most relevant chunks, the response will only have 3 source nodes. As can be seen, the model is able to respond accurately and retrieve generally relevant chunks to each question.

Congratulations! You've implemented a semantic RAG pipeline using LlamaIndex in four lines of code.

What makes this so powerful is how much work is wrapped into so little code. LlamaIndex is a fully maintained, widely used framework that bundles chunking, embedding, vector storage, retrieval, ranking, and context injection into a clean and consistent interface. Changing defaults (chunk size, embedding model, `similarity_top_k`) will add a few lines, but the overall reduction compared to a from-scratch implementation remains significant.

LlamaIndex includes built-in tools for evaluating how well a RAG system is performing — we will look at those next. An optional extension at the end of this lesson covers swapping the in-memory store for a persistent PostgreSQL database using pgvector.

## Optional Extension: Persistent Vector Store with pgvector

> **Prerequisites:** This section requires Docker installed and running on your machine, plus two additional packages:
> ```bash
> pip install llama-index-vector-stores-postgres psycopg2-binary
> ```
> **You set up the database container yourself.** This lesson does not include setup instructions for Docker or for the PostgreSQL + pgvector container. You need a running PostgreSQL server with the pgvector extension, reachable at `localhost:5432`. These resources explain how to set one up:
> - [Docker: Get started](https://docs.docker.com/get-started/) explains how to install Docker and run a container.
> - The [pgvector README](https://github.com/pgvector/pgvector#docker) and the [`pgvector/pgvector` image on Docker Hub](https://hub.docker.com/r/pgvector/pgvector) explain how to run PostgreSQL with pgvector in Docker.
>
> When you start the container, choose a database name, user, and password. Then put the same values in the connection settings below.
>
> If you do not have Docker, skip this section. The main lesson (in-memory RAG and evaluation) is complete without it. The assignment's Extension C covers this same material.

The in-memory `SimpleVectorStore` used above disappears when your script stops — every restart requires re-embedding all documents from scratch. A persistent database solves this: embeddings are stored once and reused across sessions. This section walks through replacing `SimpleVectorStore` with a PostgreSQL database backed by pgvector, using the same LlamaIndex interface you already know.

LlamaIndex provides support to work with persistent databases using pgvector and PostgreSQL through the `llama-index-vector-stores-postgres` package. LlamaIndex creates and manages its own table in the database. Before starting, make sure your Postgres + pgvector Docker container is running and reachable at `localhost:5432`.

<!-- This notebook is the "framework sequel" to the earlier RAG notebooks:

- Hand-rolled semantic RAG (FAISS)
- Hand-rolled Postgres + pgvector RAG (Docker)
- Framework RAG with LlamaIndex + SimpleVectorStore (SVS)

Here we use **LlamaIndex + pgvector** while reusing the **same Postgres server/container** you already set up.

## Key idea

- We reuse the same Postgres database **server**.
- We **do not reuse** the hand-rolled table schema (e.g., `rag_chunks`).
- Instead, LlamaIndex manages its own table (e.g., `li_brightleaf_pgvector`) to store nodes + embeddings.

## Prereqs

1. Your Postgres + pgvector container is running and reachable at `localhost:5432`.
2. You have PDFs in `brightleaf_pdfs/` (same as the previous notebooks).
3. Your OpenAI key is set:

```bash
export OPENAI_API_KEY="..."
```

(Or set it in the notebook environment.)

Make sure the following are installed in your virtual environment

    llama-index llama-index-vector-stores-postgres llama-index-embeddings-openai psycopg2-binary
-->

We first define some variables associated with the docker container, table name, and embedding model.

```python
# Connection + indexing configuration
# Update these to match your own PostgreSQL + pgvector container.

PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "ctd_rag"
PG_USER = "ctd"
PG_PASSWORD = "ctdpassword"

# LlamaIndex will manage this table.
# PGVectorStore adds the prefix "data_", so the table in Postgres is named "data_li_brightleaf_pgvector".
LI_TABLE_NAME = "li_brightleaf_pgvector"

# Embedding model choice must match embed_dim.
EMBED_MODEL_NAME = "text-embedding-3-small"
EMBED_DIM = 1536

PDF_DIR = "brightleaf_pdfs"

# If you rerun "build" repeatedly, you will insert duplicates.
# Recommended: build once, then use the query-only section below.
BUILD_INDEX = True
```

### Connect with docker container

Before we let LlamaIndex modify the contents of the docker container, we first check to make sure the container is reachable using the `psycopg2` library.

```python
import psycopg2

conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    dbname=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
)
cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone()[0])
cur.close()
conn.close()
```

Assuming that the connection is successful, you should get the following output.

    PostgreSQL 15.4 (Debian 15.4-2.pgdg120+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit

Once the connection is established, we go ahead with building the PostgreSQL table in the docker container using LlamaIndex.

### Build the database table (for the first run)

Since this is the first time using LlamaIndex to create the database table, we will read, chunk, and embed the documents before storing them in the PostgreSQL table in the docker container via LlamaIndex. For this, we first setup our OpenAI client using the loaded API key. 

```python
import os
from dotenv import load_dotenv
from openai import OpenAI
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.postgres import PGVectorStore

# Load .env (expects OPENAI_API_KEY)
if load_dotenv():
    print("Loaded openai api key")
else:
    print("no api key loaded check out .env")
    
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```
Following a successful extraction of the OpenAI API key, the output should be the following

    Loaded openai api key

We set the embedding model in the `Settings` object, as we did for the in-memory index. This model must match `EMBED_DIM`. Then we use the `SimpleDirectoryReader` as before to read our documents. 
```python
Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL_NAME)

docs = SimpleDirectoryReader(PDF_DIR).load_data()
print(f"Loaded {len(docs)} documents from: {PDF_DIR}")
```
The successful output looks as follows (minus any user warnings):

    Loaded 6 documents from: brightleaf_pdfs

Unlike the previous implementation where we used a `SimpleVectorStore` to store our embeddings in memory, now we use a `PGVectorStore` to connect to the docker container, build the postgreSQL table, and retrieve the relevant chunks using pgvector.

```python 
vector_store = PGVectorStore.from_params(
    host=PG_HOST,
    port=PG_PORT,
    database=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
    table_name=LI_TABLE_NAME,
    embed_dim=EMBED_DIM,
)
```
In the previous implementation with `SimpleVectorStore`, LlamaIndex used default in-memory storage behind the scenes, so we could build the `VectorStoreIndex` index without thinking about storage. In this pgvector version, we want the embeddings database to be the PostgreSQL table instead of local RAM, so we create the `PGVectorStore` and pass it to the `VectorStoreIndex` via a `StorageContext`. In this case, the `PGVectorStore` initialization handles the steps in the dashed block in the figure at the start of the lesson.

```python
if BUILD_INDEX:
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)
    print(f"Indexed documents into Postgres table: {LI_TABLE_NAME}")
else:
    print("BUILD_INDEX is False; skipping indexing.")
```
When building the index for the first time (`BUILD_INDEX=True`), the output will look like the following:

    Indexed documents into Postgres table: li_brightleaf_pgvector

The code prints the value of `LI_TABLE_NAME`. Inside PostgreSQL, `PGVectorStore` adds the prefix `data_` to this name, so the actual table is named `data_li_brightleaf_pgvector`.

As seen in the image at the beginning of the lesson, the storage context is able to interface with any type of vector store to create the vector store index. You can think of `StorageContext` as the wiring step that tells LlamaIndex, "store and search embeddings in the PostgreSQL table." It basically acts like an abstraction layer that allows the `VectorStoreIndex` to be built from different kinds of vector stores (such as `PGVectorStore`). Thus, the "Storage Context" arrow goes from the dotted block with all different types of vector stores to "Vector Store Index" in the figure at the start of the lesson. After this, the rest of the workflow is the same as the previous implementation: LlamaIndex chunks the documents into nodes (LlamaIndex uses the word "node" for a chunk), embeds them, stores them, and later embeds the user query to retrieve the top-k most relevant nodes for the LLM.

Once we have the index constructed, we can build the query engine.

### Build the query engine and generate response

Recall that once the Postgres table is added to the docker container, you do not need to read, chunk, and embed the documents again. When building the table for the first run, the vector index is already build so it can be directly used to create the query engine with `similarity_top_k=3`. 

```python
# Query (works immediately after build)
from llama_index.core import VectorStoreIndex

# If you just built the index above, you already have `index` in memory.
# If not, attach to the existing Postgres-backed vector store.
if "index" not in globals():
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

qe = index.as_query_engine(similarity_top_k=3)
```
In subsequent runs (make sure to set `BUILD_INDEX=False` to avoid duplicate table entries), since the table is already present in the docker container all you need to do is to create the `PGVectorStore` object with the parameters required to connect to the postgres table and create the vector index from it. This is done using the `from_vector_store()` method instead of the `from_documents()` method used before. Note that we don't need to provide a storage context here as it is inferred from the vector store itself.

Now we test the pgvector based query engine with a question and observe the response and retrieved nodes (or chunks) with their similarity scores. Note that, like the `SimpleVectorStore`, `PGVectorStore` also uses cosine similarity by default. 

```python
question = "When did BrightLeaf partner with SunSpan and what did they focus on?"
response = qe.query(question)

print("Q:", question)
print()
print(response)
for node_with_score in response.source_nodes:
    print(f"Node ID: {node_with_score.node.node_id}")
    print(f"Similarity Score: {node_with_score.score:.4f}")
    print(f"Text Snippet: {node_with_score.node.get_content()[:100]}...")
    print("-" * 30)
```

The output should look something like so:

    Q: When did BrightLeaf partner with SunSpan and what did they focus on?

    BrightLeaf partnered with SunSpan Microgrids in 2025. Their partnership focused on developing hybrid renewable infrastructure for the Midwest, targeting legacy industrial zones in Ohio and Michigan. The collaboration involved pairing solar and wind power systems with SunSpan's real-time grid analytics, resulting in improved grid stability and lower emissions at the first hybrid sites. Additionally, SunSpan and BrightLeaf co-authored a white paper on the economic benefits of decarbonizing regional manufacturing supply chains.
    Node ID: 1d116f12-c67e-4538-a6dc-d77fda8dab6a
    Similarity Score: 0.7224
    Text Snippet: EcoVolt Energy (2022 Partnership)
    BrightLeaf's collaboration with EcoVolt Energy, established in 202...
    ------------------------------
    Node ID: d60981ba-879a-4760-a3f2-74f0d858299c
    Similarity Score: 0.6353
    Text Snippet: Overview
    BrightLeaf Solar was founded on the belief that renewable energy should be a right, not a p...
    ------------------------------
    Node ID: 64657f51-466d-4ba5-b9dc-b599a8b14c8c
    Similarity Score: 0.5912
    Text Snippet: Overview
    This report summarizes BrightLeaf Solar's financial performance from 2021 through 2025. The...
    ------------------------------

The response is comprehensive and accurate with the retrieved nodes (chunks) also bearing high relevance to the query and high similarity scores.

That's it! We've set up the system to build and query the pgvector store! Let's test it out without the table creation steps.

### Query-only pattern (for later runs)
Once you have built the database table, it will remain there even if you restart your jupyter kernel or stop your docker container connection (i.e. it is a "persistent" database). For later runs, you don't need to recreate this database. You can simply run the following code that creates the `PGVectorStore` with the database connection parameters, creates the `VectorStoreIndex` from it, converts it to a query engine and answers a user query. To test this properly, clear all outputs and restart the kernel (assuming a jupyter notebook), stop running the docker container, then restart it and try running the following code. 

```python
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.postgres import PGVectorStore

Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL_NAME)

vector_store_q = PGVectorStore.from_params(
    host=PG_HOST,
    port=PG_PORT,
    database=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
    table_name=LI_TABLE_NAME,
    embed_dim=EMBED_DIM,
)

index_q = VectorStoreIndex.from_vector_store(vector_store=vector_store_q)
qe_q = index_q.as_query_engine(similarity_top_k=3)

question2 = "Which partner joined most recently?"
response2 = qe_q.query(question2)

print("Q:", question2)
print()
print(response2)
for node_with_score in response2.source_nodes:
    print(f"Node ID: {node_with_score.node.node_id}")
    print(f"Similarity Score: {node_with_score.score:.4f}")
    print(f"Text Snippet: {node_with_score.node.get_content()[:100]}...")
    print("-" * 30)
```

Assuming the table exists and connection to the docker container was successful, the output should look something like this:

    Q: Which partner joined most recently?

    SunSpan Microgrids joined most recently.
    Node ID: 1d116f12-c67e-4538-a6dc-d77fda8dab6a
    Similarity Score: 0.3178
    Text Snippet: EcoVolt Energy (2022 Partnership)
    BrightLeaf's collaboration with EcoVolt Energy, established in 202...
    ------------------------------
    Node ID: 1aaa91d0-193d-4bb4-84a9-d559e1ef9aa6
    Similarity Score: 0.2184
    Text Snippet: Introduction
    BrightLeaf Solar views employee well-being as inseparable from long-term innovation. Ou...
    ------------------------------
    Node ID: 64657f51-466d-4ba5-b9dc-b599a8b14c8c
    Similarity Score: 0.1899
    Text Snippet: Overview
    This report summarizes BrightLeaf Solar's financial performance from 2021 through 2025. The...
    ------------------------------

The answer is correct but interestingly the similarity scores for the top 3 most relevant chunks is relatively low. This can be because of the relative brevity of the question. However, the chunks do seem relevant to the query.

Congratulations! You have now created a semantic RAG framework that leverages a persistent database using LlamaIndex. As with the in-memory semantic RAG framework, the creation of the postgres table and using it to generate a response to a query was achieved with much fewer lines of code compared to the custom implementation. The number of lines reduces even further after the table is already populated. This is why LlamaIndex is so helpful in creating custom RAG frameworks quickly.

### Extra Utilities and Common Issues

Here are a few optional code snippets that address certain utilitarian needs. You are not required to run these code snippets but they are useful to know.

#### For in-memory semantic RAG
Each element of the `docs` list (which is the output of the `SimpleDirectoryReader` method) is a `Document` object containing the metadata and text for each loaded document. To make sure the text has been read correctly, you can check the metadata and text for each document. For example, to check the first document's metadata you can run the following code.

```python
print(docs[0].metadata)
```
The output should look something like this.

    {'page_label': '1',
    'file_name': 'earnings_report.pdf',
    'file_path': 'c:\\Users\\rosha\\Downloads\\CTD RAG\\rag\\brightleaf_pdfs\\earnings_report.pdf',
    'file_type': 'application/pdf',
    'file_size': 3658,
    'creation_date': '2025-10-22',
    'last_modified_date': '2025-11-10'}

Now, to make sure the text from the "earnings_report" document (or whichever document was read first) has been read correctly you can check the first 100 characters of the text by running the following code.
```python
print(docs[0].text_resource.text[:100])
```
The output should look something like this.

    "Overview\nThis report summarizes BrightLeaf Solar's financial performance from 2021 through 2025. The"

If there is a reading error (usually due to the document not being in the UTF-8 encoding format), the text will have some random symbols that do not resemble the english language.

LlamaIndex uses predefined defaults for the chunking parameters and the embedding model. If you do not set an embedding model, LlamaIndex uses OpenAI's `text-embedding-ada-002` model. Earlier in this lesson, we set the embedding model to `text-embedding-3-small`. You can change these values before creating the vector store index to make sure LlamaIndex uses your custom values. To check the current values, you can run the following code.

```python
from llama_index.core import Settings

print(f"Chunk size:  {Settings.chunk_size}")
print(f"Chunk overlap: {Settings.chunk_overlap}")
print(f"Embedding model: {Settings.embed_model.model_name}")
```
If you ran the earlier code that sets the embedding model, the output should be the following.

    Chunk size:  1024
    Chunk overlap: 200
    Embedding model: text-embedding-3-small

If you did not set the embedding model, the last line shows `text-embedding-ada-002` instead.

To change the chunking parameters and the embedding model, you can do the following.
```python
## Optional: Change default chunking parameters and embedding model (Run before creating vector store index)
from llama_index.embeddings.openai import OpenAIEmbedding

# Specify the new model
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Specify the new chunking parameters
Settings.chunk_size = 512
Settings.chunk_overlap = 50
```

You can check the response model by running the following code.

```python
#check LLM model currently being used
print(f"LLM model: {Settings.llm.model}")
```
As mentioned earlier, the output should be the following.

    LLM model: gpt-3.5-turbo    


#### For persistent database semantic RAG
The code below displays the list of tables in your docker container.

```python
# Optional: List tables

import psycopg2

list_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"

conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    dbname=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
)
conn.autocommit = True
cur = conn.cursor()
cur.execute(list_sql)
tables = cur.fetchall()

cur.close()
conn.close()

print(f"Listed tables: {tables}")
```

Recall that you're using pgvector to explicitly communicate with PostgreSQL in the docker container through SQL commands. The `list_sql` command is basically an SQL command to output the list of table names. If the database contains only the table that LlamaIndex built, the output should be the following:

    Listed tables: [('data_li_brightleaf_pgvector',)]

If you ran the build step more than once, the `data_li_brightleaf_pgvector` table contains duplicate rows. To start over, you can drop the whole table with the following code and then build the index again.

```python
# Optional reset: drop the LlamaIndex-managed table so you can rebuild cleanly
# This is useful for teaching and demos.

import psycopg2

# PGVectorStore stores the data in a table named "data_" + LI_TABLE_NAME
drop_sql = f'DROP TABLE IF EXISTS "data_{LI_TABLE_NAME}";'

conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    dbname=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
)
conn.autocommit = True
cur = conn.cursor()
cur.execute(drop_sql)
cur.close()
conn.close()

print(f"Dropped table (if existed): data_{LI_TABLE_NAME}")
```

Additionally, here are some common issues you may face and how to solve them.
- If you see duplicate retrieval behavior, you probably re-ran the build cell and inserted more nodes.
  Use the reset cell (drop table) and rebuild.

- If you get an embedding dimension mismatch error:
  - Ensure `EMBED_MODEL_NAME` and `EMBED_DIM` agree.
  - For OpenAI `text-embedding-3-small`, `EMBED_DIM = 1536`.

- If you cannot connect to Postgres:
  - Confirm the Docker container is running.
  - Confirm the port mapping is `-p 5432:5432` (or update `PG_PORT`).

## RAG Evaluation using LlamaIndex

So far, we learned how to architect a RAG framework that uses relevant context from an external database, augmented to the query to produce a response from the LLM. But how do we know whether the RAG implementation is working as is intended? How can we measure the efficacy of the RAG framework?

In general, the evaluation of a RAG framework is done by computing certain metrics pertaining to the performance of either the retrieval process or the generation of the response. You can think of these metrics as similar to the accuracy metrics you learned about in the ML lessons, such as the confusion matrix. The biggest difference here is that for RAG frameworks we're trying to assess accuracy in the natural language space as opposed to the numerical or categorical space for ML models. As a result, the evaluation is carried out using an "LLM-as-a-judge" approach, meaning the evaluation metrics are computed using an external LLM (different from the RAG framework). An external LLM (trained appropriately) will be able to assess these subjective metrics faster compared to multiple human experts. LlamaIndex provides support for multiple models including local Ollama models. But in this case, we use OpenAI's gpt-4o-mini as our judge llm.  

Like the ML accuracy metrics, some RAG evaluation metrics will also need a reference/true response for each query. But not all metrics require a ground truth answer. In this exercise, we will look at two such metrics: 
- Relevancy: Metric representing whether the response is relevant to the query using the retrieved contexts, i.e. whether the response is off-topic or rambling. This metric can be used to assess the retrieval step.
- Faithfulness: Metric representing whether the response is faithful to the retrieved contexts, i.e. whether the response contains hallucinations or lying. This metric can be used to assess the generation step.

We use the `FaithfulnessEvaluator` and `RelevancyEvaluator` to compute the faithfulness and relevancy metrics respectively for the given RAG framework (in this case the in-memory semantic RAG framework from earlier). Usually we need a dataset of user queries, responses, and retrieved contexts for each query for the evaluation process. In the following example, we show the computation of both metrics using a single query.

```python
from llama_index.llms.openai import OpenAI
from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator

# Create Judge LLM
llm = OpenAI(model="gpt-4o-mini", temperature=0.2)

# Define evaluator
faithfulness_evaluator = FaithfulnessEvaluator(llm=llm)
relevancy_evaluator = RelevancyEvaluator(llm=llm)

# Get response to query
q = "What is BrightLeaf Solar's mission?"
response = query_engine.query(q)

# Evaluate faithfulness and relevancy
faithfulness_result = faithfulness_evaluator.evaluate_response(query=q, response=response)
print("Faithfulness Evaluation: " + str(faithfulness_result.score))

relevancy_result = relevancy_evaluator.evaluate_response(query=q, response=response)
print("Relevancy Result: " + str(relevancy_result.score))
```
Note that for the relevancy evaluator, we don't need to provide the contexts separately as the response object contains the retrieved nodes. 

To compute a certain evaluation metric, the judge LLM is queried with set prompts based on the evaluation metric and is instructed to output a "YES" or "NO" based on whether the metric is satisfied. If the response if "YES," the corresponding score is 1.0 otherwise it is 0.0. The result objects for both metrics contain the following important attributes: `query`, `contexts`, `response`, `passing`, `score`, and `feedback`. `Feedback` is the response from the judge LLM, `passing` is True if the `feedback` is "YES" and False if "NO."  

The output looks like the following (minus the HTTP requests):

    Faithfulness Evaluation: 1.0
    Relevancy Result: 1.0


Both the faithfulness and relevancy scores are 1.0 implying that the in-memory semantic RAG implementation has passed the evaluation. Ideally, you would have to test your RAG implementation on a large dataset that covers the entire scope of queries in your application using different evaluation metrics. LlamaIndex provides great support to compute the predefined metrics as well as create your own custom metrics based on the goal of your RAG framework. 

Congratulations! In this lesson, you have learned to create both an in-memory and a persistent memory database semantic RAG implementation using LlamaIndex, greatly reducing the lines of code needed to do so. You also learned about RAG evaluation and tested your in-memory semantic RAG implementation on two evaluation metrics. Now you are ready to create your own RAG framework and evaluate it to continue refining it's performance. Here are some additional resources on RAG evaluation to explore: [Huggingface article on RAG evaluation](https://huggingface.co/learn/cookbook/en/rag_evaluation), [LlamaIndex documentation on evaluation](https://developers.llamaindex.ai/python/framework/module_guides/evaluating/), [Youtube video on RAG evaluation](https://www.youtube.com/watch?v=cRz0BWkuwHg). 

Interestingly, there also exist hybrid approaches that use both keyword and semantic search techniques to improve the accuracy of the RAG response in situations where the exact context of a common word is different from its commonly understood meaning. Here's some additional resources to explore this approach if interested: [Hybrid Search article](https://machinelearningplus.com/gen-ai/hybrid-search-vector-keyword-techniques-for-better-rag/), [Postgres vector store documentation in LlamaIndex which includes hybrid search](https://developers.llamaindex.ai/python/examples/vector_stores/postgres/).

Although we covered only naive keyword and semantic RAG in this class, it is important to note that RAG frameworks are a hot topic of research today. As a result, there are many different vairants of RAG being developed continuously. You can learn more in this [Youtube video](https://www.youtube.com/watch?v=tLMViADvSNE).

## Check for Understanding

### Question 1
By default, what similarity metric does the `VectorStoreIndex` created from a `SimpleVectorStore` use to retrieve the relevant contexts to a user query?

Choices:
- A. L2 distance
- B. Cosine similarity
- C. L1 distance
- D. Hamming distance

<details>
<summary> View Answer </summary>
<strong>Answer: B - Cosine similarity</strong>  <br>
By default, the simple vector store uses cosine similarity to find the most relevant chunks to the query.
</details>

### Question 2
What does the faithfulness metric try to address during the evaluation of a RAG framework?

Choices:
- A. Hallucinations
- B. Off-topic ramblings
- C. Response conciseness
- D. Both A and B

<details>
<summary> View Answer </summary>
<strong>Answer: A - Hallucinations</strong>  <br>
The faithfulness metric represents whether the response is faithful to the retrieved contexts (i.e. whether the RAG framework hallucinates). The relevancy metric addresses off-topic rambling responses. Response conciseness is not addressed by any of the predefined metrics.
</details>
