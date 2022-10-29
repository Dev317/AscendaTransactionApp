import json
import logging
import os
import requests

import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
EXCLUSION_TABLE_NAME = os.environ.get("EXCLUSION_TABLE_NAME", "exclusion_service_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
EXCLUSION_TABLE = DYNAMODB_CLIENT.Table(EXCLUSION_TABLE_NAME)

APIG_URL = os.environ.get("APIG_URL","https://kd61m94cag.execute-api.ap-southeast-1.amazonaws.com/dev/")


def invoke_lambda(post_request: dict, end_point: str):
    """Packages a JSON message into a http request and invokes another service
    Returns a jsonified response object"""
    return requests.post(APIG_URL + end_point, json = post_request).json()


def create_exclusion(data):
    """Takes in a json of exclusion data (from APIG) and creates DB object
    Then, invokes the calculation service to apply the exclusion"""
    #TODO input verification to check that the fields are correctly set? or relegate to frontend?

    #check if exclusion exists
    existing_exclusion = get_by_card_type_and_name(data["card_type"], data["exclusion_name"])
    if "Item" in existing_exclusion:
        return {
            "statusCode": 500,
                "message": "Exclusion already exists. Did you mean to update instead?"
        }

    try:
        LOGGER.info("attempting to add")
        exclusion_item = data
        card_types_list  = data["card_type"]
        for card_type in card_types_list:
            exclusion_item["card_type"] = card_type
            response = EXCLUSION_TABLE.put_item(
                Item = exclusion_item
            )
            LOGGER.info("exclusion %s - %s created", card_type, data["exclusion_name"])
            # apply exclusion to existing policies
            try:
                post_request = {
                    "action": "add_new_exclusion",
                    "data": exclusion_item
                }
                invoke_lambda(post_request, "calculation")
                LOGGER.info("calculation successfully invoked for %s", str(data["card_type"]))
            except Exception as exception:
                return {
                    "statusCode": 500,
                        "message": "An error occurred invoking the calculation service.",
                        "error": str(exception)
                }
        
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred creating the exclusion.",
                "error": str(exception)
        }

    # data["card_type"] = card_types_list # python and pointers means this key got overwritten


    return response


def get_all():
    """get all exclusions from the exclusions table"""
    try:
        response = EXCLUSION_TABLE.scan()
        data = response['Items']
        while 'LastEvaluatedKey' in response:
            response = EXCLUSION_TABLE.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])

    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred getting all exclusions.",
                "error": str(exception)
        }
    return data


def get_by_card_type_and_name(card_type: str, exclusion_name: str):
    """CRUD: get by card type and name"""
    LOGGER.info("Attempting to get %s", exclusion_name)
    try:
        response = EXCLUSION_TABLE.get_item(Key={"card_type": card_type,"exclusion_name": exclusion_name})
        LOGGER.info(json.dumps(response))
        # note: if the item is not found, response will not have key "item"
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred getting exclusion by id.",
                "error": str(exception)
        }
    return response


def lambda_handler(event, context):
    """main handler"""
    try:
        if "body" in event: #if the event comes from APIG
            body = json.loads(event["body"])
            action = body["action"]
        else: #if the event comes from lambda test
            body = event
            action = event["action"]
    except Exception as exception:
        LOGGER.error(exception)
        return {
            "statusCode": 500,
            "message": "Incorrect input",
            "error": repr(exception),
        }

    try:
        if action == "create":
            dynamo_resp = create_exclusion(body["data"])
        elif action == "get_all":
            dynamo_resp = get_all()
        elif action == "get_by_card_type_and_name":
            dynamo_resp = get_by_card_type_and_name(body["data"]["card_type"], body["data"]["exclusion_name"])
        else:
            dynamo_resp = {
                "statusCode": 500,
                "body": "no such action"
            }
    #TODO: format error returns properly so apig can give proper error response reporting (rather than having to check cloud watch)
    except Exception as exception:
        LOGGER.error(exception)
        return {
            "statusCode": 500,
            "message": "An error occurred processing the action.",
            "error": str(exception),
        }

    return {
        "statusCode": 200,
        "body": json.dumps(dynamo_resp)
    }
