# (Optional) Practicum AWS Bridge, Part 1: IAM Permissions

> **This lesson is optional this term.** The Practicum AWS Bridge is a new set of four short lessons, one each week from Week 8 to Week 11. We are running it as a pilot. You can skip it without any effect on your grade. If you do it, your feedback will help us improve it before we add it to the main course.

The practicum that follows this course deploys a pipeline on AWS. In the previous lesson, you read a short description of the AWS services the practicum uses: Lambda, EventBridge, IAM, CloudWatch, and Parameter Store. The Practicum AWS Bridge gives you hands-on practice with those services before the practicum starts, so that their names and their main ideas are familiar.

You do not need an AWS account for any part of the bridge. Everything runs on your own computer.

## Learning Objectives

By the end of this lesson, you will be able to:

- Explain what IAM is and what an IAM role does for a Lambda function
- Read an IAM policy document and identify its `Effect`, `Action`, and `Resource` fields
- Explain how AWS combines Allow and Deny statements to make a decision
- Explain the principle of least privilege and recognize a policy that breaks it

## The Bridge Mini-Project

Each week of the bridge builds one piece of a small, realistic AWS feature. This feature is separate from the weather pipeline you build in Weeks 9 to 11.

**The scenario:** Code the Dream wants an automatic alert for its teaching team. Every week, after the assignment deadline, a Lambda function will calculate the percentage of students who submitted their coding assignment. If fewer than 80% of students submitted, the team receives an alert, so that mentors can contact students who may need help.

Over four weeks, you will build this feature one piece at a time:

| Week | Topic | What you build |
|---|---|---|
| 8 | IAM permissions | A checker that reads the alert's permission policy and decides whether an action is allowed |
| 9 | Secrets and settings | A function that loads the alert's settings safely from the environment or from Parameter Store |
| 10 | The Lambda handler | The function that AWS runs on a schedule, which calculates the submission rate |
| 11 | Assembly | A CloudWatch metric and alarm for the alert, and tests that run the whole feature on your computer |

This week, you start with permissions, because every AWS service checks permissions before it does anything else.

## What IAM Is

**IAM** (Identity and Access Management) is the AWS service that decides who can do what. Every request to AWS, such as "read this setting" or "write this log line," goes through IAM first. If IAM does not allow the request, AWS rejects it.

IAM uses three terms that you will see often:

- A **principal** is whoever makes a request. A principal can be a person who logs in, or it can be a piece of software, such as a Lambda function.
- A **policy** is a JSON document that lists permissions. Each permission says which actions are allowed or denied, and on which resources.
- A **role** is an identity that a piece of software uses. You attach policies to a role. When a Lambda function runs, it uses its role, and it receives exactly the permissions in that role's policies.

A role is how you avoid putting passwords in your code. In this week's assignment, you store your Supabase key in a `.env` file. A Lambda function on AWS does not need a key to call other AWS services, because its role already gives it permission. This role is called the function's **execution role**.

## Reading a Policy Document

Here is one permission from the submission alert's policy. Read it before you continue.

Example — this is one statement from the provided policy file:

```json
{
  "Sid": "ReadAlertSettings",
  "Effect": "Allow",
  "Action": ["ssm:GetParameter", "ssm:GetParameters"],
  "Resource": "arn:aws:ssm:us-east-1:123456789012:parameter/ctd/submission-alert/*"
}
```

A policy contains a list of these objects under the key `"Statement"`. Each statement has four fields:

- **`Sid`** (statement ID) is a label for humans. AWS does not use it to make decisions.
- **`Effect`** is either `"Allow"` or `"Deny"`.
- **`Action`** names one or more operations. An action has the form `service:Operation`. For example, `ssm:GetParameter` means "read one setting from Parameter Store." (Parameter Store is part of a service called Systems Manager, so its actions start with `ssm`.)
- **`Resource`** names the specific things the statement applies to.

`Action` and `Resource` can each be a single string or a list of strings. Your code will need to handle both forms.

### Resources are named with ARNs

AWS gives every resource a unique name called an **ARN** (Amazon Resource Name). An ARN is a string of parts separated by colons:

```
arn:aws:ssm:us-east-1:123456789012:parameter/ctd/submission-alert/threshold
    |   |   |         |            |
    |   |   region    account ID   the resource inside the service
    |   service
    partition (almost always "aws")
```

The account ID `123456789012` is the standard placeholder that AWS uses in its own documentation. It is not a real account.

### Wildcards

A `*` in an action or resource matches any sequence of characters. A `?` matches exactly one character.

- `ssm:Get*` matches `ssm:GetParameter`, `ssm:GetParameters`, and `ssm:GetParameterHistory`.
- `.../parameter/ctd/submission-alert/*` matches every setting whose name starts with `/ctd/submission-alert/`.
- A `Resource` of `"*"` by itself matches every resource.

One more detail matters when you compare strings. AWS treats **action names as case-insensitive**, so `SSM:getparameter` and `ssm:GetParameter` are the same action. AWS treats **ARNs as case-sensitive**, so `.../Threshold` and `.../threshold` are different resources.

## How AWS Makes a Decision

A role can have many statements, and some of them can disagree. AWS uses three rules, in this order, to decide whether a request is allowed:

1. **If any matching statement has `"Effect": "Deny"`, the request is denied.** This is called an **explicit deny**. A Deny always wins, even if another statement allows the same request.
2. **Otherwise, if any matching statement has `"Effect": "Allow"`, the request is allowed.**
3. **Otherwise, the request is denied.** This is called an **implicit deny**. Everything starts out denied, and a request is allowed only if a statement allows it.

A statement "matches" a request when its `Action` matches the requested action **and** its `Resource` matches the requested resource.

Here is how the three rules work for the submission alert's policy. The policy allows reading settings under `/ctd/submission-alert/`, and it denies everything under `/ctd/submission-alert/admin/`.

| Request | Matching statements | Decision |
|---|---|---|
| `ssm:GetParameter` on `.../submission-alert/threshold` | One Allow | Allowed |
| `ssm:GetParameter` on `.../submission-alert/admin/override` | One Allow and one Deny | Explicit deny |
| `ssm:PutParameter` on `.../submission-alert/threshold` | None | Implicit deny |

The second row is the important one. The Allow statement matches, because `admin/override` starts with `submission-alert/`. The Deny statement also matches, and a Deny always wins.

The real IAM system has more features than these three rules. For example, statements can include conditions such as "only during business hours," and AWS also checks policies attached to the resource itself. You will not need these features in the bridge, and the practicum does not depend on them. The three rules above are the core of every IAM decision.

## Least Privilege

The **principle of least privilege** says that each role should have only the permissions it needs to do its job, and nothing more.

Compare these two statements. Both of them would let the submission alert read its settings.

Example — a policy that breaks least privilege:

```json
{ "Effect": "Allow", "Action": "*", "Resource": "*" }
```

Example — a policy that follows least privilege:

```json
{
  "Effect": "Allow",
  "Action": "ssm:GetParameter",
  "Resource": "arn:aws:ssm:us-east-1:123456789012:parameter/ctd/submission-alert/*"
}
```

The first statement allows every action on every resource in the account. Suppose someone found a bug in the alert function and used it to run their own code. That code could then delete databases, read private files, or create expensive servers. The second statement limits the damage to reading a few alert settings.

Sometimes AWS does not let you narrow a permission as much as you would like. The CloudWatch action `cloudwatch:PutMetricData` sends a number, such as a submission rate, to CloudWatch. This action does not support resource ARNs, so its statement must use `"Resource": "*"`. In this case, least privilege means that you allow only that one action, even though you cannot limit the resource.

## Checking Policies in Python

A policy is JSON, so Python can read it with the `json` module. The result is an ordinary dictionary:

```python
import json

with open("submission_alert_policy.json") as f:
    policy = json.load(f)

for statement in policy["Statement"]:
    print(statement["Sid"], statement["Effect"], statement["Action"])
```

To compare a requested action or resource with a pattern that contains `*` or `?`, use `fnmatchcase` from the standard library's `fnmatch` module. It returns `True` if the string matches the pattern:

```python
from fnmatch import fnmatchcase

fnmatchcase("ssm:GetParameter", "ssm:Get*")    # True
fnmatchcase("ssm:PutParameter", "ssm:Get*")    # False
fnmatchcase("ssm:getparameter", "ssm:Get*")    # False, because the case differs
```

`fnmatchcase` is always case-sensitive. That is correct for ARNs. For actions, convert both strings to lowercase before you compare them.

In this week's optional assignment, you will use these two tools to write a policy checker. You will also use the checker in Week 11 as a safety test. Before a team deploys the alert, the test confirms that the alert's role can do everything the alert needs, and nothing more.

## Check for Understanding

1. A Lambda function's role has two statements. One allows `s3:GetObject` on `arn:aws:s3:::reports/*`. The other denies `s3:*` on `arn:aws:s3:::reports/private/*`. The function requests `s3:GetObject` on `arn:aws:s3:::reports/private/salaries.csv`. What happens?

    - A. The request is allowed, because a statement allows `s3:GetObject`
    - B. The request is denied with an explicit deny
    - C. The request is denied with an implicit deny
    - D. AWS uses whichever statement appears first in the policy

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. Both statements match the request. When any matching statement is a Deny, the request is denied, and the order of the statements does not matter.
    </details>

2. A role has one statement, which allows `dynamodb:GetItem` on one table. The function requests `dynamodb:DeleteItem` on that table. What happens?

    - A. The request is allowed, because the role has access to the table
    - B. The request is denied with an explicit deny
    - C. The request is denied with an implicit deny
    - D. AWS raises an error, because the policy does not mention `DeleteItem`

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: C. No statement matches <code>dynamodb:DeleteItem</code>, so nothing allows it. AWS denies every request that no statement allows.
    </details>

3. Why does a Lambda function on AWS not need an access key in a `.env` file to call other AWS services?

    - A. AWS services do not check permissions for Lambda functions
    - B. The function uses its execution role, and the role's policies give it permission
    - C. Lambda functions read the developer's personal access key automatically
    - D. The access key is stored in the policy document

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. AWS gives the function temporary permissions through its execution role. The role's policies decide what the function can do, so no key needs to be stored in the code or in a file.
    </details>

## Lesson Wrap-Up

IAM decides whether every AWS request is allowed. A policy is a JSON list of statements, and each statement has an `Effect`, an `Action`, and a `Resource`. AWS denies a request if any matching statement denies it, allows it if a matching statement allows it, and denies it in every other case. Good policies follow least privilege, which means that they allow only what a role needs.

In Week 9, the bridge continues with secrets and settings. You will write the function that loads the alert's settings, first from environment variables and then from AWS Parameter Store, using a local stand-in for AWS.
