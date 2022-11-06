# CREATE
# invoked by UI

# READ
# invoked by UI

# UPDATE
# ? luxury

# DELETE
# ? luxury

# pk: card_group
# sk: card_type
# 
# unit_prefix
# unit_suffix
# group_name


"""
Lambda function that manages card groups and types
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
CARD_TABLE_NAME = os.environ.get("CARD_TABLE_NAME", "card_service_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
CARD_TABLE = DYNAMODB_CLIENT.Table(CARD_TABLE_NAME)

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


def create_card(data):
    """Takes in a json of card data (from APIG) and creates DB object"""
    # check if card exists
    existing_card = get_by_card_type_and_group(
        data["card_type"], data["card_group"]
    )
    if "Item" in existing_card:
        LOGGER.error("ERROR: Card already exists. Did you mean to update instead?")
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "Card already exists. Did you mean to update instead?",
        }

    try:
        response = CARD_TABLE.put_item(Item=data)
        LOGGER.info("card created")
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred creating the card.",
            "error": str(exception),
        }

    return response


def get_all():
    """get all card groups from the cards table"""
    try:
        response = CARD_TABLE.scan()
        data = response["Items"]
        while "LastEvaluatedKey" in response:
            response = CARD_TABLE.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            data.extend(response["Items"])
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred getting all cards.",
            "error": str(exception),
        }
    return data


def get_by_card_type(card_type: str):
    """CRUD: get by card type"""
    try:
        response = CARD_TABLE.query(
            IndexName='card_type-index',
            KeyConditionExpression=Key('card_type').eq(card_type)
        )
        # note: if the item is not found, response will not have key "item"
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred getting card_group by card_type.",
            "error": str(exception),
        }
    if "Items" in response:
        return response["Items"]
    else:
        LOGGER.error("ERROR: Cannot find card group with given card type %s", card_type)
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "Cannot find card group with given card type"
        }


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
            resp = create_card(body["data"])
        elif action == "get_all":
            resp = get_all()
        elif action == "get_by_card_type":
            resp = get_by_card_type(body["data"]["card_type"])
        elif action == "health":
            resp = "Card service is healthy"
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
