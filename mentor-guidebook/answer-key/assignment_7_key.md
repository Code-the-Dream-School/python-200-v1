# Assignment 7 Answer Key: AI Agents

**Mentor note:** This key covers Week 7 warmups (tool definitions, the ReAct loop, multi-tool agents, smolagents) and the World Happiness Agent mini-project. **Reproducibility caveat:** agents call live LLMs and decide their own steps, so the exact reasoning trace, wording, and which-tool-when will vary run to run. Grade the tool implementations, schemas, and dispatch logic (which *are* checkable) plus the quality of the reflection comments. The deterministic pieces — the `celsius_to_fahrenheit` outputs, the JSON schema shape, and `compute_correlation`'s return contract — are given exactly below.

---

## Expected File Setup

Assignment lives in `assignments_07/`:

```
assignments_07/
├── warmup_07.py     # all warmup exercises
├── project_07.py    # mini-project agent
├── outputs/         # saved plots
└── .env             # OPENAI_API_KEY — not committed
```

Requires `pip install smolagents`. The project reuses the World Happiness data (ideally the merged CSV from Week 1; otherwise it re-merges the yearly files).

---

# Part 1: Warmup Exercises (`warmup_07.py`)

## Lesson 02: Tool Definitions and the ReAct Loop

### Q1 — **Objective**
Direct function calls (deterministic):
- `celsius_to_fahrenheit(0)` → `"0°C is 32.0°F"`
- `celsius_to_fahrenheit(100)` → `"100°C is 212.0°F"`
- `celsius_to_fahrenheit(-40)` → `"-40°C is -40.0°F"`

JSON schema should match the lesson's shape:
```python
{
    "type": "function",
    "function": {
        "name": "celsius_to_fahrenheit",
        "description": "Convert a Celsius temperature to Fahrenheit...",
        "parameters": {
            "type": "object",
            "properties": {
                "celsius": {"type": "number", "description": "..."}
            },
            "required": ["celsius"]
        }
    }
}
```
Check that `name` matches the function, `celsius` is type `"number"`, and it's marked required. (Exact wording of descriptions is free; the structure is what matters. Accept the flatter `{"name", "description", "parameters"}` form if that's what the lesson used.)

### Q2 — **Objective (approach) + Subjective**
Prediction comment then result. Correct prediction:
1. **No tool call** — the only tool is `get_current_time`, which doesn't match a temperature-conversion request, so the model answers from its own knowledge.
2. **One API call** (no tool round-trip needed).
The model should answer that 100°C = 212°F directly. A student who predicted a tool call should recognize why it didn't happen.

### Q3 — **Objective (approach) + Subjective**
Agent extended with both tools; `tools` list and dispatch logic updated.
- Response A ("37°C in Fahrenheit?") → **triggers `celsius_to_fahrenheit`**, returns 98.6°F. Comment: a matching tool exists, so the model calls it.
- Response B ("boiling point of water in plain English?") → **no tool call**; answered from general knowledge (100°C / 212°F). Comment: no tool needed/matched.
- Key check: the dispatch code actually routes the model's requested tool name to the right function and feeds the result back.

## Lesson 03: Multi-Tool Agent

### Q4 — **Objective (contract)**
`compute_correlation` added to `CsvManager`:
- Uses `scipy.stats.pearsonr`.
- Returns a dict with keys `"col1"`, `"col2"`, `"pearson_r"`, `"p_value"`, each float rounded to 4 decimals.
- Returns `{"error": "..."}` if a column is missing or no CSV is loaded.
- Its schema is added to `tools_schema` and its dispatch entry to `node_tools`. Missing either registration is the usual bug — the tool exists but the agent can't call it.

### Q5 — **Objective (approach)**
Re-runs the scenario that previously hit the tool-round limit. With the new tool registered, the agent now **succeeds** and returns the correlation between `avg_traffic_density` and `avg_speed_kmh`. The final response should report a real coefficient/p-value (expected to be a negative correlation — more traffic, lower speed — but the dataset drives the exact number). If it still hits the round limit, the schema/dispatch wiring from Q4 is likely incomplete.

### Q6 — **Objective (approach) + Subjective**
Prints the full `messages` list. Comment correctly maps the ReAct roles:
- **system** — the instructions/persona and available-tools framing.
- **user** — the human query.
- **assistant** — the model's turns, including its decision to call a tool (Reason/Act).
- **tool** — the returned result of a tool call (Observe), fed back for the next reasoning step.

## Lesson 04: smolagents

### Q7 — **Objective (approach) + Subjective**
`compute_correlation` re-wrapped with `@tool`, calling `csv_manager.compute_correlation(...)` internally. `print(compute_correlation.description)` shows an auto-generated description. Comment: smolagents builds the schema from the **function signature + type hints + docstring**, so a good docstring and typed params are what the developer must supply (vs. the hand-written JSON schema in Q4).

### Q8 — **Objective (approach) + Subjective**
Both a `ToolCallingAgent` and a `CodeAgent` run the scatter-plot prompt. Expected observation:
- The **`ToolCallingAgent`** can only call existing tools, so it **cannot honor "green dots"** unless a tool exposes color — it produces the plot but not the custom styling.
- The **`CodeAgent`** writes matplotlib code directly, so it **can** make the dots green.
- Comment insight: tool-calling agents are constrained to predefined actions (safer, predictable); code agents are flexible (handle novel/custom requests) but run generated code.

### Q9 — **Subjective**
1. A `ToolCallingAgent` is better when the task maps to a **fixed set of well-defined operations** (safety, predictability, auditability matter — e.g. regulated actions, API calls with strict contracts).
2. A `CodeAgent`'s distinct risk: it **generates and executes arbitrary code**, which can be unsafe (destructive commands, security holes, unpredictable behavior) — a risk tool-calling agents don't have.

---

# Part 2: Mini-Project — World Happiness Agent (`project_07.py`)

**Overall check:** four working `@tool` functions with proper docstrings, a `CodeAgent` wired to them, and the guided queries running with `reset=False` so context persists. The plot must actually be saved to disk. Grade tool correctness + docstrings + reflection; the agent's per-run reasoning varies.

### Pre-task: Load the Data — **Objective (approach)**
Points at the Week 1 merged CSV via `DATA_PATH`, or falls back to merging the yearly files inside `load_happiness_data`.

### Task 1: Define Tools — **Objective (contract)**
All four use the `@tool` decorator with complete Google-style docstrings (smolagents reads these to decide when to use each tool — thin docstrings are a real deduction here, not a style nit).
- **`load_happiness_data`** → loads merged CSV (or merges yearly files), stores in global `df`, returns `{"shape", "columns"}`.
- **`summarize_column`** → returns `df[column].describe().to_dict()`; `{"error": ...}` if no data / bad column.
- **`compute_correlation`** → `scipy.stats.pearsonr`; returns `{"col1", "col2", "pearson_r", "p_value"}` rounded to 4 decimals; `{"error": ...}` on bad input.
- **`get_top_n_countries`** → filters to `year`, sorts by `column` descending, returns top `n` as a list of dicts (country + column value); `{"error": ...}` on bad input.
- Common misses: forgetting the `global df` update in `load_happiness_data`; no error-handling branch; missing/weak docstrings.

### Task 2: Build the Agent — **Objective (approach)**
`CodeAgent` with all four tools, the `OpenAIServerModel` (`gpt-4o-mini`), the given system prompt as `instructions`, `additional_authorized_imports=["pandas", "matplotlib.pyplot", "scipy.stats"]`, and `max_steps=8`.

### Task 3: Guided Queries — **Objective (approach) + Subjective**
Five queries run in sequence with `reset=False`. Expected behavior:
- Q1 → calls `load_happiness_data` (reports shape + columns).
- Q2 → calls `summarize_column("happiness_score")`.
- Q3 → calls `compute_correlation("gdp_per_capita", "happiness_score")` — should report a **strong positive** correlation with a very small p-value, and state it's significant.
- Q4 → calls `get_top_n_countries("happiness_score", 2020, 5)` — typically Nordic countries (Finland, Denmark, etc.).
- Q5 → **no tool covers this**, so the agent should **write matplotlib code** and save `outputs/happiness_by_region.png`. Verify the file exists on disk after running.

### Task 4: Your Own Questions — **Subjective**
Two student queries, ideally ≥1 requiring generated code. Comments note whether each triggered tool use, code generation, or both. Any reasonable questions are fine.

### Task 5: Reflection — **Subjective**
Comment block answering:
1. How the agent communicated significance in Q3 — did it use the p-value correctly and state a threshold (typically 0.05)?
2. A specific surprise (more or less capable than expected) with a concrete example.
3. One additional useful tool, with what it would do and what questions it would answer (e.g. group-by-region aggregation, year-over-year change, filtering by a threshold).

### Running — **Objective**
`if __name__ == "__main__":` runs Task 3 + Task 4 queries; whole thing runs with `python project_07.py` and saves the plot.