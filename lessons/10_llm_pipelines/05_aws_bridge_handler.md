# (Optional) Practicum AWS Bridge, Part 3: The Lambda Handler

> **This lesson is optional this term.** It is part of the Practicum AWS Bridge pilot. You can skip it without any effect on your grade. This lesson uses the settings loader from Part 2 in Week 9.

The Practicum AWS Bridge builds an automatic alert for the Code the Dream teaching team. Every week, a Lambda function calculates the percentage of students who submitted their coding assignment. If fewer than 80% submitted, the team receives an alert.

So far, you have written a checker for the alert's IAM permissions (Week 8) and a function that loads the alert's settings (Week 9). This week, you write the function that AWS actually runs, which is called the **handler**.

## Learning Objectives

By the end of this lesson, you will be able to:

- Explain what a Lambda handler is and what its `event` and `context` arguments contain
- Describe the event that EventBridge Scheduler sends and the event that a Lambda Function URL sends
- Write a handler that returns a Function URL response with `statusCode`, `headers`, and `body`
- Explain where a Lambda function's log lines go, and write one structured log line per run

## What a Handler Is

**AWS Lambda** runs your code without a server that you manage. You upload your Python files, and you tell Lambda which function to call. That function is the handler. A common choice is a function called `lambda_handler` in a file called `handler.py`, which you configure as `handler.lambda_handler`.

Every time something triggers your function, Lambda calls the handler with two arguments:

```python
def lambda_handler(event, context):
    ...
```

- **`event`** is a dictionary that describes why the function is running. Its contents depend on what triggered the function.
- **`context`** is an object with information about the current run, such as a unique request ID and how much time is left before Lambda stops the function. The alert does not use it. In tests, you can pass `None`.

You have seen this pattern before, in a different form. In this week's orchestration lesson, a Prefect `@flow` function called each step of the pipeline in order. A Lambda handler has the same job. It calls the other functions, and it contains very little logic itself. Keeping the logic in small, separate functions makes each piece easy to test.

## Two Ways to Trigger the Alert

The alert can start in two ways, and each way sends a different `event`.

### 1. EventBridge Scheduler

**EventBridge Scheduler** runs a function on a schedule, such as "every Monday at 9 a.m." When you create a schedule, you can give it a JSON input. Scheduler sends that exact input to the function as the `event`. If you give no input, the event is an empty dictionary:

```json
{}
```

A schedule sends the **same** event every time it runs. It cannot send `{"week": 7}` one week and `{"week": 8}` the next. For this reason, a scheduled run of the alert checks the most recent week in the data.

Scheduler calls the function **asynchronously**. This means that Scheduler starts the function and does not wait for the result. Whatever the handler returns is discarded. If the handler raises an exception, Lambda records the error and tries again later.

### 2. A Lambda Function URL

A **Function URL** gives a Lambda function its own web address. When someone sends an HTTP request to that address, Lambda calls the handler. The alert uses a Function URL so that a staff member can check any earlier week by hand.

A Function URL event contains information about the HTTP request. Here is a shortened example:

```json
{
  "version": "2.0",
  "requestContext": {
    "http": { "method": "POST", "path": "/" }
  },
  "headers": { "content-type": "application/json" },
  "body": "{\"week\": 5}",
  "isBase64Encoded": false
}
```

Look carefully at `"body"`. Its value is a **string** that contains JSON, and it is not a dictionary. The handler has to call `json.loads(event["body"])` to read the week. The body can also be empty, or the `"body"` key can be missing, for example when someone sends a request with no data. Use `event.get("body")` so that a missing key does not raise an error.

For a Function URL, the handler's return value matters, because Lambda turns it into the HTTP response. The handler returns a dictionary with three keys:

```python
{
    "statusCode": 200,
    "headers": {"Content-Type": "application/json"},
    "body": json.dumps({"week": 5, "submission_rate": 82.5}),
}
```

`statusCode` is the HTTP status code. `200` means success, and `400` means that the request itself was wrong, for example because the body was not valid JSON. Like the request body, the response body is a JSON **string**, so the handler calls `json.dumps`.

### Telling the two events apart

A Function URL event always has a `"requestContext"` key, which describes the HTTP request. A scheduled event for the alert never has one. The handler uses this difference to decide where to look for the week.

## What the Handler Does

On every run, the alert's handler takes these steps:

1. Read the requested week from the event. A scheduled event has no week.
2. Load the settings with `get_alert_settings()` from Week 9.
3. Fetch the cohort's submissions from the gradebook with the token.
4. Choose the week. Use the requested week, or the most recent week if none was requested.
5. Calculate the submission rate for that week, and compare it with the threshold.
6. Write one log line, and return a response.

For the bridge, Code the Dream's gradebook is replaced by a provided file called `gradebook.py`. Its `fetch_submissions(token)` function checks that a token was given, and then it reads a bundled data file instead of contacting a real server. The data file uses fictional student IDs.

### Counting each student once

Each submission in the data file has a `student_id`, a `week`, and a `submitted_at` time. When a mentor asks for revisions, the student submits again, so some students appear more than once in the same week. To calculate the submission rate correctly, count the **different** students who submitted. A Python `set` does this for you, because a set keeps only one copy of each value.

### Returning an error or raising an exception

The handler handles two kinds of problems differently:

- **The request is wrong**, for example because the body is not valid JSON, or because it asks for a week that has no data yet. Retrying will not help, so the handler returns a response with `statusCode` `400` and a short error message.
- **Something unexpected fails**, for example because the gradebook does not respond. The handler lets the exception happen. Lambda marks the run as failed, the error appears in the logs, and a scheduled run is retried.

## Logging to CloudWatch

On AWS, everything a Lambda function prints or logs goes to **CloudWatch Logs** automatically. You do not need any extra code to send it there. CloudWatch keeps each function's log lines in its own **log group**, such as `/aws/lambda/submission-alert`. You saw this log group in the Week 8 policy.

Plain sentences in a log are hard to search when you have hundreds of runs. A common practice is to log one line of JSON per run, with the important values as fields:

```python
import json
import logging

logger = logging.getLogger("submission_alert")
logger.setLevel(logging.INFO)

logger.info(json.dumps({"week": 7, "submission_rate": 72.5, "below_threshold": True}))
```

CloudWatch can then search these fields directly. For example, you can find every run where `below_threshold` was true.

Give your logger a name, such as `"submission_alert"`. Libraries like `boto3` write their own log lines too, and a name lets you separate your lines from theirs.

### Testing log lines with caplog

pytest provides a fixture called `caplog`, which collects the log lines that your code writes during a test:

```python
def test_handler_logs_one_line(caplog):
    with caplog.at_level("INFO"):
        lambda_handler({}, None)
    mine = [record for record in caplog.records if record.name == "submission_alert"]
    assert len(mine) == 1
```

`record.getMessage()` returns the text of one log line. Because the line is JSON, a test can turn it back into a dictionary with `json.loads` and check its fields.

## Check for Understanding

1. EventBridge Scheduler triggers the alert, and the handler returns `{"statusCode": 400, ...}`. What happens to that response?

    - A. Scheduler retries the function, because the status code is not 200
    - B. Scheduler discards it, because it calls the function asynchronously
    - C. Scheduler emails the response to the account owner
    - D. Lambda raises an error, because scheduled functions cannot return a value

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. Scheduler starts the function and does not wait for the result, so the return value is not used. Only an exception tells Lambda that a scheduled run failed. This is why the handler raises an exception for unexpected failures.
    </details>

2. A Function URL event contains `"body": "{\"week\": 3}"`. What does `event["body"]["week"]` do?

    - A. It returns `3`
    - B. It returns `"3"`
    - C. It raises a `TypeError`, because `event["body"]` is a string
    - D. It returns `None`

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: C. The body is a string that contains JSON. Python cannot index a string with <code>"week"</code>, so it raises a <code>TypeError</code>. Call <code>json.loads(event["body"])</code> first, and then read <code>"week"</code> from the dictionary it returns.
    </details>

3. In one week, 40 rows in the data have `"week": 2`, but three students submitted twice. The roster has 40 students. What is the correct submission rate?

    - A. 100.0%
    - B. 92.5%
    - C. 107.5%
    - D. 85.0%

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. There are 40 rows, but only 37 different students, because three students appear twice. 37 out of 40 is 92.5%. Counting rows instead of students would report 100%.
    </details>

## Lesson Wrap-Up

A Lambda handler is the function that AWS calls, with an `event` that describes the trigger and a `context` that describes the run. EventBridge Scheduler sends a fixed JSON input, often `{}`, and ignores the return value. A Function URL sends an HTTP request with a JSON string in `body`, and it uses the returned `statusCode`, `headers`, and `body` as the HTTP response. The handler returns a `400` response for a bad request and raises an exception for an unexpected failure. Everything the function logs goes to CloudWatch Logs, where one JSON line per run is easy to search.

In Week 11, the bridge ends with assembly. The handler will send the submission rate to CloudWatch as a metric, and a CloudWatch alarm will watch it. You will also test the whole alert end to end on your own computer.
