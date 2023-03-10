# CREATING A NEW CAMPAIGN
# 1) Admin creates a new campaign on frontend
# 2) Create request comes through API gateway
# 3) API gateway hits this service
# 4) This service runs CRUD operations to update the campaigns database
# 5) On success, there is a need to re-create the calculation policies
# 6) This service sends the dates to calculation_service through API gateway
# to do identify point of failure for the above, and where the error reporting and handling should fall, and whether there should be saga rollback

# READ
# invoked by UI (admin), calculation

# UPDATE
# ? luxury

# DELETE
# ? luxury


"""
Lambda function that reads dynamodb, generates calculation policies
"""
#!/usr/bin/env python3

import json
import logging
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
import requests

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
CAMPAIGN_TABLE_NAME = os.environ.get("CAMPAIGN_TABLE_NAME", "campaign_service_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
CAMPAIGN_TABLE = DYNAMODB_CLIENT.Table(CAMPAIGN_TABLE_NAME)

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


def create_campaign(data):
    """Takes in a json of campaign data (from APIG) and creates DB object
    Then, invokes the calculation service to apply the campaign"""

    # TODO input verification to check that the fields are correctly set? or relegate to frontend?

    # check if campaign exists
    existing_campaign = get_by_card_type_and_name(
        data["card_type"], data["campaign_name"]
    )
    if "Item" in existing_campaign:
        LOGGER.error("ERROR: Campaign already exists. Did you mean to update instead?")
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "Campaign already exists. Did you mean to update instead?",
        }

    try:
        response = CAMPAIGN_TABLE.put_item(Item=data)
        LOGGER.info("campaign created")
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred creating the campaign.",
            "error": str(exception),
        }

    try:
        post_request = {"action": "add_new_campaign", "data": data}
        invoke_lambda(post_request, "calculation")
        LOGGER.info("calculation successfully invoked")
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred invoking the calculation service.",
            "error": str(exception),
        }

    return response


def get_all():
    """get all campaigns from the campaigns table"""
    try:
        response = CAMPAIGN_TABLE.scan()
        data = response["Items"]
        while "LastEvaluatedKey" in response:
            response = CAMPAIGN_TABLE.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            data.extend(response["Items"])
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred getting all campaigns.",
            "error": str(exception),
        }
    return data


def get_by_card_type_and_name(card_type: str, campaign_name: str):
    """CRUD: get by card type and name"""
    LOGGER.info("Attempting to get %s", campaign_name)
    try:
        response = CAMPAIGN_TABLE.get_item(
            Key={"card_type": card_type, "campaign_name": campaign_name}
        )
        LOGGER.info(json.dumps(response))
        # note: if the item is not found, response will not have key "item"
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred getting campaign by id.",
            "error": str(exception),
        }
    return response


def get_by_card_type(card_type: str):
    """CRUD: get by card type only"""
    LOGGER.info("Attempting to get all campaigns for %s", card_type)
    try:
        response = CAMPAIGN_TABLE.query(
            KeyConditionExpression=Key('card_type').eq(card_type)
            )
        data = response["Items"]
        while "LastEvaluatedKey" in response:
            response = CAMPAIGN_TABLE.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            data.extend(response["Items"])
        LOGGER.info(json.dumps(response))
        # note: if the item is not found, response will not have key "item"
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred getting campaign by card_type.",
            "error": str(exception),
        }
    return response


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
        if action == "create":
            resp = create_campaign(body["data"])
        elif action == "get_all":
            resp = get_all()
        elif action == "get_by_card_type_and_name":
            resp = get_by_card_type_and_name(
                body["data"]["card_type"], body["data"]["campaign_name"]
            )
        elif action == "get_by_card_type":
            resp = get_by_card_type(
                body["data"]["card_type"]
            )
        elif action == "health":
            resp = "Campaign service is healthy"
        else:
            LOGGER.error("ERROR: No such action: %s", action)
            return {
                "statusCode": 500,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": "no such action",
            }
    # TODO: format error returns properly so apig can give proper error response reporting (rather than having to check cloud watch)
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
