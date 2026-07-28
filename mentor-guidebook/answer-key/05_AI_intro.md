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

Load your API key and initialize the client. Then define a `get_completion()` helper function (as seen in the prompt engineering lesson) that takes a `messages` list and returns the model's text response:

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

Test it with:

```python
job_title = "Junior Data Engineer"
background = "Five years of experience as a middle school math teacher; recently completed \
a Python course and built data pipelines using Prefect and Pandas."
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

Now assemble everything into a working chatbot. Use the starter code below as your structure — your job is to fill in the marked sections.

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

1. **Token budget tracker**: After each turn in the chatbot loop, print a running total of tokens used. Use the `.usage.total_tokens` field on the response object. Warn the user when they cross a threshold you define (e.g., 2,000 tokens).

2. **Swap in Ollama**: Modify Task 5 to route the regular chat turns to your local `qwen3:0.6b` model using the Ollama Python API. Compare the response quality to `gpt-4o-mini`. What tradeoffs do you notice?

3. **Resume upload**: Instead of collecting bullets interactively, let the user specify a `.txt` file path at the start of the session and read the bullets from it. Pass the full list through `rewrite_bullets()` automatically.

4. **Confidence-aware output**: Extend the JSON schema in Task 2 to include a `"confidence"` field (float, 0–1). If confidence is below 0.7, have the bot print a note flagging that bullet for the user to review carefully.

5. **Top-p experiment** (add to warmup): Add a question exploring `top_p`. Set `temperature=1.0` and vary `top_p` between `0.1`, `0.5`, and `1.0` for the same prompt. Print and compare the results. How does it differ from what you observed when varying `temperature`?

---

# Rubric

| Component | Points | What we're looking for |
|---|---|---|
| **Warmup: API basics (Q1–Q4)** | 15 | Calls work; `.choices[0].message.content`, `.model`, `.usage` accessed correctly; temperature experiment includes a comment showing genuine observation |
| **Warmup: System messages (Q5–Q6)** | 10 | System message used correctly; conversation history constructed manually; comment shows understanding of statelesness |
| **Warmup: Prompt engineering (Q7–Q12)** | 20 | Each technique (zero-shot, one-shot, few-shot, CoT, JSON output, delimiters) implemented correctly; comparison comments show genuine reflection |
| **Warmup: Ollama (Q13)** | 5 | CLI output pasted as comment; OpenAI API call made; thoughtful comparison comment |
| **Project Task 1: System prompt** | 10 | Prompt is specific (role, audience, constraints); comment explains at least one deliberate design choice |
| **Project Task 2: Bullet rewriter** | 15 | Delimiters used; JSON parsed correctly; original and improved bullets printed side by side |
| **Project Task 3: Cover letter** | 10 | Two or more few-shot examples present in the prompt; output is tailored to the input; comment explains example choices |
| **Project Task 4: Moderation** | 5 | Moderation check runs before API call; flagged and unflagged inputs both tested and printed |
| **Project Task 5: Chatbot loop** | 15 | History accumulates correctly across turns; moderation wired in; bullet and cover letter features accessible from the loop; exits cleanly |
| **Project Task 6: Ethics reflection** | 10 | At least 2 of 3 questions addressed; responses show genuine engagement rather than surface-level answers |
| **Code quality** | 5 | Outputs labeled; sections marked with comments; code runs without errors |
| **Total** | **120** | |

---
