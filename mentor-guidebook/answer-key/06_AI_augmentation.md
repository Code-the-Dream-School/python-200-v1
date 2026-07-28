# Week 6 Assignments

This week's assignments cover the week 6 material, including:

- LLM augmentation: prompt engineering, fine-tuning, and RAG
- Keyword-based RAG
- Semantic RAG concepts: embeddings, chunking, and cosine similarity
- LlamaIndex: building and evaluating a semantic RAG pipeline

As with previous weeks, Part 1 is a set of warmup exercises to practice the core concepts and tools. Part 2 is a mini-project where you will build a complete RAG-powered Q&A assistant from scratch.

Good luck, and enjoy this one. By the end of the project, you will have built a system that retrieves accurate answers from real documents — the kind of work that shows up in job postings right now.

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_06/`. Inside that folder, create two files:

1. `warmup_06.py` — for the warmup exercises
2. `project_06.py` — for the project

When finished, commit your files and open a PR as described in the assignment's [README page](https://github.com/Code-the-Dream-School/python-200/blob/main/assignments/README.md).

It is very helpful for your mentors if you write your thoughts in comments throughout your code. This helps us understand your reasoning and give you better feedback.

# Part 1: Warmup Exercises

Put all warmup exercises in a single file: `warmup_06.py`. Use comments to mark each section and question (e.g. `# --- RAG Concepts ---` and `# Concepts Q1`). Use `print()` to display all outputs.

**Before you start**, make sure the following packages are installed in your virtual environment:

```bash
pip install openai pypdf python-dotenv "llama-index-core==0.14.10" llama-index-embeddings-openai
```

You will also need a `.env` file in the same directory as your script, containing your `OPENAI_API_KEY`. Add the following block at the top of `warmup_06.py` — you will need it for the LlamaIndex section:

```python
from dotenv import load_dotenv
import os

if load_dotenv():
    print("API key loaded successfully.")
else:
    print("Warning: could not load API key. Check your .env file.")
```

---

**Key Terms for This Assignment**

You will encounter the following vocabulary throughout Part 1 and Part 2. Read these before you start.

- **Hallucination** — When an AI model produces information that sounds convincing but is not accurate. The model is not lying intentionally; it is generating text that fits the pattern of the conversation, even if that text is wrong.
- **RAG (Retrieval-Augmented Generation)** — A technique where a system retrieves relevant text from an external document database before generating a response. This grounds the response in real information rather than the model's general training.
- **Retrieval** — The step where the system searches for and selects the most relevant pieces of text to answer a query.
- **Embedding** — A list of numbers (called a vector) that represents the meaning of a piece of text. Texts with similar meanings will have similar embeddings.
- **Chunk** — A small piece of a larger document. Long documents are split into chunks so the system can retrieve only the most relevant sections, rather than the whole document.
- **Cosine similarity** — A number between -1 and 1 that measures how similar two embeddings are. A score close to 1 means the two pieces of text are very similar in meaning.
- **Token** — A unit of text. A token is roughly one word, or part of a word. Language models process text as tokens rather than characters.
- **Stopword** — A very common word (like "the," "and," "of") that is removed before keyword matching because it appears in almost every document and adds little meaning to a search.
- **Vector store / index** — A database that stores embeddings and can quickly find the ones most similar to a given query.

---

## RAG Concepts

### Concepts Question 1

Three teams at a software company are each building a different AI project. Add a comment block to your code that identifies the best approach — **prompt engineering**, **fine-tuning**, or **RAG** — for each scenario, and gives a 1–2 sentence explanation of your reasoning.

**Scenario A**: A legal team wants an assistant that can answer questions about their internal policy library — hundreds of PDFs that are updated every quarter.

**Scenario B**: A startup wants their model to write product copy in a very specific brand voice — a dry, minimalist style that does not appear much online. They have 3,000 examples their in-house writers produced over the years.

**Scenario C**: A data analyst needs to ask an LLM questions about a single two-page report she just received. She does not need this to work for any other document.

### Concepts Question 2

AI hallucinations (responses that sound confident but are wrong) can be particularly difficult to detect. Add a comment to your code answering this:

Why is a *confidently wrong* answer more harmful than one that says "I am not sure"? Give one example of a real situation where a confident hallucination could cause harm.

Think about the *tone* of the response as well as its content — why does the way the model expresses an answer affect how much we trust it?

### Concepts Question 3

The steps below make up a complete RAG pipeline, but they are out of order. Copy the list into your code as a comment, arrange them in the correct order, and add a one-sentence description of what happens at each step.

```python
steps = [
    "Generate a response from the LLM",
    "Extract text from source documents",
    "Receive the user's query",
    "Retrieve the most relevant chunks",
    "Convert text chunks into embeddings",
    "Inject retrieved chunks into the prompt",
    "Split text into chunks",
    "Embed the user's query",
]
```

## Keyword RAG

The following questions use the keyword retrieval function from the lesson. Copy the function below into your `warmup_06.py` — you will call it in the questions that follow.

```python
import string

def simple_keyword_retrieval(query, documents, verbose=True):
    """Keyword retrieval using token overlap scoring."""
    stopwords = {
        "a", "an", "the", "and", "or", "in", "on", "of", "for", "to", "is",
        "are", "was", "were", "by", "with", "at", "from", "that", "this",
        "as", "be", "it", "its", "their", "they", "we", "you", "our"
    }
    translator = str.maketrans("", "", string.punctuation)

    query_words = {
        w.translate(translator)
        for w in query.lower().split()
        if w not in stopwords
    }
    if verbose:
        print(f"\nQuery tokens (filtered): {sorted(query_words)}")

    scores = []
    for name, content in documents.items():
        content_words = {
            w.translate(translator)
            for w in content.lower().split()
            if w not in stopwords
        }
        overlap = query_words & content_words
        score = len(overlap)
        scores.append((score, name, content))
        if verbose:
            print(f"[{name}] overlap={score} -> {sorted(overlap)}")

    scores.sort(reverse=True)
    best = next(((name, content) for score, name, content in scores if score > 0), None)
    if best:
        if verbose:
            print(f"\nSelected best match: {best[0]}")
        return [best]
    else:
        if verbose:
            print("\nNo overlapping keywords found.")
        return [("None found", "No relevant content.")]
```

### Keyword Question 1

Run `simple_keyword_retrieval` with `verbose=True` on the query and documents below. Print the name of the selected document.

```python
query = "What are your hours on weekends?"

documents = {
    "menu.txt": "We serve espresso, lattes, cappuccinos, and cold brew. Pastries include croissants and muffins baked fresh daily. Oat milk and almond milk are available.",
    "hours.txt": "We are open Monday through Friday from 7am to 7pm. On weekends we open at 8am and close at 5pm. We are closed on Thanksgiving and Christmas Day.",
    "hiring.txt": "We are currently hiring baristas and shift supervisors. Send your resume to jobs@groundworkcoffee.com.",
    "loyalty.txt": "Join our loyalty program to earn one point per dollar spent. Redeem 100 points for a free drink of your choice.",
}
```

After running the function, add a comment explaining which document was selected and why.

### Keyword Question 2

Run the same function with this second query using the **same documents** from Q1:

```python
query = "Do you have anything without caffeine?"
```

Add a comment explaining:
- Which document was selected
- Whether keyword RAG got this right — and why or why not
- What kind of retrieval would do better here

### Keyword Question 3

Before running any code, predict which document will be selected for the query below. Write your prediction and your reasoning as a comment first, then run the code to check.

```python
query = "How do I sign up for rewards?"
```

Was your prediction correct? If the result surprised you, add a comment explaining what happened.

## Semantic RAG Concepts

### Semantic Question 1

Add a comment block answering the following in your own words. Try not to just copy the definitions from the lesson — explaining a concept in your own words is a good sign that you have understood it.

1. What is a vector embedding? (1–2 sentences)
2. Two text chunks have cosine similarity scores of 0.85 and 0.30 with a given query. Which chunk is more relevant, and what does that number tell you about the relationship between the texts?
3. Why can semantic search find a relevant chunk even when none of the exact words from the query appear in the chunk?

### Semantic Question 2

Keyword RAG and semantic RAG handle the same problem differently. Copy this table into your code as a comment and fill in the right column:

```
| Feature                    | Keyword RAG                       | Semantic RAG |
|----------------------------|-----------------------------------|--------------|
| What is compared?          | Exact word overlap                | ?            |
| What is retrieved?         | Full document                     | ?            |
| Can it handle synonyms?    | No                                | ?            |
| Storage format             | Plain text dictionary             | ?            |
| Relevance score            | Number of overlapping keywords    | ?            |
```

## LlamaIndex

For this section you will build a small LlamaIndex pipeline using the Brightleaf Solar PDFs from the lesson. These documents should already be familiar from the lesson material.

**Path note**: The `brightleaf_pdfs/` directory is in the lesson folder, not the assignments folder. Point `SimpleDirectoryReader` to it using a path relative to where you run your script — for example:

```python
SimpleDirectoryReader("../../06_AI_augmentation/brightleaf_pdfs")
```

Adjust this path as needed based on your local folder structure.

**API note**: These questions make a small number of calls to the OpenAI embeddings API to build the vector index. The cost is very low (typically less than one cent), but make sure your `.env` file has a valid key before running.

### LlamaIndex Question 1

Build an in-memory LlamaIndex pipeline using the Brightleaf Solar PDFs and run the two queries below. For each query, print:
- The question
- The answer from the model
- For each of the 3 retrieved source nodes: the similarity score and the first 150 characters of the chunk text

```python
questions = [
    "What employee benefits does BrightLeaf offer?",
    "What are BrightLeaf's security policies?",
]
```

Use `similarity_top_k=3`. After printing the results, add a comment for each query answering:
- Do the retrieved chunks look relevant to the question?
- Does the model's response sound confident and specific, or does it hedge with phrases like "based on the context" or "I'm not sure"? Note what you observe about the tone.
- Did anything unexpected get retrieved?

### LlamaIndex Question 2

Re-run one of the queries from Q1 twice: once with `similarity_top_k=1` and once with `similarity_top_k=5`. Print the response and source node scores for both runs.

Add a comment explaining how the response changed (if at all) and whether more retrieved context is always better.

### LlamaIndex Question 3

Try a query you think the pipeline might struggle with — something vague, something that spans multiple documents, or something where the information might not be in the documents at all. Print the response and all retrieved chunks.

Add a comment explaining what you expected, what actually happened, and what you would change about the system to handle this kind of query better.

### LlamaIndex Question 4

Using the same index and query engine you built in Q1, evaluate one response using LlamaIndex's built-in evaluators.

Import and instantiate a `FaithfulnessEvaluator` and a `RelevancyEvaluator`, both using `gpt-4o-mini` as the judge LLM (refer to the "RAG Evaluation using LlamaIndex" section of lesson 4 for the exact import and setup pattern). Run them on this query:

```python
q = "What employee benefits does BrightLeaf offer?"
```

Print both scores. Then run the evaluators again on a query you expect to produce a lower-quality response — for example, a question about something that is clearly not in the Brightleaf documents.

After printing both sets of scores, add a comment block answering:
- What does a faithfulness score of 1.0 mean? What would a score of 0.0 indicate?
- What does a relevancy score measure, and how is it different from faithfulness?
- Did the scores change between your two queries? If so, why do you think that happened?
- What is the "LLM-as-a-judge" approach, and why is it used for RAG evaluation instead of a simple accuracy metric?

---

# Part 2: Mini-Project: Groundwork Coffee Co. Q&A Assistant

Groundwork Coffee Co. is a small, community-focused coffee shop. They have put together a set of documents about their menu, story, hours, loyalty program, and catering services. Your job is to build a RAG-powered assistant that can answer questions about any of those documents accurately.

This is the kind of project you might build in a real job. A business has a folder of internal documents and wants an AI assistant that can answer questions without reading every file manually — and without the AI making things up. By the end of this project, you will have built that system from scratch.

The Groundwork documents are in `lessons/06_AI_augmentation/resources/groundwork_docs` (link [here](https://github.com/Code-the-Dream-School/python-200/tree/a31aa606a13ef99fe2b8359dd3e04407e0452b91/lessons/06_AI_augmentation/resources/groundwork_docs)). Read through them before writing any code. Understanding your data before you start coding will save you time — this is the same principle as the pre-preprocessing step from Week 1.

Place all your code in `assignments_06/project_06.py`.

## Step 1: Setup

Add your imports at the top of the file. Load your API key from `.env` and print a confirmation message. Add an `assert` statement to verify that the `groundwork_docs/` directory exists before your code tries to use it.

An `assert` statement stops the program early with a clear error message if a condition is not met. For example:

```python
from pathlib import Path
docs_dir = Path("assignments_06/resources/groundwork_docs")
assert docs_dir.exists(), f"Document directory not found: {docs_dir}"
```

Adjust the path as needed.

## Step 2: Load the Documents

Load all documents from `groundwork_docs/` using `SimpleDirectoryReader`. Print:
- How many documents were loaded
- The file name of each document

Hint: each `Document` object has a `metadata` dictionary with a `"file_name"` key.

## Step 3: Build the Index and Query Engine

Build a `VectorStoreIndex` from the loaded documents and create a query engine with `similarity_top_k=3`. Print a short confirmation message once the index is ready, such as:

```
Index built successfully. Ready to answer questions.
```

## Step 4: Query the Assistant

Run the five queries below through your query engine. For each one, print:
- The question
- The answer from the model
- The top retrieved source node: document name, similarity score, and the first 200 characters of the chunk text

Use a loop — do not repeat the same code block five times.

```python
questions = [
    "What are Groundwork's hours on weekends?",
    "Do you offer any dairy-free milk options?",
    "How does the loyalty program work?",
    "How did Groundwork Coffee get started?",
    "Do you offer catering or wholesale orders?",
]
```

After running all five queries, add a comment reflecting on the responses: did the assistant sound confident and accurate? Did any of the answers surprise you?

## Step 5: Find a Failure

Ask the assistant a question you expect it to struggle with. Good candidates include: something vague or ambiguous, something that requires combining information from more than one document, or a question where the answer is simply not in the documents.

Print the full response and **all three** retrieved source nodes (document name, similarity score, and first 200 characters of text). Then add a comment explaining:
- What you asked and why you expected it to be hard
- What went wrong — wrong retrieval, missing information, the model guessed anyway?
- When the retrieval failed, did the model's tone change — did it become less certain, or did it still sound confident even when it was wrong? What does this suggest about trusting AI-generated responses?
- What you would change about the system to improve it

## Step 6: Reflection

Add a comment block at the end of `project_06.py` answering the following:

1. The lesson built semantic RAG manually — chunking, embedding, and indexing took many lines of code. How many lines did the equivalent LlamaIndex implementation take in your project? What does that tell you about the value of using a framework?
2. You have now built a system that answers questions from real documents. Describe a different use case — not a coffee shop — where this approach would add genuine value to a business or organization.
3. What is one failure mode that RAG cannot fully prevent, even when retrieval is working correctly?

---

# Optional Extensions

## Extension A: Side-by-Side Comparison (Moderate)

*No new setup required.*

Build a keyword RAG system using the `simple_keyword_retrieval` function from the warmup and run it over the Groundwork documents. Then run the same five project queries through both your keyword RAG system and your LlamaIndex system.

For each query, print both responses side by side and add a comment comparing them:
- Did keyword RAG retrieve the right document?
- How did the quality of the two answers differ?
- Were there any queries where keyword RAG did just as well as semantic RAG? Any where it clearly failed?

To load the Groundwork documents as plain text for the keyword system, you can read the `.txt` files directly:

```python
from pathlib import Path

docs_dir = Path("assignments_06/resources/groundwork_docs")
documents = {f.name: f.read_text() for f in docs_dir.glob("*.txt")}
```

## Extension C: Add a New Document (Low)

*No new setup required.*

Write a new document for Groundwork Coffee Co. and add it to the `groundwork_docs/` folder. It can be anything that fits the company — a seasonal specials update, a job posting, a catering FAQ, or an event announcement. Keep it to one page or less.

Once you have written it, rebuild the LlamaIndex index and verify that your assistant can now answer questions about the new document.

Add a comment explaining:
- What document you added and what information it contains
- What query you used to test it and whether the assistant retrieved the correct content
- Why this demonstrates an advantage of RAG over fine-tuning

## Extension D: Persistent Vector Store with pgvector (Stretch)

*This extension requires Docker to be installed on your computer. If you do not have Docker, skip it — the setup time is significant and is not the focus of this week's learning. If you do have Docker installed, refer to the pgvector setup instructions in the LlamaIndex lesson before starting.*

Replace the in-memory `SimpleVectorStore` in your project with a `PGVectorStore` backed by a PostgreSQL container. This makes your vector database persistent — it will survive a kernel restart and can be queried without re-embedding the documents each time.

The code change itself is small (approximately 20 lines), but you will need:
- Docker running with the pgvector image from the lesson
- The packages `llama-index-vector-stores-postgres` and `psycopg2-binary` installed

Follow the "Persistent database semantic RAG using LlamaIndex" section of the lesson for the full setup pattern. Once it is working, add a comment comparing the experience of using the persistent store vs. the in-memory store:
- What is the main practical advantage of persisting the embeddings?
- In what situation would you definitely want this in a production system?