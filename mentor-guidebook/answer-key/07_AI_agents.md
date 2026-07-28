# Week 7 Assignments

This week's assignments will cover the week 7 material, including:

- What AI agents are and how they differ from plain LLMs
- The ReAct framework (Reason → Act → Observe)
- Building a tool-based agent from scratch with the OpenAI API
- Writing JSON tool schemas
- Using smolagents: the `@tool` decorator, `ToolCallingAgent`, and `CodeAgent`

As with previous weeks, Part 1 is a set of warmup exercises that build up your skills one step at a time. Part 2 is a mini-project where you put it all together in a real agent you build from scratch.

Good luck, and have fun with it! Agents are one of the most exciting areas in AI right now, and by the end of this assignment you'll have built one yourself.

# Submission instructions

In your `python200-homework` repository, create a folder called `assignments_07/`. Inside that folder, create two files and an outputs directory:

1. `warmup_07.py`  : for the warmup exercises
2. `project_07.py` : for the project exercise
3. `outputs/`      : for any plots or data files your code generates

When finished, commit the files to your repo and open a PR as discussed in the assignment's [README page](https://github.com/Code-the-Dream-School/python-200/blob/e072675df8c08073483cf708d18e28916635a203/assignments/README.md).

Note it is very helpful for your mentors if you write your thoughts/comments in your code. This helps us understand your thought process and give you better feedback.

**Setup reminder:** These exercises require an OpenAI API key in a `.env` file (same setup as Weeks 5 and 6). For the smolagents questions, make sure you have installed the library:

```bash
pip install smolagents
```

# Part 1: Warmup Exercises

Put all warmup exercises in a single file: `warmup_07.py`. Use comments to mark each section and question (e.g. `# --- Lesson 02 ---` and `# Q1`). Use `print()` to display all outputs.

---

## Lesson 02: Tool Definitions and the ReAct Loop

### Q1

Define the following Python function:

```python
def celsius_to_fahrenheit(celsius: float) -> str:
    """Convert a Celsius temperature to Fahrenheit and return it as a formatted string."""
    fahrenheit = (celsius * 9 / 5) + 32
    return f"{celsius}°C is {fahrenheit}°F"
```

Next, write the JSON schema dictionary that describes this function to an LLM — exactly like the `get_current_time` schema in the lesson. Your schema should include `name`, `description`, and `parameters` (with a `celsius` property of type `"number"`).

Finally, call the function directly (not through an agent yet) with `0`, `100`, and `-40` and print each result.

### Q2

Copy the `run_agent` function from the lesson — the one that uses `get_current_time` as its only tool. Before calling it, add a comment block that predicts:

1. Will calling `run_agent("Convert 100 degrees Celsius to Fahrenheit")` trigger a tool call? Why or why not?
2. How many API calls will be made to answer this query?

Then call `run_agent("Convert 100 degrees Celsius to Fahrenheit")` and print the result. Was your prediction correct?

### Q3

Now extend the agent to support both tools. Update your `tools` list to include `celsius_to_fahrenheit` (using the schema from Q1), and update `run_agent` to dispatch it when the model requests it.

Test the extended agent on both of these queries:

```python
response_a = run_agent("What is 37 degrees Celsius in Fahrenheit?")
print("Response A:", response_a)

response_b = run_agent("What is the boiling point of water in plain English?")
print("Response B:", response_b)
```

Add a comment after each `print()` explaining whether a tool was called and why.

---

## Lesson 03: Multi-Tool Agent

For Q4–Q6, use the full `CsvManager` class and `run_agent_cycle` setup from the lesson (copy them into your file). You will extend them.

### Q4

The lesson ended with the agent hitting the tool-round limit when asked to compute a correlation, because no tool existed for it. Fix that.

Add a `compute_correlation` method to `CsvManager`:

```python
def compute_correlation(self, col1: str, col2: str):
    """
    Compute the Pearson correlation between two columns in the loaded DataFrame.
    Returns the correlation coefficient and p-value.
    """
    # your code here
```

Use `scipy.stats.pearsonr` to compute the correlation. Return a dictionary with keys `"col1"`, `"col2"`, `"pearson_r"`, and `"p_value"` (round each float to 4 decimal places). Return `{"error": "..."}` if either column is not found or no CSV is loaded.

Also add its JSON schema entry to `tools_schema` and its entry to `node_tools`.

### Q5

Recreate the scenario from the lesson that hit the tool-round limit. Set up the agent with the system prompt from the lesson, then run:

```python
messages = [{"role": "system", "content": SYSTEM_PROMPT}]
result = run_agent_cycle(messages, "Load bike_commute.csv and compute the correlation between avg_traffic_density and avg_speed_kmh.")
print(result)
```

With the new tool in place, the agent should now succeed. Print the agent's final response.

### Q6

After Q5 runs, print the full `messages` list. Each item in the list is a dictionary with a `"role"` key. Add a comment above the print that identifies what each role (`system`, `user`, `assistant`, `tool`) represents in the ReAct loop.

Hint:

```python
import json
print(json.dumps(messages, indent=2, default=str))
```

---

## Lesson 04: smolagents

For Q7–Q9, use the smolagents setup from the lesson (`ToolCallingAgent`, `CodeAgent`, `OpenAIServerModel`, and the `@tool` decorator). Reuse the `CsvManager` instance from above.

### Q7

Re-wrap `compute_correlation` as a smolagents tool using the `@tool` decorator. The decorated function should call `csv_manager.compute_correlation(col1, col2)` under the hood.

After defining it, run:

```python
print(compute_correlation.description)
```

Add a comment comparing what smolagents generates automatically to the JSON schema you wrote manually in Q4. What information does smolagents need from you (the developer) in order to produce a good description?

### Q8

Create both a `ToolCallingAgent` and a `CodeAgent` using the same `TOOLS` list from the lesson (including your new `compute_correlation` tool) and the same `OpenAIServerModel`. Run the following prompt through both:

```python
prompt = "Load bike_commute.csv. Plot avg_heart_rate vs duration_min as a scatter plot with green dots."

response_tool = tool_agent.run(prompt)
response_code = code_agent.run(prompt, additional_args={"csv_manager": csv_manager})
```

Print both responses, then add a comment block answering:

1. What did each agent actually produce? Did the `ToolCallingAgent` change the dot color? Did the `CodeAgent`?
2. What does this reveal about when each type of agent is more useful?

### Q9

Add a comment block at the bottom of your warmup file answering both questions:

1. Describe a task where a `ToolCallingAgent` would be a better choice than a `CodeAgent`. What property of the task makes it a good fit for a tool-based approach?
2. What is one meaningful risk of using a `CodeAgent` that does not apply to a `ToolCallingAgent`? (Think about what's actually happening when the agent generates and runs code.)

This is the last answer to put in `warmup_07.py`. Congrats!!!

---

# Part 2: Mini-Project — World Happiness Agent

In Week 1, you built a Prefect pipeline that loaded, cleaned, and analyzed the World Happiness dataset. In this project, you will revisit that same dataset — but this time you will use a `CodeAgent` to explore it conversationally.

The goal is to build a complete agent from scratch: define the tools, instantiate the agent, and run it through a series of guided queries. Along the way you should see exactly where the agent uses your tools, where it writes its own code, and where its reasoning impresses or surprises you.

Place your code in `assignments_07/project_07.py`. Save any plots to `assignments_07/outputs/`.

## Pre-task: Load the Data

Your agent will need access to the World Happiness data. If you still have the merged file from Week 1, you can point directly to it:

```python
DATA_PATH = "assignments_01/outputs/merged_happiness.csv"
```

If you don't have that file, you can load and merge the yearly CSVs from `assignments/resources/happiness_project/` inside a `load_happiness_data` tool — see the hint in Task 1 below.

---

## Task 1: Define Your Tools

Using the smolagents `@tool` decorator, implement the four tools below. Each tool operates on a shared global DataFrame (define `df = None` at the top of the file and update it inside `load_happiness_data`).

**Tool 1: `load_happiness_data`**

```python
@tool
def load_happiness_data() -> dict:
    """Load the World Happiness dataset into memory.
    ...
    """
```

Load the merged CSV from `DATA_PATH`. If that file does not exist, fall back to loading and merging all yearly CSVs from `assignments/resources/happiness_project/` (use a loop, just like in the Week 1 project). Store the result in the global `df`. Return a dict with `"shape"` and `"columns"`.

**Tool 2: `summarize_column`**

```python
@tool
def summarize_column(column: str) -> dict:
    """Return descriptive statistics for a single column in the loaded dataset.
    ...
    """
```

Return `df[column].describe().to_dict()`. Return `{"error": "..."}` if no data is loaded or the column is not found.

**Tool 3: `compute_correlation`**

```python
@tool
def compute_correlation(col1: str, col2: str) -> dict:
    """Compute the Pearson correlation coefficient and p-value between two numeric columns.
    ...
    """
```

Use `scipy.stats.pearsonr`. Return a dict with `"col1"`, `"col2"`, `"pearson_r"`, and `"p_value"` (rounded to 4 decimal places). Return `{"error": "..."}` on bad input.

**Tool 4: `get_top_n_countries`**

```python
@tool
def get_top_n_countries(column: str, year: int, n: int = 5) -> dict:
    """Return the top N countries ranked by a given column for a specific year.
    ...
    """
```

Filter `df` to the given `year`, sort by `column` in descending order, and return the top `n` rows as a list of dicts (each dict has `"country"` and the requested `column` value). Return `{"error": "..."}` on bad input.

Write complete Google-style docstrings for all four tools. Remember: smolagents reads your docstring to understand what the tool does and when to use it.

---

## Task 2: Build the Agent

Instantiate a `CodeAgent`:

```python
from smolagents import CodeAgent, OpenAIServerModel

model = OpenAIServerModel(api_key=api_key, model_id="gpt-4o-mini")

SYSTEM_PROMPT = """
You are a data analyst assistant for the World Happiness dataset.
Use the available tools for loading data, summarizing columns, computing correlations,
and ranking countries. Write Python code directly only when the tools are not sufficient
(for example, when creating custom plots or computing something the tools don't cover).
Be concise and student-friendly in your responses.
"""

agent = CodeAgent(
    tools=[load_happiness_data, summarize_column, compute_correlation, get_top_n_countries],
    model=model,
    instructions=SYSTEM_PROMPT,
    additional_authorized_imports=["pandas", "matplotlib.pyplot", "scipy.stats"],
    max_steps=8,
)
```

---

## Task 3: Run Guided Queries

Run the five queries below in sequence. Use `reset=False` so the agent retains context across turns. Print each response.

```python
queries = [
    "Load the happiness data and tell me its shape and column names.",
    "Summarize the happiness_score column.",
    "What is the correlation between gdp_per_capita and happiness_score? Is it statistically significant?",
    "Show me the top 5 happiest countries in 2020.",
    "Plot happiness_score over the years as a line chart, with one line per region. Save the plot to outputs/happiness_by_region.png.",
]

for query in queries:
    print(f"\n--- Query: {query} ---")
    response = agent.run(query, reset=False)
    print(response)
```

Query 5 should cause the agent to write matplotlib code (no tool covers multi-line regional plots). Verify that `outputs/happiness_by_region.png` is saved to disk after running.

---

## Task 4: Your Own Questions

Run two additional queries of your own choice. Try to make at least one of them require the agent to write code rather than just call a tool.

```python
# My query 1
my_query_1 = "..."   # replace with your question
response_1 = agent.run(my_query_1, reset=False)
print(response_1)
# Comment: Did this trigger tool use, code generation, or both?

# My query 2
my_query_2 = "..."   # replace with your question
response_2 = agent.run(my_query_2, reset=False)
print(response_2)
# Comment: Did this trigger tool use, code generation, or both?
```

---

## Task 5: Reflection

Add a comment block at the very bottom of `project_07.py` answering these three questions:

```python
# --- Reflection ---
#
# 1. In Query 3, how did the agent communicate whether the correlation was statistically
#    significant? Did it use the p-value correctly? What threshold did it apply?
#
# 2. Did any of the agent's responses surprise you — either by being more capable than
#    you expected, or less? Describe one specific example.
#
# 3. What one additional tool would make this agent meaningfully more useful?
#    Describe what it would do and what kind of question it would help the agent answer.
#    (You do not need to implement it.)
```

### Running the Project

Structure your file so all setup and queries run when the script is executed directly:

```python
if __name__ == "__main__":
    # Task 3 queries
    # Task 4 queries
```

The full project should be runnable with:

```bash
python project_07.py
```

When you run it, all five guided queries should complete, the plot should be saved to `outputs/happiness_by_region.png`, and your two custom queries should run as well.
