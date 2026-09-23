# Week 5 Assignments

This week's assignments cover the Week 5 material, including:

- How large language models work (tokenization, embeddings, attention)
- The OpenAI Chat Completions API
- Building a chatbot with conversation memory
- Prompt engineering techniques (zero-shot, one-shot, few-shot, chain-of-thought, structured output, delimiters)
- AI ethics, bias, and responsible use

As always, Part 1 is a set of warmup exercises to get hands-on with the week's tools and concepts. Part 2 is a mini-project that pulls everything together into something genuinely useful.

Good luck, and have fun with it! The best way to build intuition for working with LLMs is to experiment — try breaking the prompts, changing parameters, and seeing what happens. That curiosity is what will make you good at this.

# Submission Instructions

In your `python200-homework` repository, create a folder called `assignments_05/`. Inside it, create two files:

1. `warmup_05.py` — for the warmup exercises
2. `project_05.py` — for the mini-project

When finished, commit and open a PR as described in the [assignments README](https://github.com/Code-the-Dream-School/python-200/blob/e072675df8c08073483cf708d18e28916635a203/assignments/README.md).

**API key reminder**: CTD provided your OpenAI API key via Slack. Store it in a `.env` file at the root of your project — **never commit it to GitHub.** Your `.env` file should look like this:

```
OPENAI_API_KEY=your-key-here
```

Use `load_dotenv()` from the `python-dotenv` package to load it before making any API calls.

---

# Part 1: Warmup Exercises

*Estimated time: ~2 hours*

Put all warmup exercises in `warmup_05.py`. Use comments to mark each section and question (e.g., `# --- Completions API ---` and `# API Q1`). Use `print()` to display all outputs with labels.

---

## The Chat Completions API

*~35 minutes*

### API Question 1

Set up your OpenAI client and make your first chat completion call. Use the model `"gpt-4o-mini"` and send this prompt: `"What is one thing that makes Python a good language for beginners?"`. Print the model's response.

```python
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is one thing that makes Python a good language for beginners?"}]
)
```

Print just the text of the response (not the whole object). Then print the name of the model that responded and the total number of tokens used. Label each output.

### API Question 2

Run the same prompt three times with three different temperature settings: `0`, `0.7`, and `1.5`. Print each response, labeled with its temperature.

```python
prompt = "Suggest a creative name for a data engineering consultancy."
temperatures = [0, 0.7, 1.5]
```

Add a comment in your code answering: *What do you notice about how the outputs differ? Which temperature would you use if you needed a consistent, reproducible output?*

### API Question 3

Use `n=3` with `temperature=1.0` to get three different completions in a single API call. Print all three.

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Give me a one-sentence fun fact about pandas (the animal, not the library)."}],
    n=3,
    temperature=1.0
)
```

Iterate over `response.choices` and print each one.

### API Question 4

Set `max_tokens=15` and send a prompt that would normally produce a long response (for example, `"Explain how neural networks work."`). Print the result. Add a comment: *What happened, and why might you want to use `max_tokens` in a real application?*

---

## System Messages and Personas

*~20 minutes*

### System Question 1

Use a `system` message to give the model a personality, then ask it a question. Print the response.

```python
messages = [
    {"role": "system", "content": "You are a patient, encouraging Python tutor. You always explain things simply and end with a word of encouragement."},
    {"role": "user", "content": "I don't understand what a list comprehension is."}
]
```

Now change the system message to give the model a completely different personality (your choice) and ask the same question. Print that response too. Add a comment noting what changed.

### System Question 2

The completions API is stateless — it has no memory of previous calls. The way to give a model context is to pass the conversation history yourself as a list of messages.

Build the following conversation manually (no loop, no user input — just construct the list) and send it in a single API call:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "My name is Jordan and I'm learning Python."},
    {"role": "assistant", "content": "Nice to meet you, Jordan! Python is a great choice. What would you like to work on?"},
    {"role": "user", "content": "Can you remind me what my name is?"}
]
```

Print the model's response. Add a comment: *Why does the model know Jordan's name, even though it's stateless?*

---

## Prompt Engineering

*~50 minutes*

### Prompt Question 1 — Zero-Shot

Ask the model to classify the sentiment of each review below as `positive`, `negative`, or `mixed`. Give it **no examples** — just the task description and the reviews. Print each result labeled with the review number.

```python
reviews = [
    "The onboarding process was smooth and the team was welcoming.",
    "The software crashes constantly and support never responds.",
    "Great price, but the documentation is nearly impossible to follow."
]
```

### Prompt Question 2 — One-Shot

Repeat the same task, but this time add **one example** before the reviews to show the model the format you want:

```
Example:
Review: "Fast shipping but the item arrived damaged."
Sentiment: mixed
```

Print the results. Add a comment: *Did adding one example change the format or consistency of the output compared to Q1?*

### Prompt Question 3 — Few-Shot

Repeat the task again, this time with **three examples**. At least one example should be positive, one negative, and one mixed. Print the results. Add a comment comparing all three approaches (zero-shot, one-shot, few-shot): *When would you choose each one?*

### Prompt Question 4 — Chain of Thought

Ask the model to solve the following problem, but instruct it to show its reasoning step by step before giving a final answer. Label the final answer clearly.

```
A data engineer earns $85,000 per year. She gets a 12% raise, then 6 months later
takes a new job that pays $7,500 more per year than her post-raise salary.
What is her final annual salary?
```

Print the full response including the reasoning. Add a comment: *Why does asking the model to reason step by step tend to improve accuracy on problems like this?*

### Prompt Question 5 — Structured Output

Ask the model to analyze the review below and return the result **only as valid JSON** with keys `sentiment`, `confidence` (a float from 0 to 1), and `reason` (one sentence). Print the raw response, then parse it with `json.loads()` and print each field separately, labeled.

```python
import json

review = "I've been using this tool for three months. It handles large datasets well, \
but the UI is clunky and the export options are limited."
```

Add a `try/except` block to handle the case where the response is not valid JSON. If it fails, print the raw response so you can debug the prompt.

### Prompt Question 6 — Delimiters

Use **triple backticks** as delimiters to clearly separate the user's text from your instructions. Send the prompt below and print the result.

```python
user_text = "First boil a pot of water. Once boiling, add a handful of salt and the \
pasta. Cook for 8-10 minutes until al dente. Drain and toss with your sauce of choice."

prompt = f"""
You will be given text inside triple backticks.
If it contains step-by-step instructions, rewrite them as a numbered list.
If it does not contain instructions, respond with exactly: "No steps provided."

```{user_text}```
"""
```

Then send a second prompt using a passage that is *not* a set of instructions (any sentence or two of regular prose). Confirm that the model returns `"No steps provided."` Add a comment: *What problem do delimiters help prevent?*

---

## Local Models with Ollama

*~15 minutes*

### Ollama Question 1

In your terminal, run the following prompt using Ollama (you installed it during the lesson):

```bash
ollama run qwen3:0.6b "Explain what a large language model is in two sentences."
```

Then run the same prompt using the OpenAI API in Python (as you've been doing above). Print the OpenAI response.

Paste the Ollama output as a multi-line string comment in your code. Then add another comment answering: *What differences did you notice between the two responses? What is one advantage and one disadvantage of running a model locally?*

---

# Part 2: Mini-Project — Job Application Helper

*Estimated time: ~2.5 hours*

Place your project code in `assignments_05/project_05.py`.

## Background

You've learned to build conversations with LLMs, apply prompt engineering techniques, and use moderation guardrails. In this project, you'll pull all of those skills together to build something immediately useful: an AI-powered job application assistant.

Career changers often struggle with translating experience from a previous field into language that resonates in a new one. This tool will help a user rewrite their resume bullet points, generate a draft cover letter, and ask follow-up questions — all in a single, coherent conversation.

This isn't a toy. With a little polish, the chatbot you build here is something you could actually use.

---

## Task 1: Setup and System Prompt

*~20 minutes*

Load your API key and initialize the client. Then define a `get_completion()` helper function (as seen in the prompt engineering lesson) that takes a `messages` list and returns the model's text response.

Use the helper below as written — keep the function name `get_completion`, since later tasks call it by this name. The parameter defaults (`model`, `temperature`, `max_completion_tokens`) are reasonable starting values you may adjust:

```python
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def get_completion(messages, model="gpt-4o-mini", temperature=0.7):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_completion_tokens=400
    )
    return response.choices[0].message.content
```

Next, write a **system prompt** that sets up the model as a job application coach. Be specific: give it a role, a description of who it's helping, and clear behavioral constraints. At a minimum, your system prompt should instruct the model to:

- Stay focused on job application materials
- Always remind the user to review and edit its output before submitting anywhere
- Acknowledge that it may not know the user's specific industry norms, and that the user should use their own judgment

Add a comment explaining at least one deliberate choice you made in writing the system prompt and why.

**Before you move on — check:** If you print your system prompt and read it aloud, does it sound like a clear briefing for a specific assistant? If it's vague or could apply to almost any task, try adding more specificity. The more concrete your system prompt, the more predictable and useful the model's behavior will be throughout the project.

---

## Task 2: Bullet Point Rewriter

*~35 minutes*

Write a standalone `rewrite_bullets()` function that takes a list of resume bullet points and returns improved versions. This function will later be called from inside the chatbot loop.

Your function should:
1. Use **delimiters** to clearly separate the user's bullet points from your instructions
2. Ask for the output as a **JSON list** where each item has `"original"` and `"improved"` keys
3. Parse the JSON response and print both versions of each bullet side by side

Keep the function name `rewrite_bullets` and the JSON keys `"original"` and `"improved"` exactly as written — the chatbot in Task 5 calls this function, and the printing step depends on those keys. The prompt wording inside the function is an example you can adapt:

```python
def rewrite_bullets(bullets: list[str]) -> list[dict]:
    # Format the bullets into a delimited block
    bullet_text = "\n".join(f"- {b}" for b in bullets)

    prompt = f"""
    You are a professional resume coach helping a career changer.
    Rewrite each resume bullet point below to be more specific, results-oriented, and compelling.
    Use strong action verbs. Do not invent facts that aren't implied by the original.

    Return ONLY a valid JSON list. Each item should have two keys:
    "original" (the original bullet) and "improved" (your rewritten version).

    Bullet points:
    ```
    {bullet_text}
    ```
    """

    messages = [{"role": "user", "content": prompt}]
    # Your code here: call get_completion(), parse the JSON, and return the result
```

Test it with these starter bullets:

```python
bullets = [
    "Helped customers with their problems",
    "Made reports for the management team",
    "Worked with a team to finish the project on time"
]
```

Add a comment: *What makes these bullets weak, and what kinds of changes did the model suggest?*

**Before you move on — check:**
- Did `json.loads()` succeed without raising an error? If not, try adding `"Respond ONLY with valid JSON, no other text."` to your prompt. The model sometimes adds a preamble like "Here is the JSON:" that breaks the parser.
- Are both the original and improved versions printing clearly for each bullet?
- Do the improvements feel meaningfully better, or are they just rearranged words? If the output is weak, try making your prompt more specific about what "strong" looks like.

---

## Task 3: Cover Letter Generator

*~30 minutes*

Write a `generate_cover_letter()` function that takes a job title and a brief description of the user's background, and returns a cover letter opening paragraph.

Use **few-shot prompting**: include at least two examples of strong cover letter openings in your prompt before asking for the new one. Your examples should demonstrate the tone and style you want — confident, specific, and not generic.

Keep the function name `generate_cover_letter` and its two parameters as written — the chatbot in Task 5 calls it. The two example openings inside the prompt below are illustrative; you may keep them or write your own:

```python
def generate_cover_letter(job_title: str, background: str) -> str:
    prompt = f"""
    You write strong cover letter opening paragraphs for career changers.
    The paragraph should be 3-5 sentences: confident, specific, and free of clichés.

    Here are two examples of the style and tone you should match:

    Example 1:
    Role: Data Analyst at a healthcare nonprofit
    Background: Seven years as a registered nurse, recently completed a data analytics bootcamp.
    Opening: After seven years as a registered nurse, I've spent my career making decisions
    under pressure using incomplete information — which turns out to be excellent training for
    data analysis. I recently completed a data analytics program where I built dashboards
    tracking patient outcomes across departments. I'm excited to bring that combination of
    clinical context and technical skill to [Company]'s mission-driven work.

    Example 2:
    Role: Junior Software Engineer at a fintech startup
    Background: Ten years in retail banking operations, self-taught Python developer for two years.
    Opening: I spent a decade on the operations side of banking, watching technology decisions
    get made by people who had never processed a wire transfer or resolved a failed ACH batch.
    That frustration turned into curiosity, and two years of self-teaching Python later, I'm
    ready to be on the other side of those decisions. I'm applying to [Company] because your
    work on payment infrastructure is exactly where my domain expertise and new technical skills
    intersect.

    Now write an opening paragraph for this person:
    Role: {job_title}
    Background: {background}
    Opening:
    """

    messages = [{"role": "user", "content": prompt}]
    # Your code here: call get_completion() and return the result
```

Test it with (example values — you may use these or your own):

```python
job_title = "Junior Data Engineer"
background = "Five years of experience as a middle school math teacher; recently completed \
a Python course and built data pipelines using Pandas."
```

Print the generated paragraph. Add a comment: *Why did you choose those particular examples? What does the few-shot pattern help control in the output?*

**Before you move on — check:**
- Does the output feel tailored to the specific person, or is it generic? (Phrases like "I am excited to bring my unique skills..." are a red flag.)
- Does it avoid inventing credentials the user didn't mention?
- Try changing the job title and background to something very different and see if the output adapts. If it sounds the same regardless of input, your prompt may not be specific enough.

---

## Task 4: Moderation Check

*~20 minutes*

Before sending any user input to the model in your chatbot loop, run it through OpenAI's moderation endpoint first.

Write an `is_safe(text)` function that:
1. Calls `client.moderations.create()` with `model="omni-moderation-latest"`
2. Returns `True` if the input is not flagged, `False` if it is
3. Prints a short, respectful message if the input is flagged, asking the user to rephrase

Keep the function name `is_safe` and the moderation model string `"omni-moderation-latest"` exactly as written — the chatbot in Task 5 calls `is_safe`, and the model string is the specific endpoint used here:

```python
def is_safe(text: str) -> bool:
    result = client.moderations.create(
        model="omni-moderation-latest",
        input=text
    )
    flagged = result.results[0].flagged
    # Your code here: return True if safe, False if flagged, and print a message if flagged
```

Test your function with at least two inputs — one that should pass and one that should be flagged — and print the result of each test. You want to confirm this is working correctly before wiring it into the loop.

**Before you move on — check:**
- Does your flagged test case actually get caught? If not, try a more explicit phrase.
- Does your safe test case pass without triggering any warning?
- What happens if you test a borderline phrase? Look at `result.results[0].categories` to see which category was triggered.

---

## Task 5: The Chatbot Loop

*~30 minutes*

Now assemble everything into a working chatbot. Use the starter code below as your structure — your job is to fill in the marked sections. Keep the `run_chatbot()` structure and the calls to `is_safe()`, `rewrite_bullets()`, `generate_cover_letter()`, and `get_completion()`; the surrounding print text and keyword triggers are examples you can adapt:

```python
def run_chatbot():
    # 1. Initialize conversation history with your system prompt
    messages = [
        {"role": "system", "content": YOUR_SYSTEM_PROMPT}
    ]

    print("=" * 50)
    print("Job Application Helper")
    print("=" * 50)
    print("I can help you with:")
    print("  1. Rewriting resume bullet points")
    print("  2. Drafting a cover letter opening")
    print("  3. Any other questions about your application")
    print("\nType 'quit' at any time to exit.\n")

    while True:
        user_input = input("You: ").strip()

        # 2. Handle exit
        if user_input.lower() in {"quit", "exit"}:
            print("\nJob Application Helper: Good luck with your applications!")
            break

        # 3. Skip empty input
        if not user_input:
            continue

        # 4. Run moderation check before doing anything else
        if not is_safe(user_input):
            continue  # is_safe() already printed the warning message

        # 5. Check if the user wants to rewrite bullets
        #    (hint: look for keywords like "bullet" or "resume" in user_input.lower())
        if "bullet" in user_input.lower() or "resume" in user_input.lower():
            print("\nJob Application Helper: Paste your bullet points below, one per line.")
            print("When you're done, type 'DONE' on its own line.\n")
            raw_bullets = []
            while True:
                line = input().strip()
                if line.upper() == "DONE":
                    break
                if line:
                    raw_bullets.append(line)
            # YOUR CODE: call rewrite_bullets() and print the results

        # 6. Check if the user wants a cover letter
        elif "cover letter" in user_input.lower():
            job_title = input("Job Application Helper: What is the job title? ").strip()
            background = input("Job Application Helper: Briefly describe your background: ").strip()
            # YOUR CODE: call generate_cover_letter() and print the result

        # 7. Otherwise, handle it as a regular chat turn
        else:
            # YOUR CODE:
            # - Append the user's message to `messages`
            # - Call get_completion(messages)
            # - Print the reply
            # - Append the reply to `messages` as an assistant message
            pass


if __name__ == "__main__":
    run_chatbot()
```

**Before you move on — check:**
- Have a short conversation with your bot (3-4 exchanges) without using the bullet or cover letter features. After each turn, add a temporary `print(len(messages))` to confirm the history is growing. Remove it when you're done.
- Ask the bot something from turn 1, then reference it in turn 3 (e.g., give your name in the first message, then ask "what did I tell you my name was?"). If it can't remember, check that you're appending both user and assistant messages to `messages` after every turn.
- Try triggering the bullet rewriter and cover letter generator from inside the loop and confirm they still work.
- Type `quit` and confirm the bot exits cleanly.

---

## Task 6: Ethics Reflection

*~20 minutes*

**Choose one of the following** and add a comment at the top of your reflection noting which format you chose:

**Option A — Comment block**: At the bottom of `project_05.py`, add a comment block responding to the questions below. Write at least 3-5 sentences total.

**Option B — Short video**: Record a 2-3 minute Loom or YouTube video walking through the same questions and paste the link as a comment at the bottom of `project_05.py`. This can be submitted as your second LMS link.

**Respond to at least two of the following three questions:**

1. Your bot was trained on text written by and about certain kinds of people. How might this produce biased advice? Could it favor certain communication styles, industries, or cultural backgrounds?
2. What could go wrong if a job-seeker submitted the bot's output directly — without reviewing it — to a real employer?
3. What is one guardrail you would add if you were deploying this tool professionally? (A guardrail is any design choice that reduces the chance of harm — a UI warning, a moderation filter, a usage policy, a disclaimer, or something else entirely.)

# Optional / Extension Tasks

These are all optional. You may skip any or all of them, and you will not lose points for doing so.

1. **(Optional) Token budget tracker**: After each turn in the chatbot loop, print a running total of tokens used. Use the `.usage.total_tokens` field on the response object. Warn the user when they cross a threshold you define (e.g., 2,000 tokens).

2. **(Optional) Swap in Ollama**: Modify Task 5 to route the regular chat turns to your local `qwen3:0.6b` model using the Ollama Python API. Compare the response quality to `gpt-4o-mini`. What tradeoffs do you notice?

3. **(Optional) Resume upload**: Instead of collecting bullets interactively, let the user specify a `.txt` file path at the start of the session and read the bullets from it. Pass the full list through `rewrite_bullets()` automatically.

4. **(Optional) Confidence-aware output**: Extend the JSON schema in Task 2 to include a `"confidence"` field (float, 0–1). If confidence is below 0.7, have the bot print a note flagging that bullet for the user to review carefully.

5. **(Optional) Top-p experiment** (add to warmup): Add a question exploring `top_p`. Set `temperature=1.0` and vary `top_p` between `0.1`, `0.5`, and `1.0` for the same prompt. Print and compare the results. How does it differ from what you observed when varying `temperature`?


<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

**General grading notes:**

- This assignment is about applying LLM techniques, not reproducing exact text. Almost every output here is **LLM-generated and nondeterministic**, and many inputs are **student-chosen** (personas, system prompts, the second-persona choice, bullet points, cover-letter job/background, moderation test phrases, ethics answers). Grade whether the required technique and structure are present — do **not** fail a student because their wording, the model's reply, or a sample value differs from any reference or from another student.
- **File paths and folder layout** (`assignments_05/`, `warmup_05.py`, `project_05.py`, the `.env` location) are enforced by any automated run, not by the reviewer's inspection. Do not fail a submission for a path or folder structure you cannot verify.
- Exact-vs-example labels used below:
  - `Use exactly as written (later tasks depend on these names)` — hold the line on these identifiers/strings.
  - `Example — adapt to your own values` — a differing value must **not** be failed.

### Required Deliverables/Tasks

Warmup — all in `warmup_05.py`, with each section/question marked by a comment and outputs printed with labels.

- **API Question 1** — Make a chat completion with model `"gpt-4o-mini"` and the given prompt; print the response *text* (not the whole object), the responding model name, and the total tokens used, each labeled. `"gpt-4o-mini"` `Use exactly as written (later tasks depend on these names)`; the prompt string is provided, its answer text varies.
- **API Question 2** — Run the same prompt at temperatures `0`, `0.7`, and `1.5`; print each labeled by temperature; include a comment on how outputs differ and which temperature suits reproducible output. `temperatures = [0, 0.7, 1.5]` `Use exactly as written (later tasks depend on these names)`; the prompt is `Example — adapt to your own values`.
- **API Question 3** — One API call with `n=3` and `temperature=1.0`; iterate `response.choices` and print all three completions.
- **API Question 4** — Set `max_tokens=15` on a normally-long prompt; print the (cut-off) result; comment on what happened and why `max_tokens` is useful in real apps.
- **System Question 1** — Use a `system` message to set a persona, ask a question, print the reply; then change to a different persona (student's choice), ask again, print, and comment on what changed. Personas and replies vary.
- **System Question 2** — Build the given multi-message conversation manually (no loop/input) and send it in one call; print the reply; comment on why the model "knows" the name despite being stateless. The message list is provided.
- **Prompt Question 1 (Zero-Shot)** — Classify the three given reviews as `positive` / `negative` / `mixed` with no examples; print each labeled by review number.
- **Prompt Question 2 (One-Shot)** — Same task with one example added; print results; comment on any change in format/consistency vs Q1.
- **Prompt Question 3 (Few-Shot)** — Same task with three examples (at least one positive, one negative, one mixed); print results; comment comparing zero/one/few-shot and when to use each.
- **Prompt Question 4 (Chain of Thought)** — Prompt the model to show step-by-step reasoning on the given salary problem, with the final answer clearly labeled; print the full response; comment on why step-by-step reasoning helps. Reasoning wording varies — do not fail on phrasing.
- **Prompt Question 5 (Structured Output)** — Ask for output as valid JSON with keys `sentiment`, `confidence` (float 0–1), and `reason`; print raw response, then `json.loads()` it and print each field labeled; wrap parsing in `try/except` that prints the raw response on failure. Keys `sentiment`, `confidence`, `reason` `Use exactly as written (later tasks depend on these names)`.
- **Prompt Question 6 (Delimiters)** — Use triple-backtick delimiters to separate instructions from user text on the given instruction passage; then send a second, non-instruction passage and confirm the model returns exactly `No steps provided.`; comment on what delimiters prevent.
- **Ollama Question 1** — Run the given `ollama run qwen3:0.6b ...` command, paste its output as a comment; also make the equivalent OpenAI API call and print its response; comment comparing the two plus one advantage and one disadvantage of running locally. Local install/output is not reviewer-verifiable — accept the pasted comment as evidence.

Project — all in `project_05.py`.

- **Task 1: Setup and system prompt** — Load the key, initialize the client, define the `get_completion()` helper, and write a specific job-application-coach system prompt covering role, who it helps, and at least the three listed behavioral constraints; add a comment explaining one deliberate design choice. `get_completion` `Use exactly as written (later tasks depend on these names)`; the system prompt wording is the student's own.
- **Task 2: Bullet rewriter** — `rewrite_bullets()` that uses delimiters, requests a JSON list of `{"original", "improved"}` items, parses it, and prints both versions side by side; test with the starter bullets; comment on why the bullets are weak. Function name `rewrite_bullets` and keys `"original"`/`"improved"` `Use exactly as written (later tasks depend on these names)`; the starter bullets and prompt wording are `Example — adapt to your own values`.
- **Task 3: Cover letter generator** — `generate_cover_letter(job_title, background)` using few-shot prompting with at least two example openings; returns an opening paragraph; test it and print; comment on the example choices and what few-shot controls. Function name and signature `Use exactly as written (later tasks depend on these names)`; the in-prompt examples and the test `job_title`/`background` are `Example — adapt to your own values`.
- **Task 4: Moderation check** — `is_safe(text)` that calls `client.moderations.create(model="omni-moderation-latest", ...)`, returns `True` if not flagged and `False` if flagged, and prints a respectful rephrase message when flagged; test with at least one passing and one flagged input and print each result. Function name `is_safe` and model string `"omni-moderation-latest"` `Use exactly as written (later tasks depend on these names)`; test phrases vary.
- **Task 5: The chatbot loop** — `run_chatbot()` that seeds history with the system prompt, loops on user input, exits on `quit`/`exit`, skips empty input, runs `is_safe()` before anything else, routes bullet/resume keywords to `rewrite_bullets()` and "cover letter" to `generate_cover_letter()`, and otherwise appends the user message, calls `get_completion(messages)`, prints the reply, and appends the reply as an assistant message so history accumulates. Function/call names `Use exactly as written (later tasks depend on these names)`; the printed banner text and trigger keywords are `Example — adapt to your own values`.
- **Task 6: Ethics reflection** — Either Option A (a comment block of at least 3–5 sentences at the bottom of `project_05.py`) **or** Option B (a 2–3 minute video link pasted as a comment), with a note stating which format was chosen, responding to at least two of the three listed questions. Both formats earn full credit — do not require the comment-block form if a video link is provided.

### Optional Deliverables/Tasks

Everything under "Optional / Extension Tasks" is skippable. **Do not fail a student for omitting any of these.** If attempted, grade only that it works as described.

- **(Optional) Token budget tracker** — Print a running total of tokens (`.usage.total_tokens`) after each chatbot turn and warn past a student-defined threshold.
- **(Optional) Swap in Ollama** — Route regular chat turns to a local `qwen3:0.6b` model via the Ollama Python API and compare quality/tradeoffs.
- **(Optional) Resume upload** — Read bullets from a user-specified `.txt` file path and pass them through `rewrite_bullets()` automatically. The file path is user-supplied at runtime — not reviewer-verifiable.
- **(Optional) Confidence-aware output** — Add a `"confidence"` (float 0–1) field to the Task 2 JSON and flag bullets below 0.7 for review.
- **(Optional) Top-p experiment** — Add a warmup question varying `top_p` (`0.1`, `0.5`, `1.0`) at `temperature=1.0` and compare with the temperature results.

</details>
