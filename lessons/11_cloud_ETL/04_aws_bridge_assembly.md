# (Optional) Practicum AWS Bridge, Part 4: Assembly

> **This lesson is optional this term.** It is the last part of the Practicum AWS Bridge pilot. You can skip it without any effect on your grade. This lesson uses the code from Parts 1 to 3, in Weeks 8 to 10.

The Practicum AWS Bridge builds an automatic alert for the Code the Dream teaching team. Every week, a Lambda function calculates the percentage of students who submitted their coding assignment. If fewer than 80% submitted, the team receives an alert.

You have built three pieces so far:

- **Week 8:** a checker that decides whether the alert's IAM policy allows a request
- **Week 9:** a function that loads the alert's settings from the environment or from Parameter Store
- **Week 10:** the Lambda handler, which calculates the submission rate for a scheduled run or a manual check

This week, you add the last piece, which is the alert itself. The handler sends the submission rate to **CloudWatch** as a metric, and a CloudWatch **alarm** watches that metric. Then you test the whole feature on your own computer, and you use your Week 8 checker to confirm that the alert's role has exactly the permissions it needs.

## Learning Objectives

By the end of this lesson, you will be able to:

- Explain what a CloudWatch metric is, and publish one with `boto3`
- Explain how a CloudWatch alarm watches a metric, and define one with `boto3`
- Write an end-to-end test that runs AWS code against a fake AWS with `moto`
- Explain what a local test can confirm, and what only a real deployment can confirm

## CloudWatch Metrics

In Week 10, you learned that CloudWatch collects a Lambda function's log lines. CloudWatch also collects **metrics**. A metric is a series of numbers over time, such as "the submission rate, measured once a week."

Every data point in a metric has these parts:

- A **namespace**, which groups related metrics. The alert uses `CTD/Submissions`.
- A **metric name**, such as `SubmissionRate`.
- **Dimensions**, which are name-value pairs that tell similar data points apart. The alert uses one dimension, `Cohort`, so that each cohort has its own series of numbers.
- A **value**, such as `72.5`, and a **unit**, such as `Percent`.

The `boto3` method that sends a data point is `put_metric_data`. It is the `cloudwatch:PutMetricData` action from your Week 8 policy:

```python
import boto3

cloudwatch = boto3.client("cloudwatch", region_name="us-east-1")
cloudwatch.put_metric_data(
    Namespace="CTD/Submissions",
    MetricData=[
        {
            "MetricName": "SubmissionRate",
            "Value": 72.5,
            "Unit": "Percent",
            "Dimensions": [{"Name": "Cohort", "Value": "python200-fall-2026"}],
        }
    ],
)
```

### Publish only on scheduled runs

The handler publishes the metric only when the run was scheduled. A manual check through the Function URL does not publish anything.

The reason is that the alarm treats every data point as the current week's result. Suppose a staff member checks week 2 by hand on a Tuesday. If the handler published that 92.5%, the alarm would see a high rate that has nothing to do with this week. Manual checks are for looking at data, and only the schedule feeds the alarm.

## CloudWatch Alarms

A CloudWatch **alarm** watches one metric and compares it with a threshold. You define an alarm with these settings:

- **The metric to watch.** The namespace, metric name, and dimensions must match the published data points exactly. If one dimension is different, the alarm watches an empty metric.
- **`Statistic` and `Period`.** CloudWatch groups the data points into time periods, and it calculates one number per period. The alarm uses `Minimum` over one day (`86400` seconds). The alert publishes one data point per week, so the minimum is that data point.
- **`Threshold` and `ComparisonOperator`.** The alarm uses a threshold of `80` and `LessThanThreshold`.
- **`EvaluationPeriods`.** This is the number of periods in a row that must cross the threshold. The alarm uses `1`.
- **`TreatMissingData`.** Most days have no data point, because the alert runs once a week. The value `notBreaching` tells CloudWatch to treat a day without data as "fine."

An alarm is always in one of three states: `OK`, `ALARM`, or `INSUFFICIENT_DATA`. When the state changes to `ALARM`, the alarm can run **actions**. The most common action sends an email or a chat message through another AWS service. Setting up those actions is outside the bridge, so the alarm's state is the result you will study.

### Who creates the alarm

The Lambda function runs every week, but the alarm needs to be created only once. A team member creates it, or a deployment script does. The Lambda function never creates it.

This affects permissions. The function's role needs `cloudwatch:PutMetricData` to publish the rate. It does not need `cloudwatch:PutMetricAlarm`, because it never creates an alarm. Following least privilege, the role should not have that permission. Your Week 8 policy already follows this rule, and this week you write a test that confirms it.

## Testing the Whole Alert

In Week 9, you used `moto` to test the settings loader against a fake Parameter Store. moto also provides a fake CloudWatch, so you can test the whole alert in one test:

1. Start moto, and create the two parameters, as an administrator would do once.
2. Call `lambda_handler({}, None)`, as EventBridge Scheduler would.
3. Read the metric back from the fake CloudWatch, and check its value.

To read a metric, use `get_metric_statistics`. It returns the data points in a time range, grouped by period:

```python
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
stats = cloudwatch.get_metric_statistics(
    Namespace="CTD/Submissions",
    MetricName="SubmissionRate",
    Dimensions=[{"Name": "Cohort", "Value": "python200-fall-2026"}],
    StartTime=now - timedelta(hours=1),
    EndTime=now + timedelta(hours=1),
    Period=3600,
    Statistics=["Minimum"],
)
print([point["Minimum"] for point in stats["Datapoints"]])  # [72.5]
```

### What moto does not do

moto stores the alarms you create, and `describe_alarms` returns them with all their settings. However, **moto does not evaluate alarms.** Its alarms stay in the `OK` state, even when the metric is below the threshold. On AWS, CloudWatch checks the metric for you and changes the state.

This means that your tests can confirm two separate facts:

- The handler publishes the correct number to the correct metric.
- The alarm watches that metric, with the correct threshold and comparison.

If both facts are true, the alarm will fire on AWS. The tests cannot confirm that last step directly, and that is a normal limit of local tests.

### A permission test before deployment

moto also does not check IAM permissions by default. A test that passes in moto does not prove that the deployed function is allowed to make its calls. This is where your Week 8 checker is useful.

A **pre-deploy test** lists every AWS call the handler makes, and it asks the checker whether the policy allows each one. It also lists calls the handler never makes, and it confirms that the policy does not allow them:

```python
NEEDED = [
    ("ssm:GetParameter", PARAM + "gradebook_token"),
    ("cloudwatch:PutMetricData", "*"),
    ...
]
NOT_NEEDED = [
    ("cloudwatch:PutMetricAlarm", "*"),
    ...
]
```

If someone later adds a new AWS call to the handler and forgets to update the policy, the `NEEDED` test fails. If someone adds a broad permission to the policy, the `NOT_NEEDED` test can fail. Teams often run checks like this automatically before every deployment.

## From the Bridge to the Practicum

In the practicum, you will deploy code like this to a real AWS account. Most of your code does not change, because the `boto3` calls you wrote are real AWS calls. What changes is the setup around the code:

| On your computer | On AWS |
|---|---|
| `mock_aws()` provides a fake AWS | Real AWS services, in a real account |
| Tests call `lambda_handler({}, None)` | EventBridge Scheduler calls the handler on a schedule |
| The test fixture creates the parameters | An administrator creates the parameters once |
| `create_low_submission_alarm` runs in a test | A team member or a deployment script creates the alarm once |
| The Week 8 checker reads `submission_alert_policy.json` | AWS IAM applies the policy attached to the function's role |
| moto never changes the alarm's state | CloudWatch sets the alarm to `ALARM` when the rate is low |

The Week 11 lesson on production patterns has a similar table for the weather pipeline. It shows how Prefect's flows, retries, and logs map onto Lambda, EventBridge, and CloudWatch.

## Check for Understanding

1. Your end-to-end test publishes a rate of `72.5`, and the alarm's threshold is `80`. The test then calls `describe_alarms` in moto. What is the alarm's state?

    - A. `ALARM`, because 72.5 is less than 80
    - B. `OK`, because moto does not evaluate alarms
    - C. `INSUFFICIENT_DATA`, because the period is one day
    - D. moto raises an error, because it does not support alarms

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. moto stores the alarm's settings but never changes its state. This is why the tests check the published value and the alarm's settings separately.
    </details>

2. Why does the alert's role not have the `cloudwatch:PutMetricAlarm` permission?

    - A. AWS does not allow Lambda functions to have that permission
    - B. The function never creates the alarm, so least privilege says it should not be able to
    - C. The permission is included automatically in `cloudwatch:PutMetricData`
    - D. Alarms can only be created in the AWS console

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. A team member or a deployment script creates the alarm once. The function only publishes the metric, so it needs only <code>cloudwatch:PutMetricData</code>.
    </details>

3. The alarm watches the `Cohort` dimension `python200-fall-2026`, but the handler publishes with the dimension `python200-fall26`. What happens on AWS when the rate is low?

    - A. The alarm fires, because the namespace and metric name match
    - B. The alarm does not fire, because it watches a different metric that has no data
    - C. CloudWatch corrects the dimension automatically
    - D. `put_metric_data` raises an error

    <details><summary><strong>Click to reveal answer</strong></summary>
    Correct answer: B. A metric is identified by its namespace, name, and dimensions together. With a different dimension value, the published data goes to a different metric, and the alarm sees no data. With <code>notBreaching</code>, it stays in <code>OK</code>. A test that compares the alarm's dimensions with the published dimensions catches this mistake.
    </details>

## Lesson Wrap-Up

The handler now sends the submission rate to CloudWatch as a metric on every scheduled run, and a CloudWatch alarm compares that metric with the threshold. You can test the whole alert on your own computer with moto. One test confirms that the handler publishes the correct value, and another confirms that the alarm watches the correct metric. Your Week 8 checker confirms that the alert's role allows exactly the calls the handler makes. moto does not evaluate alarms or enforce IAM, so these tests check the pieces, and a real deployment confirms the final behavior.

You have now practiced the main AWS services that the practicum uses: IAM, Parameter Store, Lambda, EventBridge Scheduler, and CloudWatch. In the practicum, you will deploy a pipeline with these same services in a real AWS account.
