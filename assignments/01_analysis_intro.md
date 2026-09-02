# Week 1 Assignments
This week's assignments will cover the week 1 material, including:

-   Python 100 review (Pandas, NumPy, Matplotlib)
-   Describing data
-   Hypothesis testing
-   Correlation
-   Pipelines (both home-grown and Prefect)
  
As discussed in the overview of how to approach assignments, the first part of this assignment is a set of warmup exercises to review the week 1 material. The second part is a mini-project that applies the concepts in a more realistic context (setting up a pipeline). 

Good luck, and have fun with it! This is the time to get hands-on practice with the material, feel free to experiment and explore as you work through the material: that is often the best way to learn! 





# Start Here: Create a `python200-homework` repository

**First-Time Setup**: Before submitting your first assignment, create a public GitHub repository called `python200-homework` — you'll use this same repo for all weekly submissions. If you'd like a full overview of the assignment structure and weekly workflow before diving in, check out the [assignments README](https://github.com/Code-the-Dream-School/python-200/blob/e072675df8c08073483cf708d18e28916635a203/assignments/README.md).
  
# Submission instructions
In your `python200-homework` repository, create a folder called `assignments_01/`. Inside that folder, create three files and an outputs directory:

1. `warmup_01.py`      : for the warmup exercises
2. `prefect_warmup.py` : for the prefect pipeline warmup exercise
3. `project_01.py`     : for the project exercise
4. `outputs/`          : for any plots or data files your code generates

When finished, commit the files to your repo and open a PR as discussed in the assignment's [README page](https://github.com/Code-the-Dream-School/python-200/blob/e072675df8c08073483cf708d18e28916635a203/assignments/README.md). 

Note it is very helpful for your mentors if you write your thoughts/comments in your code. This helps us understand your thought process and give you better feedback.

# Part 1: Warmup Exercises
Put all warmup exercises  in a single file: `warmup_01.py`. Use comments to mark each section and question (e.g. `# --- Pandas ---` and `# Pandas Q1`). Use `print()` to display all outputs. 

> **About the code blocks below:** Where a question gives you data (a DataFrame, an array, a list), use it **exactly as written** — these are the inputs to work from, not placeholder values to swap for your own. Several later questions reuse the data defined in an earlier one.

## Pandas Review

### Pandas Question 1

Create the following DataFrame and print the first three rows, the shape, and the data types of each column.

```python
import pandas as pd

data = {
    "name":   ["Alice", "Bob", "Carol", "David", "Eve"],
    "grade":  [85, 72, 90, 68, 95],
    "city":   ["Boston", "Austin", "Boston", "Denver", "Austin"],
    "passed": [True, True, True, False, True]
}
df = pd.DataFrame(data)








```

Print each result with a label (e.g. `print(f"Num Rows: {len(df)}")`).

### Pandas Question 2

Using the DataFrame from Q1, filter the rows to show only students who passed *and* have a grade above 80. Print the result.

### Pandas Question 3

Add a new column called `"grade_curved"` that adds 5 points to each student's grade. Print the updated DataFrame (all columns, all rows).

### Pandas Question 4



Add a new column called `"name_upper"` that contains each student's name in uppercase, using the `.str` accessor. Print the `"name"` and `"name_upper"` columns together.

### Pandas Question 5

Group the DataFrame by `"city"` and compute the mean grade for each city. Print the result.

### Pandas Question 6

Replace the value `"Austin"` in the `"city"` column with `"Houston"`. Print the `"name"` and `"city"` columns to confirm the change.

### Pandas Question 7

Sort the DataFrame by `"grade"` in descending order and print the top 3 rows.

## NumPy Review

### NumPy Question 1




Create a 1D NumPy array from the list `[10, 20, 30, 40, 50]`. Print its shape, dtype, and ndim.

### NumPy Question 2

Create the following 2D array and print its shape and size (total number of elements).

```python
import numpy as np

arr = np.array([[1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]])
```

### NumPy Question 3

Using the 2D array from Q2, slice out the top-left 2x2 block and print it. The expected result is `[[1, 2], [4, 5]]`.

### NumPy Question 4

Create a 3x4 array of zeros using a built-in command. Then create a 2x5 array of ones using a built-in command. Print both.

### NumPy Question 5

Create an array using `np.arange(0, 50, 5)`. First, think about what you expect it to look like. Then, print the array, its shape, mean, sum, and standard deviation.

### NumPy Question 6

Generate an array of 200 random values drawn from a normal distribution with mean 0 and standard deviation 1 (use `np.random.normal()`). Print the mean and standard deviation of the result.

## Matplotlib Review

### Matplotlib Question 1

Plot the following data as a line plot. Add a title `"Squares"`, x-axis label `"x"`, and y-axis label `"y"`.

```python
x = [0, 1, 2, 3, 4, 5]
y = [0, 1, 4, 9, 16, 25]
```

### Matplotlib Question 2

Create a bar plot for the following subject scores. Add a title `"Subject Scores"` and label both axes.

```python
subjects = ["Math", "Science", "English", "History"]
scores   = [88, 92, 75, 83]
```

### Matplotlib Question 3

Plot the two datasets below as a scatter plot on the same figure. Use different colors for each, add a legend, and label both axes.

```python
x1, y1 = [1, 2, 3, 4, 5], [2, 4, 5, 4, 5]
x2, y2 = [1, 2, 3, 4, 5], [5, 4, 3, 2, 1]





```

### Matplotlib Question 4

Use `plt.subplots()` to create a figure with 1 row and 2 subplots side by side. In the left subplot, plot `x` vs `y` from Q1 as a line. In the right subplot, plot the subjects and scores from Q2 as a bar plot. Add a title to each subplot and call `plt.tight_layout()` before showing.

## Descriptive Statistics Review

### Descriptive Stats Question 1


Given the list below, use NumPy to compute and print the mean, median, variance, and standard deviation. Label each printed value.

```python
data = [12, 15, 14, 10, 18, 22, 13, 16, 14, 15]
```

### Descriptive Stats Question 2

Generate 500 random values from a normal distribution with mean 65 and standard deviation 10 (use `np.random.normal(65, 10, 500)`). Plot a histogram with 20 bins. Add a title `"Distribution of Scores"` and label both axes.




### Descriptive Stats Question 3

Create a boxplot comparing the two groups below. Label each box (`"Group A"` and `"Group B"`) and add a title `"Score Comparison"`.

```python
group_a = [55, 60, 63, 70, 68, 62, 58, 65]
group_b = [75, 80, 78, 90, 85, 79, 82, 88]
```

Hint: pass `labels=["Group A", "Group B"]` to `plt.boxplot()`.

### Descriptive Stats Question 4

You are given two datasets: one normally distributed and one 'exponential' distribution.

```python
import numpy as np
import matplotlib.pyplot as plt

normal_data = np.random.normal(50, 5, 200)
skewed_data = np.random.exponential(10, 200)
```

Create side-by-side boxplots comparing the two distributions. Label each boxplot appropriately (`"Normal"` and `"Exponential"`) and add a title `"Distribution Comparison"`.

Then, add a comment in your code briefly noting which distribution is more skewed, and which descriptive statistic (mean or median) would provide a more appropriate measure of central tendency for each distribution.






### Descriptive Stats Question 5
Print the mean, median, and mode of the following:

data1 = [10, 12, 12, 16, 18]  
data2 = [10, 12, 12, 16, 150]

Why are the median and mean so different for data2? Add your answer as a comment in the code.





## Hypothesis Testing Review

### Hypothesis Question 1

Run an independent samples t-test on the two groups below. Print the t-statistic and p-value.

```python
from scipy import stats

group_a = [72, 68, 75, 70, 69, 73, 71, 74]
group_b = [80, 85, 78, 83, 82, 86, 79, 84]
```

### Hypothesis Question 2

Using the p-value from Q1, write an `if/else` statement that prints whether the result is statistically significant at alpha = 0.05.

### Hypothesis Question 3

Run a paired t-test on the before/after scores below (the same students measured twice). Print the t-statistic and p-value.

```python
before = [60, 65, 70, 58, 62, 67, 63, 66]
after  = [68, 70, 76, 65, 69, 72, 70, 71]
```

### Hypothesis Question 4

Run a one-sample t-test to check whether the mean of `scores` is significantly different from a national benchmark of 70. Print the t-statistic and p-value.

```python
scores = [72, 68, 75, 70, 69, 74, 71, 73]
```

### Hypothesis Question 5

Re-run the test from Q1 as a one-tailed test to check whether `group_a` scores are *less than* `group_b` scores. Print the resulting p-value. Use the `alternative` parameter.

### Hypothesis Question 6

Write a plain-language conclusion for the result of Q1 (do not just say "reject the null hypothesis"). Format it as a `print()` statement. Your conclusion should mention the direction of the difference and whether it is likely due to chance.

## Correlation Review



### Correlation Question 1

Compute the Pearson correlation between `x` and `y` below using `np.corrcoef()`. Print the full correlation matrix, then print just the correlation coefficient (the value at position `[0, 1]`).

```python
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]
```

What do you expect the correlation to be, and why? Add your answer as a comment in the code.

### Correlation Question 2

Use `pearsonr()` from `scipy.stats` to compute the correlation between `x` and `y` below. Print both the correlation coefficient and the p-value.

```python
from scipy.stats import pearsonr

x = [1,  2,  3,  4,  5,  6,  7,  8,  9, 10]
y = [10, 9,  7,  8,  6,  5,  3,  4,  2,  1]
```

### Correlation Question 3

Create the following DataFrame and use `df.corr()` to compute the correlation matrix. Print the result.

```python
people = {
    "height": [160, 165, 170, 175, 180],
    "weight": [55,  60,  65,  72,  80],
    "age":    [25,  30,  22,  35,  28]
}
df = pd.DataFrame(people)
```

### Correlation Question 4

Create a scatter plot of `x` and `y` below, which have a negative relationship. Add a title `"Negative Correlation"` and label both axes.

```python
x = [10, 20, 30, 40, 50]
y = [90, 75, 60, 45, 30]
```

### Correlation Question 5

Using the correlation matrix from Q3, create a heatmap with `sns.heatmap()`. Pass `annot=True` so the correlation values appear in each cell, and add a title `"Correlation Heatmap"`.

Hint:
```python
import seaborn as sns
```

## Pipelines

### Pipeline Question 1

A data pipeline is a sequence of processing steps where each step takes in data, transforms it, and passes the result to the next. You don't need a special framework to build one -- chaining plain functions together is often enough.


Given the array below, which contains some missing values scattered throughout:

```python
arr = np.array([12.0, 15.0, np.nan, 14.0, 10.0, np.nan, 18.0, 14.0, 16.0, 22.0, np.nan, 13.0])
```

Implement the following three functions and then connect them in a `data_pipeline()` function.

- `create_series(arr)` : takes a NumPy array and returns a pandas Series with the name `"values"`.
- `clean_data(series)` : takes the Series, removes any `NaN` values using `.dropna()`, and returns the cleaned Series.
- `summarize_data(series)` -- takes the cleaned Series and returns a dictionary with four keys: `"mean"`, `"median"`, `"std"`, and `"mode"`. For mode, use `series.mode()[0]` to get a single value.
- `data_pipeline(arr)` -- calls the three functions above in sequence and returns the summary dictionary.

Call `data_pipeline(arr)` and print each key and its value from the result.

This is the last answer to put in `warmup_01.py`. Congrats!!!


The next question will be in `prefect_warmup.py`, but will implement the same functionality using Prefect instead of plain Python.

### Pipeline Question 2

The answer to this question should go in `prefect_warmup.py`, not `warmups_01.py`.

Rebuild the pipeline from Q1 using Prefect. Copy your three functions from Pipeline Question 1 (`create_series`, `clean_data`, `summarize_data`) into this file and turn them into Prefect tasks using `@task`.

Turn `data_pipeline()` into a Prefect flow using `@flow`. Inside the flow, call the three tasks in order and return the summary dictionary.

Add this block at the bottom of the file so the flow runs when you execute the script directly:

```python
if __name__ == "__main__":
    pipeline_flow()
```

Run your workflow from the terminal:

```bash
python prefect_warmup.py
```

The summary values should match what you got in Question 1.

Finally, add a comment block at the bottom of `prefect_warmup.py` answering these two questions:

1. This pipeline is simple -- just three small functions on a handful of numbers. Why might Prefect be more overhead than it is worth here?
2. Describe some realistic scenarios where a framework like Prefect could still be useful, even if the pipeline logic itself stays simple like in this case.


# Part 2: Mini-Project: World Happiness Pipeline
In this project, you will build a Prefect pipeline that performs an end-to-end analysis of the World Happiness dataset (the data are located in [assignments/resources/happiness_project](https://github.com/Code-the-Dream-School/python-200/tree/main/assignments/resources/happiness_project)).

In your python-200 homework repo, place your project code in `assignments_01/project_01.py`. Any outputs you generate should be saved in `assignments_01/outputs/`.


## Pre-preprocessing

For data engineers and analysts, data analysis begins before we code. You are not just loading data -- you are telling stories from data that was often collected at great effort and expense. It is important to have some understanding of the data, why it was collected, and what the questions are. What do the numbers represent? What are the features in the dataset actually measuring?

You do not need to do a deep dive. One useful rule of thumb is this: if you can explain to a non-technical friend what the data is about, you are ready to start coding.

This dataset is derived from the World Happiness Report, which uses survey-based measures of life evaluation along with sociocultural and economic indicators such as GDP per capita, health, social support, freedom, generosity, and perceptions of corruption. It allows us to examine what factors are associated with happiness across different countries and regions.

We have data from 2015-2024. This conveniently spans both pre-pandemic and pandemic periods, which allows you to explore potential changes in happiness over time.

### Inspect the Data

First, inspect the data directory. There is a readme that describes the dataset and what it represents. Open one of the data files (such as `world_happiness_2015.csv`) in a plain text editor (not Excel). Read the first 5-10 lines carefully.

Look at how each row is structured. Notice how the columns are separated. Notice what symbol is used for decimal values. Think about how Excel might misinterpret the file. If you were loading this file in pandas, what parameters might you need to pass to `pd.read_csv()` beyond just the filename?

This is your "pre-preprocessing" stage. It is extremely important to look at raw data before writing code. Excel automatically parses files and makes assumptions about structure and formatting. A plain text editor shows you the raw file exactly as it is stored.



## Project Description

Now that you understand the dataset at a high level and have inspected its raw format, you will build a Prefect pipeline that performs a complete multi-year analysis.

Your pipeline should be structured as a series of clearly defined tasks orchestrated inside a single Prefect flow. Each major stage of the analysis should be its own `@task`, and all tasks should be coordinated inside one `@flow`. Use `get_run_logger()` inside every task instead of `print()` -- this is one of the core practices from the lesson, and it means your results will appear in both the terminal and the Prefect dashboard.





### Task 1: Load Multiple Years of Data

Load data from all ten yearly CSV files into a single DataFrame. Your implementation should not duplicate code for each year -- iterate over a list of file paths and load them in a loop.

You discovered some quirks when you inspected the raw files. Make sure you account for those when calling `pd.read_csv()`. There is also something missing from each file that you will need to add before merging: each row needs to know which year it came from. Think about where to add that information.




After loading and merging, save the combined dataset as a CSV so it persists as an output of the pipeline. A sensible default location is `assignments_01/outputs/merged_happiness.csv`, but the exact path and filename are up to you — what matters is that the merged data is written out and that later tasks in the flow use that same merged DataFrame.

Add `retries=3, retry_delay_seconds=2` to this task's decorator. File I/O is exactly the kind of operation that can fail intermittently in production pipelines, and this is where retries earn their keep.



### Task 2: Descriptive Statistics

Compute and log overall descriptive statistics for `happiness_score`: mean, median, and standard deviation.




Then compute and log the mean happiness score grouped by year and by region. Looking at the regional breakdown is often the most interesting part of this dataset -- you may already have a hypothesis about which regions rank highest before you run the numbers.



### Task 3: Visual Exploration



Create and save the following visualizations to `assignments_01/outputs/`:

- A histogram of all happiness scores across all years. Save as `happiness_histogram.png`.
- A boxplot comparing happiness score distributions across years (one box per year). Save as `happiness_by_year.png`.
- A scatter plot showing the relationship between GDP per capita and happiness score. Save as `gdp_vs_happiness.png`.
- A correlation heatmap (using `sns.heatmap()` with `annot=True`) showing the Pearson correlations between all numeric columns. Save as `correlation_heatmap.png`.


Log a message after each plot is saved so you can see the progress in the Prefect dashboard.



### Task 4: Hypothesis Testing

The pandemic began in early 2020. Did it affect global happiness scores? Test this directly: run an independent samples t-test comparing happiness scores from 2019 to 2020.

Log the t-statistic, p-value, the mean happiness for each group, and a plain-language interpretation of the result at alpha = 0.05. Your interpretation should say something meaningful -- not just "we reject the null hypothesis" but what that actually means in terms of this data.






**(Optional)** Add a second test of your choice (for example, comparing two specific regions that you expect to differ based on the descriptive statistics you computed earlier). The pre/post-2020 t-test above is the required part of this task; this second test is encouraged extra practice.



### Task 5: Correlation and Multiple Comparisons

For each numeric explanatory variable, compute the Pearson correlation with happiness score using `scipy.stats.pearsonr` and log the coefficient and p-value.

Each time you run a statistical test at alpha = 0.05, you accept a 5% chance of a false positive -- concluding a relationship is real when it isn't. That's a reasonable risk for a single test. But when you run many tests at once, those small risks add up. If you run 20 independent tests, you'd expect roughly one false positive just by chance, even if none of the relationships are actually real. The more tests you run, the more likely you are to stumble onto something that looks significant but isn't.

This is called the *multiple comparisons problem*, and it's one of the most common sources of misleading findings in data analysis. A simple and widely used fix is the *Bonferroni correction*: divide your significance threshold by the number of tests you ran.

Count how many correlation tests you performed, then compute:

```python
adjusted_alpha = 0.05 / number_of_tests
```

Log which correlations are significant at the original alpha = 0.05, and which remain significant after applying the correction. You may find that some results that looked significant at first don't hold up under the stricter threshold -- that's a useful finding in itself.


### Task 6: Summary Report

Your final task should log a human-readable summary of the key findings from the entire pipeline. Think of it as the "report" step from the lesson -- the thing you'd share with a non-technical colleague. It should include:

- Total number of countries and years in the merged dataset.
- The top 3 and bottom 3 regions by mean happiness score.
- The result of the pre/post-2020 t-test in plain language.
- The variable most strongly correlated with happiness score (after Bonferroni correction).

Log each of these as a separate `logger.info()` message so they're easy to find in the Prefect dashboard.


### Running the Pipeline

Structure your file so that all tasks are called inside a single `@flow` function, and the flow runs when the script is executed directly:

```python
if __name__ == "__main__":
    happiness_pipeline()
```

The full pipeline should be runnable with:

```bash
python project_01.py
```

When you run it, it should execute all tasks in order, produce all outputs, and save them to the locations you chose. You should be able to run the file multiple times without errors -- each run should overwrite the previous outputs cleanly.

Once you have it working, try running `prefect server start` in a separate terminal, then re-run the pipeline and explore the logs and task states in the Prefect dashboard. You'll see exactly what the lesson described.

---

<details>
<summary>Rubric (for AirHub reviewer and mentors)</summary>

### Deliverables

Three files: `warmup_01.py`, `prefect_warmup.py`, and `project_01.py`.

- **`warmup_01.py`** — all Part 1 warmup exercises, each labeled by a comment, each printing its output:
  - Pandas Q1–Q7, NumPy Q1–Q6, Matplotlib Q1–Q4 (plots displayed/saved), Descriptive Stats Q1–Q5 (including the two written-answer comments in Q4 and Q5), Hypothesis Q1–Q6 (Q6 is a plain-language `print()` conclusion), Correlation Q1–Q5.
  - Pipeline Q1: `create_series`, `clean_data`, `summarize_data`, and `data_pipeline` functions, with the summary dict printed key by key.
- **`prefect_warmup.py`** — Pipeline Q2: the three functions as `@task`, `data_pipeline` as a `@flow`, the `if __name__ == "__main__"` block, and the two written answers in a comment block.
- **`project_01.py`** — the World Happiness pipeline: one `@flow` calling Tasks 1–6 as `@task`s, using `get_run_logger()` (not `print()`), runnable with `python project_01.py`.
  - Task 1: load all 10 yearly CSVs in a loop (no per-year copy/paste), add a year column, merge, and write the merged CSV out as an output.
  - Task 2: log mean/median/std of `happiness_score`, plus mean by year and by region.
  - Task 3: save four plots — a happiness histogram, a boxplot by year, a GDP-vs-happiness scatter, and a correlation heatmap (`annot=True`).
  - Task 4: independent-samples t-test 2019 vs 2020, logging t-stat, p-value, group means, and a plain-language interpretation at alpha = 0.05.
  - Task 5: Pearson correlation of each numeric variable with happiness score, plus a Bonferroni-corrected significance check.
  - Task 6: a human-readable summary logging country/year counts, top-3 and bottom-3 regions, the pre/post-2020 result in plain language, and the strongest correlate after correction.

### Required vs optional

**Required:** all three files and every item listed above under Deliverables, including Project Tasks 1–6.

**Optional:**
- Task 4's **second t-test** of the student's choice (the 2019-vs-2020 test is required; the second is extra practice).
- Running `prefect server start` to view the dashboard (a "try this" exploration, not a graded deliverable).

### Strict vs lenient (grading guidance for AirHub)

**Be strict about:**
- The three files existing with the functions/tasks named above present.
- Project Task 3 producing four distinct saved plot files (histogram, by-year boxplot, GDP scatter, correlation heatmap).
- `project_01.py` using `get_run_logger()` rather than `print()`, and structuring the work as `@task`s inside one `@flow`.
- Warmup data being used as given where a question supplies it.

**Be lenient about (do not fail on):**
- **File paths and directory layout.** The `assignments_01/` folder, the `outputs/` subfolder, and the exact merged-CSV path/filename are suggested conventions — the reviewer cannot see the student's filesystem, so do not fail on a path that differs from the examples. What matters is that the merged data is written out and reused within the flow.
- Exact plot **filenames** — the four required plots must exist, but their names need not match the examples verbatim.
- The student's **choice of second t-test** and which regions they compare.
- Cosmetic details of plots (styling, bin counts, colors) beyond the required titles/labels/content.

</details>
