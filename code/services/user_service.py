import json
import logging
import os
from decimal import Decimal

import boto3
import requests
from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.conditions import Key

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
USER_TABLE_NAME = os.environ.get("USER_TABLE_NAME", "user_service_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
USER_TABLE = DYNAMODB_CLIENT.Table(USER_TABLE_NAME)
AWS_KEY_ID = os.environ.get("AWS_KEY_ID")
AWS_SECRET = os.environ.get("AWS_SECRET")

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
        LOGGER.info("User added. Trying to send email")

        # email verification for email notification
        client = boto3.client(service_name = "ses", aws_access_key_id= AWS_KEY_ID, aws_secret_access_key= AWS_SECRET)
        email = data["email"]
        # check if user is already verified
        verified_list = client.list_verified_email_addresses()["VerifiedEmailAddresses"]
        LOGGER.info("verified_list: %s", verified_list)
        if email in verified_list:
            LOGGER.info("Found email among verifieds")
        else:
            response_email = client.verify_email_identity(
                EmailAddress = email
            )
            LOGGER.info("email not verified. sending verification email to %s", email)
            LOGGER.info(json.dumps(response_email))
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred creating the user.",
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


def get_cards_by_user_id(user_id:str):
    """Gets all user entries by user_id"""
    response = USER_TABLE.scan(FilterExpression=Attr("user_id").eq(user_id))
    data = response["Items"]

    while "LastEvaluatedKey" in response:
        response = USER_TABLE.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        data.extend(response["Items"])

    return data


def get_user_by_email(email:str):
    """Gets all user entries by email"""
    response = USER_TABLE.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(email)
    )

    return response["Items"]


def get_user_by_card_id(card_id:str):
    """Gets all user entries by card_id"""
    response = USER_TABLE.query(
        IndexName='card_id-index',
        KeyConditionExpression=Key('card_id').eq(card_id)
    )

    #returns just the first one
    return response["Items"][0]


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
        LOGGER.error("ERROR: %s", repr(exception))
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
        elif action == "get_user_by_email":
            resp = get_user_by_email(body["data"]["email"])
        elif action == "get_user_by_card_id":
            resp = get_user_by_card_id(body["data"]["card_id"])
        elif action == "health":
            resp = "User service is healthy"

        # TESTING ENDPOINTS
        else:
            LOGGER.error("ERROR: No such action: %s", action)
            return {
                "statusCode": 500,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": "no such action",
            }
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
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
