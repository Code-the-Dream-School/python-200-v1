# Week 7 Mentor Summary: AI Agents: Building Autonomous Systems

**Lesson files:** `lessons/07_AI_agents.md` (overview) and five lessons in `lessons/07_AI_agents/`, plus the `mini-etl` demo project in `lessons/07_AI_agents/resources/mini-etl/`
**Assignment file:** `assignments/07_AI_agents.md`
**Answer key:** `mentor-guidebook/answer-key/assignment_07_key.md`
**Slides:** `mentor-guidebook/slides/07_AI_agents.pdf`

**Learning objective:** Students learn that an AI agent is an LLM that can request tools, read the results, and decide its next step in a loop called ReAct. They build tool-calling agents by hand with the OpenAI API and JSON tool schemas. Then they rebuild them with smolagents and compare a `ToolCallingAgent` with a `CodeAgent`. The mini-project is a `CodeAgent` that analyzes the World Happiness dataset.

**Where this fits:** Week 5 taught the OpenAI chat API, the `messages` list with its roles, and the chatbot loop, and this week extends all three. Lesson 4 compares smolagents with LlamaIndex from Week 6. The tools use pandas and matplotlib from Python for Data Analysis, and the Copilot demo uses `pytest` from Week 1. Week 10 uses an LLM as a batch step in a pipeline instead of as an agent. No later assignment reuses the Week 7 code.

---

## Lesson Overview

Lessons 3 and 4 use the same data, `bike_commute.csv`, with 160 rides and six columns such as `avg_speed_kmh` and `avg_traffic_density`.

| Lesson | What students learn |
|---|---|
| **1. Overview** | An agent compared with a plain LLM call. The ReAct loop: reason, act, observe, and repeat until done. Tool-based agents compared with code-based agents. A short survey of frameworks (smolagents and LangChain), and of standard interfaces such as the Model Context Protocol (MCP). There is no code in this lesson. |
| **2. Hello, agent** | A `get_current_time` tool described by a JSON schema and passed with `tools=` and `tool_choice='auto'` to `gpt-4.1-mini`. The code reads `tool_calls`, runs the function, sends the result back as a `role: tool` message, and makes a second API call. One query uses the tool, and one does not. |
| **3. Data Analysis Tool Agent** | A `CsvManager` class with six tools, including `load_csv`, `summarize_columns`, and `plot_data`. A `run_agent_cycle` loop with `max_tool_rounds=5`, inside a chat loop. When asked for a correlation that no tool computes, the agent calls unrelated tools and hits the round limit. |
| **4. Smolagents** | The `@tool` decorator, which builds the schema from type hints and a Google-style docstring. `ToolCallingAgent` and `CodeAgent` with `OpenAIServerModel` (`gpt-4o-mini`). Asked for red dots, the tool agent claims success but cannot change the color. The code agent writes matplotlib code instead. `additional_authorized_imports`, `max_steps`, `additional_args`, and `reset=False` for multi-turn chat. |
| **5. Demo: AI Paired Programmer** | GitHub Copilot in agent mode in VS Code fixes the broken `mini-etl` project until its five `pytest` tests pass, then writes a demo notebook. The lesson stresses reviewing AI-generated code as a first draft. No assignment task uses this lesson. |

---

## Assignment Deliverables

**Setup:** Students work in `assignments_07/` with an `outputs/` folder and a `.env` file with `OPENAI_API_KEY`. They need `smolagents` and `scipy`, and both are in the course `requirements.txt`. Warmup Q4–Q8 need `bike_commute.csv` in `assignments_07/resources/`, and the assignment's setup note tells students to copy it there (see FAQ 2). For the project, students copy `assignments/resources/happiness_project/` into `assignments_07/`.

**Grading:** Agents call live LLMs and choose their own steps, so wording, step counts, and tool order vary from run to run. Grade the tool code, schemas, dispatch logic, and comments. The deterministic parts are the `celsius_to_fahrenheit` outputs and the `compute_correlation` return keys, and the answer key lists them.

| Part | File | What students do | Concepts practiced |
|---|---|---|---|
| Warmup Q1–Q3 | `warmup_07.py` | Write a JSON schema for `celsius_to_fahrenheit`. Predict and test whether the time-only agent calls a tool for a temperature question. Extend `run_agent` to dispatch both tools. | Tool schemas, `tool_calls`, two API calls |
| Warmup Q4–Q6 | `warmup_07.py` | Add `compute_correlation` (using `scipy.stats.pearsonr`) to `CsvManager` and register it in `tools_schema` and `node_tools`. Rerun the query that hit the round limit, and print the `messages` list with each role explained. | Multi-tool dispatch, the ReAct message history |
| Warmup Q7–Q9 | `warmup_07.py` | Wrap `compute_correlation` with `@tool` and print its `.description`. Run a "green dots" scatter prompt through both agent types and compare them. | smolagents, tool agents and code agents |
| Project, Task 1 | `project_07.py` | Write four `@tool` functions over a global `df`: `load_happiness_data`, `summarize_column`, `compute_correlation`, and `get_top_n_countries`. Each needs a Google-style docstring and an error dict for bad input. | Tool design, docstrings |
| Project, Tasks 2–3 | `project_07.py` | Build a `CodeAgent` (`gpt-4o-mini`, `max_steps=8`) and run five guided queries with `reset=False`. Query 5 should make the agent write matplotlib code and save `outputs/happiness_by_region.png`. | Code agents, conversation state |
| Project, Tasks 4–5 | `project_07.py` | Run two queries of their own, at least one of which needs code. Answer three reflection questions. | Reflection |

**Optional:** This week has no optional tasks. The GitHub Copilot demo is not graded.

**Submission:** Students commit their files, including the saved plot in `outputs/`, and open a pull request in their `python200-homework` repository. The `.env` file should not be committed.

---

## Key Concepts

These short explanations cover the ideas students ask about most this week. Expand any one you need.

<details>
<summary><strong>What a tool call actually is</strong></summary>

The most important idea this week is that the LLM never runs code. It can only produce text.

When you pass `tools=` to the API, the model sees a description of each function: its name, its description, and its parameters. If it decides a tool would help, it returns a structured `tool_calls` field instead of an answer. That field is a request: "run `get_current_time` with these arguments."

Your Python code then does the work:

1. Read the tool name and the arguments from `tool_calls`.
2. Run the matching function.
3. Append the result to `messages` as a `role: tool` message.
4. Call the API again so the model can read the result.

This is the ReAct loop: reason (the model decides), act (your code runs the tool), and observe (the model reads the result). Lesson 3's `run_agent_cycle` repeats these steps until the model replies without `tool_calls`, or until `max_tool_rounds` is reached. The model chooses a tool based only on the descriptions, so a vague description leads to poor choices.

</details>

<details>
<summary><strong>Tool-calling agents compared with code agents</strong></summary>

A **`ToolCallingAgent`** can only call the tools you give it. It is predictable and easier to control, but it cannot do anything the tools do not support. In Lesson 4, `plot_data` has no color option, so the agent cannot make the dots red. It reports success anyway, which is a hallucination.

A **`CodeAgent`** writes Python code in each step, and the code can call your tools as ordinary functions. When the tools are not enough, it writes its own code, such as a matplotlib scatter plot with `color="red"`.

This flexibility has a cost. The agent runs code that no person has reviewed. smolagents runs that code in a restricted Python interpreter that allows only standard safe modules plus those listed in `additional_authorized_imports`. Apart from the tools, the interpreter sees only the variables passed through `additional_args`. The lesson passes `csv_manager` this way so the agent can reach the DataFrame.

Warmup Q8 and Q9 ask students to state this trade-off in their own words.

</details>

<details>
<summary><strong>MCP and coding agents such as GitHub Copilot</strong></summary>

Lesson 1 introduces the Model Context Protocol (MCP), created by Anthropic, as an emerging standard. Each framework has its own way to define tools, so a tool written for one framework does not work in another. With MCP, an MCP server exposes tools in a standard format, and any agent that supports MCP can discover and call them. The lesson compares this to USB, which lets any device connect to any computer. The course covers MCP as a concept only, and no lesson or assignment builds an MCP server.

Coding assistants in agent mode, such as GitHub Copilot in Lesson 5, use the same ReAct loop. Their tools include reading files, editing files, and running terminal commands such as `python -m pytest -q`. The demo prompt tells Copilot to edit only `mini_etl.py` and to rerun the tests after each change until they pass. If students ask how Copilot "knows" what to do, the answer is that it follows the same loop they built in Lesson 3.

</details>

---

## FAQs and Common Trouble Spots

**1. "My `load_happiness_data` tool runs, but the data looks wrong, or `happiness_score` is not a column."**
The CSV files use semicolons as separators and commas as decimal points, so they need `pd.read_csv(path, sep=";", decimal=",")`. The original columns are `Country`, `Regional indicator`, `Happiness score` (`Ladder score` in 2024), and `GDP per capita`, and the year is only in the file name. The assignment now explains this and gives example loading code that renames the columns and adds `year`. Check the student's code against the four points in Task 1's "Loading the files" note. Accept any approach that produces `country`, `region`, `happiness_score`, `gdp_per_capita`, and `year`.

**2. "The agent says no CSV files were found."**
The lesson code uses `Path("resources")`, which is relative to the folder where the script runs. The assignment tells students to copy `lessons/07_AI_agents/resources/bike_commute.csv` into `assignments_07/resources/` and to run the script from `assignments_07/`. This error usually means the file was not copied, or the script was run from a different folder.

**3. "In Q2 the agent did not call any tool. Did I make a mistake?"**
No. The only tool is `get_current_time`, which does not fit a temperature question. The model answers directly with one API call. The comment should explain this decision.

**4. "Q5 still hits the tool-round limit after I added `compute_correlation`."**
Check both registrations. The schema must be in `tools_schema`, and the function must be in `node_tools` under the same name. The answer key calls a missing registration "the usual bug."

**5. "My `CodeAgent` cannot make the query 5 plot, or its code fails when it uses `df`."**
The agent's code runs in smolagents' restricted interpreter. That interpreter cannot see the global `df` in the student's file, and it can only import modules listed in `additional_authorized_imports`. The agent may call the tools or read the CSV files itself with pandas. Students can also pass the DataFrame with `additional_args`, as the lesson does with `csv_manager`. Grade that the plot file is produced, not how the agent produced it.

**6. "The `ToolCallingAgent` said it made green dots, but the dots are not green."**
This matches the lesson's red-dots example. `plot_data` has no color option, and the agent claims success anyway. The rubric says not to fail a student on the observed outcome. Grade the Q8 comment.

**7. "How much does this cost? My agent keeps looping."**
Every step in the loop is a separate API call, and the cost grows with each step. In smolagents 1.26, the version in `requirements.txt`, the default `max_steps` is 20, as Lesson 4 says. Students should set `max_steps` explicitly as the assignment does. Using `gpt-4o-mini` keeps the cost low.
