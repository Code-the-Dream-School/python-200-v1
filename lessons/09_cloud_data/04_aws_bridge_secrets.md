# (Optional) Practicum AWS Bridge, Part 2: Settings and Secrets

> **This lesson is optional this term.** It is part of the Practicum AWS Bridge pilot. You can skip it without any effect on your grade. Part 1 was in Week 8, but you do not need Part 1 to follow this lesson.

The Practicum AWS Bridge builds a small AWS feature, one piece each week. The feature is an automatic alert for the Code the Dream teaching team. Every week, a Lambda function calculates the percentage of students who submitted their coding assignment. If fewer than 80% submitted, the team receives an alert.

In Week 8, you wrote a checker for the alert's IAM permissions. This week, you write the code that loads the alert's settings. You also take your first step with `boto3`, the AWS library for Python, and with `moto`, a library that runs a fake version of AWS on your computer.

## Learning Objectives

By the end of this lesson, you will be able to:

- Explain the difference between a setting and a secret, and where each one belongs on AWS
- Describe AWS Systems Manager Parameter Store, and the difference between a `String` and a `SecureString` parameter
- Read a parameter with `boto3` and handle a missing parameter
- Test AWS code on your own computer with `moto` and pytest's `monkeypatch` fixture

## The Alert's Two Settings

The alert needs two values to run:

- **`gradebook_token`** is a password-like string. The alert uses it to read submission data from Code the Dream's gradebook system. Anyone who has this token can read every student's submission history, so it is a **secret**.
- **`submission_threshold`** is the percentage below which the team receives an alert, such as `80`. It is useful to change it without changing code, but nobody can misuse it. It is a **setting**, and it is not a secret.

You already know one way to keep values like these out of your code. In this week's main lessons, you stored your Supabase credentials in a `.env` file and loaded them with `load_dotenv()`. That works on your own computer. A Lambda function runs on AWS, though, and AWS does not have your `.env` file. On AWS, the alert has two other places to read its settings from.

### Option 1: Lambda environment variables

When you deploy a Lambda function, you can give it environment variables. The function reads them with `os.environ`, in the same way your scripts read the values that `load_dotenv()` loaded. Environment variables are a good fit for settings such as `submission_threshold`.

Environment variables are a poor fit for secrets. Anyone who can view the function's configuration in the AWS console can read them in plain text.

### Option 2: AWS Systems Manager Parameter Store

**Parameter Store** is an AWS service that stores named values, called **parameters**. It is part of a larger service called **Systems Manager**, so its code and its IAM actions use the short name `ssm`.

Parameter names look like file paths. The alert keeps its parameters under one prefix:

```
/ctd/submission-alert/gradebook_token
/ctd/submission-alert/submission_threshold
```

A shared prefix keeps related parameters together. It also lets an IAM policy grant access to all of them with one wildcard, as you saw in Week 8: `.../parameter/ctd/submission-alert/*`.

Each parameter has a type. The two types you will use are:

- **`String`** stores the value as plain text. Use it for settings.
- **`SecureString`** stores the value in encrypted form. When you read it, you choose whether AWS should decrypt it for you. Use it for secrets.

### The order the alert checks

The alert's code checks the two places in this order:

1. If the environment variable exists and is not empty, use it.
2. Otherwise, read the parameter from Parameter Store.
3. If neither exists, stop with a clear error message.

Checking the environment first is useful in two situations. During development, you can set an environment variable on your own computer and run the code without contacting AWS. On AWS, an administrator can override one parameter temporarily by setting an environment variable on the function.

Environment variable names are usually uppercase, so the code uses `name.upper()`. The setting `gradebook_token` comes from the environment variable `GRADEBOOK_TOKEN`.

## Reading a Parameter with boto3

**`boto3`** is the official AWS library for Python. You use it by creating a **client** for one AWS service. Then you call methods on the client:

```python
import boto3

ssm = boto3.client("ssm", region_name="us-east-1")

response = ssm.get_parameter(
    Name="/ctd/submission-alert/gradebook_token",
    WithDecryption=True,
)
print(response["Parameter"]["Value"])
```

Notice three things about this code.

First, the method name matches the IAM action. `ssm.get_parameter(...)` is the `ssm:GetParameter` action from your Week 8 policy. Every `boto3` method call is one request to AWS, and IAM checks every request.

Second, `boto3` returns an ordinary Python dictionary. The value you want is inside `response["Parameter"]["Value"]`.

Third, `WithDecryption=True` asks AWS to decrypt a `SecureString` before returning it. Without it, you receive the encrypted text. That text is a long string that looks random, and Python does not raise an error. Your code would continue with a token that does not work, which is hard to debug. For a `String` parameter, `WithDecryption` makes no difference, so it is safe to always pass `True`.

### When the parameter does not exist

If no parameter has the name you asked for, `get_parameter` raises an exception. `boto3` creates its exception classes at run time, so you find them on the client, under `client.exceptions`:

```python
try:
    response = ssm.get_parameter(Name="/ctd/submission-alert/missing", WithDecryption=True)
except ssm.exceptions.ParameterNotFound:
    print("That parameter does not exist.")
```

Catching this specific exception, and then raising your own exception with a clear message, makes the problem easy to fix. A message such as "Set the environment variable GRADEBOOK_TOKEN or create the parameter /ctd/submission-alert/gradebook_token" tells the reader exactly what to do.

### Let the caller pass in a client

A function that reads a parameter can create its own client, or the caller can give it one. Many AWS functions accept an optional client argument, for two reasons:

```python
def get_setting(name, ssm_client=None):
    ...
    if ssm_client is None:
        ssm_client = boto3.client("ssm", region_name="us-east-1")
```

- A test can pass in a client that it controls.
- The function creates a client only when it needs one. If the environment variable exists, the function returns early and never contacts AWS.

## Testing AWS Code Without AWS

You do not have an AWS account for this course, and tests should not depend on a real cloud service anyway. Real calls are slow, they can cost money, and they can fail for reasons that have nothing to do with your code.

**`moto`** solves this problem. It runs a fake version of AWS inside your Python process. While moto is active, every `boto3` call goes to the fake AWS instead of the real one. The fake AWS starts empty every time, so each test begins from a known state.

Install both libraries in your course environment:

```bash
uv pip install boto3 "moto[ssm]"
```

### mock_aws

`mock_aws` turns moto on. Use it as a `with` block. Create your clients **inside** the block, so that they talk to the fake AWS:

```python
import boto3
from moto import mock_aws

with mock_aws():
    ssm = boto3.client("ssm", region_name="us-east-1")
    ssm.put_parameter(
        Name="/ctd/submission-alert/submission_threshold",
        Value="80",
        Type="String",
    )
    response = ssm.get_parameter(Name="/ctd/submission-alert/submission_threshold")
    print(response["Parameter"]["Value"])  # 80
```

`put_parameter` creates a parameter. In a real AWS account, an administrator usually creates parameters once, in the console. In a test, you create them yourself, so that the code under test has something to read.

moto supplies fake credentials while it is active, so you do not need an AWS key. You do need to choose a region, because AWS needs one for every request.

### A pytest fixture for the fake AWS

In Week 1, you used fixtures to share setup between tests. A fixture that uses `yield` can also run cleanup code after each test. Everything before `yield` is setup, and everything after it runs when the test finishes. This makes a fixture a natural place for `mock_aws`:

```python
import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def ssm(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.delenv("GRADEBOOK_TOKEN", raising=False)
    monkeypatch.delenv("SUBMISSION_THRESHOLD", raising=False)
    with mock_aws():
        yield boto3.client("ssm", region_name="us-east-1")
```

Each test that asks for `ssm` receives a client for a new, empty Parameter Store. The two `delenv` lines are explained in the next section. When the test ends, the `with` block ends, and moto turns itself off.

### monkeypatch

The fixture above asks for another fixture, called `monkeypatch`, which pytest provides. `monkeypatch` changes something for the length of one test and then puts it back automatically. Three of its methods are useful this week:

- `monkeypatch.setenv("NAME", "value")` sets an environment variable.
- `monkeypatch.delenv("NAME", raising=False)` removes an environment variable. `raising=False` means "do not raise an error if it was not set."
- `monkeypatch.setattr("module.name", replacement)` replaces a function or an object for one test.

Environment variables are a common cause of tests that pass on one computer and fail on another. If your own shell happens to have `GRADEBOOK_TOKEN` set, a test that expects Parameter Store to be used would read your real value instead. Removing these variables with `delenv` at the start of the fixture prevents this problem.

## Check for Understanding

1. Why is a `SecureString` parameter a better place for `gradebook_token` than a Lambda environment variable?

    - A. Environment variables cannot hold long strings
    - B. Anyone who can view the function's configuration can read its environment variables in plain text
    - C. `boto3` cannot read environment variables
    - D. A `SecureString` parameter is faster to read

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. Environment variables are visible in the function's configuration. A <code>SecureString</code> is stored encrypted, and reading it requires permission to call <code>ssm:GetParameter</code> on that specific parameter.
    </details>

2. Your code calls `ssm.get_parameter(Name="/ctd/submission-alert/gradebook_token")` without `WithDecryption=True`, and the parameter is a `SecureString`. What happens?

    - A. `boto3` raises an error
    - B. The call returns the decrypted token
    - C. The call returns the encrypted text, and Python raises no error
    - D. The call returns `None`

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: C. AWS returns the encrypted form of the value. Your code continues with a value that looks like a token but does not work. This is why the alert always passes <code>WithDecryption=True</code>.
    </details>

3. A test creates its `boto3` client **before** it enters `with mock_aws():`. What is the risk?

    - A. There is no risk, because moto intercepts every client
    - B. The client might send its requests to real AWS instead of the fake AWS
    - C. moto raises an error as soon as it starts
    - D. The client cannot create parameters

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. Create every client inside the <code>mock_aws</code> block, or inside a fixture that starts moto first. That way, every request goes to the fake AWS.
    </details>

## Lesson Wrap-Up

A Lambda function cannot read your `.env` file, so it reads its settings from Lambda environment variables or from Parameter Store. Settings can be environment variables or `String` parameters, and secrets belong in `SecureString` parameters. You read a parameter with `boto3` by calling `get_parameter` with `WithDecryption=True`, and you catch `client.exceptions.ParameterNotFound` when it is missing. To test this code without an AWS account, `moto` provides a fake AWS, and pytest's `monkeypatch` fixture controls the environment variables for each test.

In Week 10, the bridge continues with the Lambda handler: the function that AWS runs on a schedule, which uses these settings to calculate the submission rate.
