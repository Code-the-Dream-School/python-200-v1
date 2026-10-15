# Week 6 Mentor Summary: Augmenting AI: From Memory to Retrieval

**Lesson files:** `lessons/06_AI_augmentation.md` (overview) and three lessons in `lessons/06_AI_augmentation/`
**Assignment file:** `assignments/06_AI_augmentation.md`
**Answer key:** `mentor-guidebook/answer-key/assignment_06_key.md`
**Slides:** `mentor-guidebook/slides/06_RAG.pdf`

**Learning objective:** Students learn how retrieval-augmented generation (RAG) gives an LLM access to documents it was not trained on. They build a keyword RAG loop from scratch, build a semantic RAG pipeline with LlamaIndex, and score its answers with LlamaIndex's faithfulness and relevancy evaluators. The mini-project is a Q&A assistant for a fictional coffee shop.

**Where this fits:** Week 5 introduced the OpenAI API, prompt engineering, and embeddings with `text-embedding-3-small`, and this week uses all three. Students need the `.env` file with `OPENAI_API_KEY` from Week 5. Week 7 gives LLMs tools to act, and its smolagents lesson presents smolagents as the agent equivalent of LlamaIndex. Week 10 returns to LLMs as a step in a data pipeline. No later assignment reuses the Week 6 code.

---

## Lesson Overview

The lessons use six PDFs for a fictional company, Brightleaf Solar Solutions, stored in `lessons/06_AI_augmentation/resources/brightleaf_pdfs/`.

| Lesson | What students learn |
|---|---|
| **1. Intro to LLM Knowledge Augmentation** | Why LLMs hallucinate and become out of date. Three ways to add knowledge: prompt engineering (put the facts in the prompt), fine-tuning (retrain the model), and RAG (retrieve from an external store at query time). The trade-offs in cost, effort, and how often the data changes. There is no code in this lesson. |
| **2. Keyword-based RAG** | A from-scratch RAG loop with `pypdf` and the OpenAI chat API (`gpt-4o-mini`). The `simple_keyword_retrieval` function removes stopwords and punctuation, counts the words a query shares with each document, and returns the single best whole document. A `use_rag` flag shows the same question answered with and without context. The lesson ends with the method's limits: exact words only, whole documents, and high token use. |
| **3. LlamaIndex** | Chunking (default 1024 tokens with 200 tokens of overlap), embeddings, cosine similarity, and indexing. `SimpleDirectoryReader`, `VectorStoreIndex.from_documents`, and `as_query_engine(similarity_top_k=3)`, with `source_nodes` to inspect the retrieved chunks and scores. Evaluation with `FaithfulnessEvaluator` and `RelevancyEvaluator`, using `gpt-4o-mini` as an "LLM-as-a-judge." An optional section replaces the in-memory store with PostgreSQL and pgvector running in Docker. |

---

## Assignment Deliverables

**Setup:** Students work in `assignments_06/` and need a `.env` file with `OPENAI_API_KEY`. The assignment's install line omits two packages that the code needs (see FAQ 1), so the course `requirements.txt` is the safer install. The Brightleaf PDFs and the Groundwork Coffee documents are in `lessons/06_AI_augmentation/resources/`, and students either copy them or point to them with a relative path. The API cost is very low.

**Grading:** The keyword RAG questions use a fixed function and fixed data, so their results are deterministic. Everything that calls the API varies by run, including LLM answers, similarity scores, and evaluator scores. Students also choose their own queries in several tasks. Grade whether each required print and comment is present and reasoned. One answer-key result is wrong (see FAQ 2).

| Part | File | What students do | Concepts practiced |
|---|---|---|---|
| Warmup, RAG Concepts | `warmup_06.py` | Q1 matches three scenarios to prompt engineering, fine-tuning, or RAG. Q2 explains why a confident wrong answer is harmful. Q3 puts eight RAG pipeline steps in order. | Lesson 1, the RAG pipeline |
| Warmup, Keyword RAG | `warmup_06.py` | Copies `simple_keyword_retrieval` exactly as written and runs it on three coffee-shop queries over four short documents. Q3 asks for a prediction before running. | Stopwords, word overlap, keyword limits |
| Warmup, Semantic RAG Concepts | `warmup_06.py` | Explains embeddings and cosine similarity in their own words, and completes a keyword-versus-semantic comparison table. | Embeddings, chunks, cosine similarity |
| Warmup, LlamaIndex Q1–Q4 | `warmup_06.py` | Builds an in-memory index over the Brightleaf PDFs, prints answers and source-node scores, compares `similarity_top_k=1` with `5`, tries a hard query, and runs both evaluators with `gpt-4o-mini` as the judge. | Query engine, retrieval inspection, evaluation |
| Project, Steps 1–3 | `project_06.py` | Asserts that the Groundwork folder exists, loads the documents with `SimpleDirectoryReader`, builds a `VectorStoreIndex`, and creates a query engine with `similarity_top_k=3`. | LlamaIndex setup |
| Project, Steps 4–5 | `project_06.py` | Runs five given questions in a loop and prints the top source node for each. Then asks a question chosen to fail and prints all three source nodes. | Retrieval quality, hallucination, tone |
| Project, Step 6 | `project_06.py` | Answers three reflection questions: the value of a framework, another use case, and a failure that RAG cannot prevent. | Reflection |

**Optional:** Extension A (keyword and semantic RAG side by side), Extension B (add a new document and rebuild the index), and Extension C (pgvector with Docker). These are marked "(Optional)" and are not graded.

**Submission:** Students commit both files and open a pull request in their `python200-homework` repository. The `.env` file should not be committed.

---

## Key Concepts

These short explanations cover the ideas students ask about most this week. Expand any one you need.

<details>
<summary><strong>Keyword retrieval versus semantic retrieval</strong></summary>

Both methods answer the same question: which stored text is most relevant to this query?

**Keyword retrieval** counts shared words. The lesson's function lowercases the text, removes stopwords and punctuation, and counts the words the query and each document have in common. It cannot connect different words with the same meaning. In Keyword Q3, "How do I sign up for rewards?" scores 0 against the loyalty document, because that document says "Join our loyalty program."

**Semantic retrieval** compares meaning. An embedding model turns each chunk of text into a list of numbers, a vector. Texts with similar meanings get vectors that point in similar directions. Cosine similarity measures that closeness, from -1 to 1. The query is embedded with the same model, and the closest chunks are retrieved. The lesson's example is a query about "fuel efficiency" that finds a chunk about "miles per gallon."

Semantic RAG also retrieves **chunks** instead of whole documents, so it sends fewer tokens to the LLM.

</details>

<details>
<summary><strong>What LlamaIndex does on each call</strong></summary>

Students often ask what the few LlamaIndex lines actually do. There are two phases.

**Build:** `VectorStoreIndex.from_documents(docs)` splits each document into chunks, sends every chunk to the OpenAI embeddings API, and stores the vectors. By default the store is a `SimpleVectorStore` in memory, so it disappears when the script ends. Every run embeds the documents again, which is cheap for these small folders.

**Query:** `query_engine.query(q)` embeds the question, finds the `similarity_top_k` closest chunks, places them in a prompt, and makes a chat call to generate the answer. `response.source_nodes` holds the retrieved chunks and their scores.

The lesson sets `Settings.embed_model` to `text-embedding-3-small`, the same embedding model students used in Week 5. It also explains that LlamaIndex uses `text-embedding-ada-002` if no model is set. The assignment asks students to set `text-embedding-3-small` too, in the warmup and in the project. A student who skips that line gets the older model, which still works. For answers, LlamaIndex uses its default `gpt-3.5-turbo` unless a student changes `Settings.llm`. The optional pgvector section stores the vectors in PostgreSQL, so later runs can query without embedding again.

</details>

<details>
<summary><strong>Faithfulness, relevancy, and LLM-as-a-judge</strong></summary>

A RAG answer is free text, so no single correct string exists to compare against. Instead, a second LLM grades the answer. This is the "LLM-as-a-judge" approach, and the course uses `gpt-4o-mini` as the judge.

- **Faithfulness:** Is the answer supported by the retrieved chunks? A score of 0.0 means the answer contains claims the context does not support. This metric catches hallucination.
- **Relevancy:** Do the answer and the retrieved context address the question that was asked? This metric catches off-topic answers.

Each evaluator asks the judge a YES or NO question, so the score is 1.0 or 0.0. Neither metric needs a reference answer.

A useful point for sessions: an answer can be faithful but not relevant. Suppose the retriever returns the wrong chunks, and the model summarizes them accurately. The answer is faithful to the chunks, but it does not answer the question. In LlamaIndex Q4, students compare both scores on a good query and on a query that the documents do not cover.

</details>

---

## FAQs and Common Trouble Spots

**1. "LlamaIndex fails with an ImportError about `llama-index-llms-openai`," or "my PDF text starts with `%PDF-1.4`."**
The student is missing a package. The query engine and the evaluators need `llama-index-llms-openai`. Without `llama-index-readers-file`, `SimpleDirectoryReader` prints a warning and reads each PDF as raw file content instead of extracting the text. The current install line in the assignment and the lesson includes both packages, but a student who installed from an older copy may not have them. Both are also in the course `requirements.txt`. Install them, or reinstall from that file.

**2. "Keyword Q1 selected `loyalty.txt`, not `hours.txt`. Is my code wrong?"**
No. `loyalty.txt` is the correct result, and the answer key now says so. The word "your" is not in the stopword list, so `hiring.txt` and `loyalty.txt` each match "your," and `hours.txt` matches "weekends." All three score 1. The function breaks ties by sorting tuples in reverse order, so the document name decides, and `loyalty.txt` comes first. This is a good example of how fragile keyword retrieval is: a filler word counts as much as the word that matters.

**3. "Keyword Q3 returned 'No overlapping keywords found.' Did I break the function?"**
No. This is the intended result. "Sign," "up," and "rewards" do not appear in any document, so every score is 0. The comment should connect this result to synonyms, which semantic retrieval handles.

**4. "`SimpleDirectoryReader` says my folder does not exist."**
The PDFs are in `lessons/06_AI_augmentation/resources/brightleaf_pdfs/`. The assignment's example path is only an example, and students must adapt it to where their copy of the folder is. Paths are relative to the folder where the script runs, not to the script file. The rubric says not to fail a submission because its paths differ from the examples.

**5. "In Step 5 the assistant gave a confident answer that was wrong. Is my code broken?"**
Probably not. This is the lesson the step teaches. Ask the student to look at the three source nodes. Did retrieval return the wrong chunks, or was the information missing from the documents? Look for a comment that notices whether the tone changed when the answer was wrong.

**6. "Step 6 Question 1 asks me to compare line counts. What do I compare with?"**
The lessons do not contain a from-scratch semantic RAG implementation, so the question asks students to compare their LlamaIndex code with the keyword RAG code from Lesson 2, or with the code they would need to write each automated step (chunking, embedding, and indexing) themselves. Accept either comparison.

**7. "Do I need Docker?"**
Only for the optional pgvector section and Extension C. Students set up their own PostgreSQL + pgvector container. The lesson and Extension C say this clearly and link to the Docker and pgvector documentation, but they do not give step-by-step setup instructions. Mentors are not expected to support the container setup. Students who skip the extension lose nothing. For students who try it, setting `BUILD_INDEX = True` on every run inserts duplicate rows, as the lesson warns.
