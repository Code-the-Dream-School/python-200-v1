# Lessons

As described on the [course home page](../README.md), Python 200 covers production Python,
machine learning, AI, and cloud computing. This page
is your home base for the lessons themselves -- you will find links to content for each week below, and instructions for setting up your development environment further down.

## Lessons by week

1. [Week 1: Production Python](01_production_python.md)
2. [Week 2: Supervised Machine Learning — Regression](02_ML_intro.md)
3. [Week 3: Classification and Model Deployment](03_ML_classification.md)
4. [Week 4: From Model to Reusable Component](04_applied_ML.md)
5. [Week 5: Introduction to AI](05_AI_intro.md)
6. [Week 6: Augmenting AI: From Memory to Retrieval](06_AI_augmentation.md)
7. [Week 7: AI Agents](07_AI_agents.md)
8. [Week 8: Introduction to Cloud Computing](08_cloud_intro.md)
9. [Week 9: Data in the Cloud](09_cloud_AI.md)
10. [Week 10: LLMs in Pipelines](10_cloud_ML.md)
11. [Week 11: Cloud ETL](11_cloud_ETL.md)

Each week's lessons are in their own directory, split into multiple shorter lessons in individual markdown files. The linked overview page for each week (above) gives a brief introduction to the week's topics and a table of contents for its lessons. For each week, we recommend that you start with the overview to get your bearings, then work through the lessons in order.

> Tip: to read Markdown files with full formatting in VS Code, open the file and press
> `Ctrl+Shift+V` (Windows/Linux) or `Cmd+Shift+V` (Mac), or click the preview icon in
> the top-right corner of the editor (the little document with the magnifying glass).

## Setting up

### Getting the course materials

Fork the [course repo](https://github.com/Code-the-Dream-School/python-200) on GitHub,
then clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/python-200.git
cd python-200
```

Add the course repo as an upstream remote so you can pull updates as new lessons are
released throughout the course:

```bash
git remote add upstream https://github.com/Code-the-Dream-School/python-200.git
```

To pull in new lessons or updates:

```bash
git pull upstream main
```

One important note: as you likely did with Python 100, you will probably want to keep a separate working directory outside the repo -- something like `p200_working/`. This is a place you will be able to save jupytext output (see below), and any other files you generate while working through the course. This keeps your fork clean and avoids accidentally committing generated files or triggering unwanted pull requests. Alternatively, if you prefer to keep your working directory inside the repo, you can add it to `.git/info/exclude` -- this tells Git to ignore it locally without modifying `.gitignore`, so it won't affect other contributors.

## Package management with uv

We recommend that you use [uv](https://docs.astral.sh/uv/) as a one-stop shop for managing your Python programming environment: it installs Python itself, manages virtual environments, and installs packages -- all with a single tool. Written in Rust, it is 10-100x faster than pip at resolving and installing dependencies. More importantly, it replaces the old tangle of pip, pyenv, and conda with a single, consistent workflow. No more version conflicts, no more "which Python is this?" confusion.

uv has rapidly become the standard tool for Python project management.

### Installing uv

Follow the [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/)
for your OS. The quick version (Windows users: run this in Git Bash):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal after installing, then verify:

```bash
uv --version
```

### Setting up the course environment

From the root of the cloned repo, create a virtual environment that includes Python 3.12 (one of the nice things about uv is you can specify the specific Python version you want: you are not locked to your system Python version): 

```bash
uv venv --python 3.12
```

Activate it:

```bash
source .venv/bin/activate        # Mac / Linux
source .venv/Scripts/activate    # Windows (Git Bash)
```

Depending on your settings in VS Code, you may need to activate the environment each time you open a new terminal in this project.

Install all course dependencies:

```bash
uv pip install -r requirements.txt
```

You should be good to go!

If you run into any installation issues or something breaks after an update, please
open an issue on the [course repo](https://github.com/Code-the-Dream-School/python-200).
We actively maintain this environment and will update `requirements.txt` as needed.

### Jupyter notebooks and jupytext

Lessons in this course are written as Markdown files (`.md`), which are easy to read in
GitHub and in VS Code. When you want to run the code interactively, you can convert a
lesson to a Jupyter notebook using [jupytext](https://jupytext.readthedocs.io/), which is
included in the course environment. For instance, to convert the first Week 1 lesson to a Jupyter notebook:

```bash
jupytext --to notebook --output ~/p200_working/01_classes.ipynb lessons/01_production_python/01_classes.md
```

This creates a `.ipynb` file in your working directory that you can open in JupyterLab or VS Code.

All our Markdown lessons are written so they should run successfully when converted to Jupyter notebooks using jupytext. Please let us know if there are any problems.

## You're all set!

That's everything you need to get started. Work through each week in order, run the code, break things, and ask questions of your mentors -- that's how we all learn. Good luck!

