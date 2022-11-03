import json
import logging
import os
from decimal import Decimal

import boto3
import requests
from boto3.dynamodb.conditions import Attr

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
USER_TABLE_NAME = os.environ.get("USER_TABLE_NAME", "user_service_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
USER_TABLE = DYNAMODB_CLIENT.Table(USER_TABLE_NAME)

APIG_URL = os.environ.get(
    "APIG_URL", "https://xxsnouhdr9.execute-api.ap-southeast-1.amazonaws.com/prod/"
)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def invoke_lambda(post_request: dict, end_point: str):
    """Packages a JSON message into a http request and invokes another service
    Returns a jsonified response object"""
    return requests.post(APIG_URL + end_point, json=post_request).json()


def create_user(data: dict):
    try:
        response = USER_TABLE.put_item(Item=data)
        LOGGER.info("campaign created")
    except Exception as exception:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred creating the campaign.",
            "error": str(exception),
        }
    return response


def batch_create_user(user_list: list):
    """Takes a list of user objects and adds them to dynamodb"""
    for user in user_list:
        create_user(user)

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": "successfully batch added",
    }


def get_cards_by_user_id(user_id):
    response = USER_TABLE.scan(FilterExpression=Attr("user_id").eq(user_id))
    data = response["Items"]

    while "LastEvaluatedKey" in response:
        response = USER_TABLE.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        data.extend(response["Items"])

    return data


def lambda_handler(event, context):
    """Main function that lambda passes trigger input into"""

    try:
        if "body" in event:  # if the event comes from APIG
            body = json.loads(event["body"])
            action = body["action"]
        else:  # if the event comes from lambda test
            body = event
            action = event["action"]
    except Exception as exception:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "Incorrect input",
            "error": repr(exception),
        }

    try:
        # PRODUCTION ENDPOINTS
        if action == "create":
            resp = create_user(body["data"])
        elif action == "batch_create":
            resp = batch_create_user(body["data"])
        elif action == "get_cards_by_user_id":
            resp = get_cards_by_user_id(body["data"]["user_id"])

        # TESTING ENDPOINTS
        else:
            resp = {
                "statusCode": 500,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": "no such action",
            }
    except Exception as exception:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred processing the action.",
            "error": str(exception),
        }

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(resp, cls=JSONEncoder),
    }
