import json
import os

import boto3

STATE_MACHINE_ARN = os.environ.get("STATE_MACHINE_ARN")


def handler(event, context):
    """
    triggers a step function from the S3 landing event,
    passing along the S3 file info
    """

    s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    s3_file = event["Records"][0]["s3"]["object"]["key"]

    input = {"s3_bucket": s3_bucket, "s3_file": s3_file}

    try:
        stepFunction = boto3.client("stepfunctions")
        response = stepFunction.start_execution(
            stateMachineArn=STATE_MACHINE_ARN, input=json.dumps(input, indent=4)
        )
        return response["executionArn"]
    except Exception as exc:
        raise exc
