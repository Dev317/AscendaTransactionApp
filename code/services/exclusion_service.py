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
EXCLUSION_TABLE_NAME = os.environ.get("EXCLUSION_TABLE_NAME", "exclusion_service_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
EXCLUSION_TABLE = DYNAMODB_CLIENT.Table(EXCLUSION_TABLE_NAME)

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


def create_exclusion(data):
    """Takes in a json of exclusion data (from APIG) and creates DB object
    Then, invokes the calculation service to apply the exclusion"""
    # TODO input verification to check that the fields are correctly set? or relegate to frontend?

    # check if exclusion exists
    existing_exclusion = get_by_card_type_and_name(
        data["card_type"], data["exclusion_name"]
    )
    if "Item" in existing_exclusion:
        LOGGER.error("ERROR: Exclusion already exists. Did you mean to update instead?")
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "Exclusion already exists. Did you mean to update instead?",
        }

    try:
        LOGGER.info("attempting to add")
        exclusion_item = data
        card_types_list = data["card_type"]
        for card_type in card_types_list:
            exclusion_item["card_type"] = card_type
            response = EXCLUSION_TABLE.put_item(Item=exclusion_item)
            LOGGER.info("exclusion %s - %s created", card_type, data["exclusion_name"])
            # apply exclusion to existing policies
            try:
                post_request = {"action": "add_new_exclusion", "data": exclusion_item}
                invoke_lambda(post_request, "calculation")
                LOGGER.info(
                    "calculation successfully invoked for %s", str(data["card_type"])
                )
            except Exception as exception:
                LOGGER.error("ERROR: %s", repr(exception))
                return {
                    "statusCode": 500,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "message": "An error occurred invoking the calculation service.",
                    "error": str(exception),
                }

    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred creating the exclusion.",
            "error": str(exception),
        }

    # data["card_type"] = card_types_list # python and pointers means this key got overwritten

    return response


def get_all():
    """get all exclusions from the exclusions table"""
    try:
        response = EXCLUSION_TABLE.scan()
        data = response["Items"]
        while "LastEvaluatedKey" in response:
            response = EXCLUSION_TABLE.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            data.extend(response["Items"])

    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred getting all exclusions.",
            "error": str(exception),
        }
    return data


def get_by_card_type_and_name(card_type: str, exclusion_name: str):
    """CRUD: get by card type and name"""
    LOGGER.info("Attempting to get %s", exclusion_name)
    try:
        response = EXCLUSION_TABLE.get_item(
            Key={"card_type": card_type, "exclusion_name": exclusion_name}
        )
        LOGGER.info(json.dumps(response))
        # note: if the item is not found, response will not have key "item"
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred getting exclusion by id.",
            "error": str(exception),
        }
    return response


def get_by_card_type(card_type: str):
    """CRUD: get by card type only"""
    LOGGER.info("Attempting to get all exclusions for %s", card_type)
    try:
        response = EXCLUSION_TABLE.query(
            KeyConditionExpression=Key('card_type').eq(card_type)
            )
        data = response["Items"]
        while "LastEvaluatedKey" in response:
            response = EXCLUSION_TABLE.scan(
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
            "message": "An error occurred getting exclusion by card_type.",
            "error": str(exception),
        }
    return response


def lambda_handler(event, context):
    """main handler"""
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
            resp = create_exclusion(body["data"])
        elif action == "get_all":
            resp = get_all()
        elif action == "get_by_card_type_and_name":
            resp = get_by_card_type_and_name(
                body["data"]["card_type"], body["data"]["exclusion_name"]
            )
        elif action == "get_by_card_type":
            resp = get_by_card_type(
                body["data"]["card_type"]
            )
        elif action == "health":
            resp = "Exclusion service is healthy"
        else:
            LOGGER.error("ERROR: No such action: %s", action)
            return {
                "statusCode": 500,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": "no such action",
            }
    # TODO: format error returns properly so apig can give proper error response reporting (rather than having to check cloud watch)
    except Exception as exception:
        LOGGER.error(exception)
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
