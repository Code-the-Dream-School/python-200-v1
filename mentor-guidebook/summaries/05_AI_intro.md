# Week 5 Mentor Summary: Introduction to AI

**Lesson files:** `lessons/05_AI_intro.md` (overview) and five lessons in `lessons/05_AI_intro/`
**Assignment file:** `assignments/05_AI_intro.md`
**Answer key:** `mentor-guidebook/answer-key/assignment_05_key.md`
**Slides:** `mentor-guidebook/slides/05_ai_llms.pdf`

**Learning objective:** Students learn how large language models (LLMs) work at a conceptual level, and then use them through the OpenAI Chat Completions API. They practice prompt engineering, use the moderation endpoint as a guardrail, and build a job application chatbot that keeps a conversation history. They also discuss the ethical questions that come with AI systems.

**Where this fits:** Weeks 2 and 3 introduced training data, classification, and predicted probabilities. This week reuses PCA from the optional Week 3 lesson to plot embeddings. Week 6 builds on embeddings for semantic search and retrieval-augmented generation (RAG), and Week 7 turns LLMs into agents. In Week 10, the weather pipeline calls `gpt-4o-mini` through the same Chat Completions API to write a short recommendation for each day.

---

## Lesson Overview

Every lesson except the ethics lesson calls the OpenAI API, so students need the OpenAI API key that CTD provides through Slack. Most examples use the model `gpt-4o-mini`.

| Lesson | What students learn |
|---|---|
| **1. Introduction to NLP and LLMs** | A short history of natural language processing (NLP). An LLM predicts the next token, which the lesson calls "autocomplete at scale." Pretraining by self-supervised learning, then fine-tuning (supervised fine-tuning and RLHF). Tokenization, embeddings, attention, and transformer blocks. A demo embeds 15 movie summaries with `text-embedding-3-small` and plots them in 2D with PCA. |
| **2. OpenAI Chat Completions API** | Storing the key in a `.env` file and loading it with `load_dotenv()`. `client.chat.completions.create()` with `model` and `messages`. Reading `response.choices[0].message.content`, `.usage`, and `.model`. The parameters `temperature`, `top_p`, `n`, and `max_tokens`. The free moderation endpoint with `omni-moderation-latest`. A text-to-speech example, abstraction libraries such as litellm, and running `qwen3:0.6b` locally with Ollama. |
| **3. Chatbots** | The API is **stateless**, so a chatbot must resend the whole conversation. A `SalesBot` keeps a `messages` list in a `while` loop and appends each user and assistant message. It limits replies with `max_completion_tokens=300` and stops after 10 exchanges. |
| **4. Prompt Engineering** | A `get_completion()` helper. Clear and specific prompts (role, audience, task, format, and length). Iterating on prompts. Chain-of-thought prompting. Zero-shot, one-shot, and few-shot examples. Delimiters such as triple backticks and XML-style tags. JSON output parsed with `json.loads()` inside `try/except`. Checking a condition before acting, with a fixed fallback such as "No steps provided." |
| **5. Ethics, Bias, and Responsible AI** | The three principles of the Belmont Report, applied to AI. Bias, with the Amazon hiring tool and facial recognition examples. Energy and water use. Misinformation, including deepfakes and hallucinations. Jobs that AI may automate or augment. Five habits for using AI safely. |

---

## Assignment Deliverables

**Setup:** Students work in `assignments_05/` with two files, `warmup_05.py` and `project_05.py`. They store `OPENAI_API_KEY` in a `.env` file and load it with `load_dotenv()` from the `python-dotenv` package. The `.env` file must never be committed. Ollama Question 1 needs Ollama and the `qwen3:0.6b` model, which students install during Lesson 2.

**Grading:** Almost every output comes from a live LLM, so the text differs for every student and every run. Grade the technique and the code structure, not the model's wording. The one deterministic answer is the chain-of-thought salary problem (Prompt Question 4): the final salary is **$102,700**. Some names are exact, because later tasks call them: `get_completion`, `rewrite_bullets`, `generate_cover_letter`, `is_safe`, `"omni-moderation-latest"`, and the JSON keys. The point values in the answer key are a suggested weighting only.

| Part | File | What students do | Concepts practiced |
|---|---|---|---|
| Warmup: API Q1–Q4 | `warmup_05.py` | Make a first call and print the text, model name, and total tokens. Compare temperatures `0`, `0.7`, and `1.5`. Use `n=3`. Cut off a long answer with `max_tokens=15`. | The completions API and its parameters |
| Warmup: System Q1–Q2 | `warmup_05.py` | Compare two `system` personas. Send a prebuilt conversation and explain how the model knows the name "Jordan." | System messages, statelessness |
| Warmup: Prompt Q1–Q6 | `warmup_05.py` | Classify three reviews with zero-shot, one-shot, and few-shot prompts. Solve a salary problem step by step. Return JSON and parse it. Use triple-backtick delimiters. | Prompt engineering |
| Warmup: Ollama Q1 | `warmup_05.py` | Run one prompt with `ollama run qwen3:0.6b` and with the OpenAI API, then compare the two answers. | Local and hosted models |
| Project, Task 1 | `project_05.py` | Use the given `get_completion(messages, ...)` helper. Write a specific system prompt for a job application coach with three required constraints. | System prompts |
| Project, Tasks 2–4 | `project_05.py` | `rewrite_bullets()` returns a JSON list with `"original"` and `"improved"` keys. `generate_cover_letter()` uses at least two few-shot examples. `is_safe()` calls the moderation endpoint. | Delimiters, JSON output, few-shot, moderation |
| Project, Task 5 | `project_05.py` | Complete the `run_chatbot()` loop: run moderation first, route to the bullet and cover letter functions, and keep the chat history. | Conversation memory |
| Project, Task 6 | `project_05.py` | Answer at least two of three ethics questions in a comment block, or link a 2–3 minute video. | Bias, review, guardrails |

**Optional:** Five extensions: a token budget tracker, swapping in Ollama, reading bullets from a `.txt` file, a `"confidence"` field, and a `top_p` experiment. These are marked "(Optional)" and are not graded.

**Submission:** A pull request in the student's `python200-homework` repository. A student who chooses the video for Task 6 pastes the link as a comment at the bottom of `project_05.py`.

---

## Key Concepts

These short explanations cover the ideas students ask about most this week. Expand any one you need.

<details>
<summary><strong>Tokens, embeddings, and next-token prediction</strong></summary>

An LLM generates text one **token** at a time. A token is a piece of text, often a whole word or part of a word. The lesson's example splits "blueberries" into "blue" and "berries." Each token maps to an integer ID. API usage and cost are counted in tokens, which is why `response.usage` reports `prompt_tokens`, `completion_tokens`, and `total_tokens`.

An integer ID carries no meaning, so the model converts each ID into an **embedding**, a long list of numbers. During training, tokens that appear in similar contexts get similar embeddings. Attention then adjusts each embedding based on the rest of the sentence, so "Apple" in a sentence about phones moves toward technology words.

At the end, the model scores every token in its vocabulary, chooses the next token, and repeats. Embedding models also work on whole texts. In the Lesson 1 demo, each movie summary becomes a vector of a little more than 1,500 numbers. PCA reduces each vector to two numbers for the plot.

</details>

<details>
<summary><strong>The API is stateless: the messages list is the memory</strong></summary>

Each call to `client.chat.completions.create()` is independent. The model sees only the `messages` list in that call. Each message is a dictionary with a `role` and `content`. The `system` role sets the assistant's behavior, `user` holds the person's input, and `assistant` holds earlier model replies.

A chatbot "remembers" because the program resends the whole conversation every turn. The pattern has four steps: append the user message, call the API with the full list, print the reply, and append the reply as an `assistant` message. System Question 2 shows this directly. The model knows the name Jordan only because that earlier message is in the list.

The answer key says the most common mistake in Task 5 is forgetting the last step. Without it, the bot loses its memory between turns. Note that a longer history means more prompt tokens on every call, so a long conversation costs more per turn.

</details>

<details>
<summary><strong>Temperature, top_p, n, and max_tokens</strong></summary>

The model produces a probability for every possible next token. These parameters control how it chooses one.

- **`temperature`** controls randomness. At `0`, the model picks the most likely token, so the output is nearly the same on every run. Higher values make less likely tokens more probable. At `1.5`, the answers in API Question 2 can become strange.
- **`top_p`** limits the choice to the smallest set of tokens whose probabilities add up to `p`. In the Lesson 2 quiz, "apple" has probability 0.6. With `top_p=0.6`, "apple" alone fills that set, so the model always chooses it.
- **`n`** returns several completions from one call. Each completion uses its own output tokens.
- **`max_tokens`** stops the reply after a fixed number of tokens. In API Question 4, `max_tokens=15` cuts the answer off in the middle of a sentence. The model does not plan for the limit, so the reply simply stops. For a short, complete answer, ask for one in the prompt as well.

</details>

---

## FAQs and Common Trouble Spots

**1. "The client says I have no API key."**
Check that the `.env` file contains `OPENAI_API_KEY=...` and that `load_dotenv()` runs before `OpenAI()` is created. In the lessons, `load_dotenv()` returns `False` when it cannot find a `.env` file, so printing its return value is a quick test. Also check that `.env` is listed in `.gitignore`. If a key appears in a pull request, flag it, because the key must be rotated.

**2. "Which packages do I install?"**
The packages are `openai` and `python-dotenv`. Lesson 2 calls them "`OpenAI` and `dotenv`," which do not match the install names. The Lesson 1 embedding demo also needs `numpy`, `matplotlib`, and `scikit-learn`.

**3. "`json.loads()` fails on the model's answer."**
The model sometimes adds a sentence before the JSON, such as "Here is the JSON:", or wraps it in a Markdown code block. Add an instruction like "Respond ONLY with valid JSON, no other text." Prompt Question 5 requires a `try/except` that prints the raw response. The student can then read what the model actually returned.

**4. "My chatbot forgets what I said."**
The student is probably not appending the assistant's reply to `messages`. The assignment suggests a temporary `print(len(messages))` after each turn to confirm that the list grows. Then the student can test memory by giving a name in turn 1 and asking for it in turn 3.

**5. "My answers do not match the answer key."**
Differences are expected, because the model output changes on every run, so grade the technique. The exception is Prompt Question 4: $85,000 × 1.12 = $95,200, and $95,200 + $7,500 = $102,700. The phrase "6 months later" does not change the annual salary.

**6. "Ollama is slow, or the answer is poor."**
Students install Ollama from the Ollama website, then run `ollama pull qwen3:0.6b`, a download of about 500 MB. This small model runs on a laptop CPU, but it is much weaker than `gpt-4o-mini`. That difference is useful material for the comparison comment in Ollama Question 1. The rubric accepts the pasted Ollama output as evidence.

**7. "How do I keep my API costs low?"**
Use `gpt-4o-mini`, which the lesson chooses for its low cost, and limit reply length. The course uses two names for that limit: `max_tokens` in the warmup and `max_completion_tokens` in the chatbot code. Both work with `gpt-4o-mini`. The moderation endpoint is free. The optional token tracker extension prints `.usage.total_tokens` after each turn.
