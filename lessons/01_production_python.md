# Week 1: Production Python

Welcome to Python 200! By the end of this course you will have built an AI-enabled data pipeline running in the cloud: it pulls data from a live API, runs it through a machine learning model and a large language model, and writes the results to a cloud database on a schedule.

This week is about the Python skills that make that possible. You already know how to load a CSV file and plot it, because that was covered in Python for Data Analysis and we assume it here. What you have probably not done yet is package your code so that someone else can import it, describe your data so that invalid input fails immediately instead of silently, or write a test that catches a mistake before it reaches production.

Those are the skills that separate a notebook from a working system, and the rest of this course depends on them. Weeks 2 and 3 build a machine learning model. Week 4 turns that model into a reusable component using everything below. Weeks 9 through 11 connect it to a cloud pipeline.

By the end of this week you will be able to:

- Define classes with attributes and methods, and use objects to bundle data with the behavior that belongs to it
- Use `dataclasses`, type hints, and docstrings to write code that documents itself
- Define and validate data schemas at your program's boundaries with Pydantic
- Write `pytest` tests that check both the success path and the failure path
- Split a script into importable modules and a package with a test suite

> For an introduction to the course as a whole, and a discussion of how to set up your environment, please see the [Welcome](../README.md) page.

## Topics

1. [Classes and Objects](01_classes.md)
Dictionaries are a reasonable way to hold data until a program grows. This lesson shows where they become inadequate, then introduces classes, which combine data with the operations that belong to it using `__init__`, attributes, methods, and `self`.

2. [Dataclasses, Type Hints, and Docstrings](02_dataclasses_and_types.md)
Most of the classes you write contain mainly data. The `dataclasses` module removes the repetitive code. Type hints state what a function expects and returns, and docstrings state what those values mean. Together they let your editor, your teammates, and you read your code without running it.

3. [Validating Data at the Boundary](03_pydantic.md)
Type hints are documentation rather than enforcement. When data arrives from outside your program, such as from an API, a CSV file, or a form, you need something that actually checks it. Pydantic turns a schema into a validator, so invalid data fails at the edge of your system instead of several steps later.

4. [Testing with pytest](04_pytest.md)
A test is a small program that runs your code and asserts that something is true about the result. This lesson covers writing test functions, asserting on values, confirming that errors are raised when they should be, and reading pytest output when something fails.

5. [Modules and Project Structure](05_modules.md)
How to turn a single script into a package. Covers modules, imports, the `if __name__ == "__main__"` guard, and a project layout that separates library code from the scripts that use it and the tests that check it.
