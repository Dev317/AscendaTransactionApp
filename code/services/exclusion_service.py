# CREATING A NEW EXCLUSION
# 1) Admin creates a new exclusion on frontend
# 2) Create request comes through API gateway
# 3) API gateway hits this service
# 4) This service runs CRUD operations to update the exclusions database
# 5) On success, there is a need to re-create the calculation policies
# 6) This service sends the dates and specific card-exclusion to calculation_service through API gateway
# to do identify point of failure for the above, and where the error reporting and handling should fall, and whether there should be saga rollback

# READ
# invoked by UI (admin), calculation

# UPDATE
# ? luxury

# DELETE
# ? luxury


import json
import logging
import os
import requests

import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
EXCLUSION_TABLE_NAME = os.environ.get("EXCLUSION_TABLE_NAME", "exclusion_service_table")
EXCLUSION_INDEX_TABLE_NAME = os.environ.get("EXCLUSION_INDEX_TABLE_NAME", "exclusion_index_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
EXCLUSION_TABLE = DYNAMODB_CLIENT.Table(EXCLUSION_TABLE_NAME)
EXCLUSION_INDEX_TABLE = DYNAMODB_CLIENT.Table(EXCLUSION_INDEX_TABLE_NAME)

APIG_URL = " https://kd61m94cag.execute-api.ap-southeast-1.amazonaws.com/dev/"

class DuplicateExclusionIndex(Exception):
    """Raised when exclusion service tries to add a exclusion whose index already exists
    Used to prevent duplicates in the index table from blocking the exclusion get_all"""


def invoke_lambda(post_request: dict, end_point: str):
    """Packages a JSON message into a http request and invokes another service
    Returns a jsonified response object"""
    return requests.post(APIG_URL + end_point, json = post_request).json()


def create_exclusion(data):
    #TODO input verification to check that the fields are correctly set? or relegate to frontend?
    exclusion_id = data["exclusion_start_date"] + "_" + data["exclusion_name"]
    exclusion_item = data
    exclusion_item["exclusion_id"] = exclusion_id

    # check if exclusion id already exists
    exclusion_index_list = get_index()
    for exclusion in exclusion_index_list:
        if exclusion_id == exclusion:
            #TODO: integrate with outer exclusion creation wrt updating of exclusions
            raise DuplicateExclusionIndex("Duplicate exclusion id detected, aborting exclusion creation")
        LOGGER.info(exclusion)

    try:
        LOGGER.info("attempting to add")
        response = EXCLUSION_TABLE.put_item(
            Item= exclusion_item
        )
        LOGGER.info("exclusion created")
        add_to_index(exclusion_id)
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred creating the exclusion.",
                "error": str(exception)
        }

    try:
        post_request = {
            "action": "add_new_exclusion",
            "data": exclusion_item
        }
        invoke_lambda(post_request, "calculation")
        LOGGER.info("calculation successfully invoked")
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred invoking the calculation service.",
                "error": str(exception)
        }

    return response

def get_index():
    """helper function to get the list of exclusions, returns a list of strings"""
    try:
        index_response = EXCLUSION_INDEX_TABLE.get_item(Key={"exclusion_index_id": "exclusion_index"})
        exclusion_index_list = index_response["Item"]["exclusion_index_list"]
    except Exception as exception:
        LOGGER.error(exception)
        return {
            "statusCode": 500,
                "message": "An error occurred retrieving index.",
                "error": str(exception)
        }
    LOGGER.info("index retrieved")
    return exclusion_index_list

def add_to_index(exclusion_id):
    """function that adds a exclusion name to the index object table, returns the add response"""
    LOGGER.info("adding %s to index", exclusion_id)
    try:
        exclusion_index_list = get_index()
        for exclusion in exclusion_index_list:
            LOGGER.info(exclusion)
        exclusion_index_list.append(exclusion_id)
        response = EXCLUSION_INDEX_TABLE.put_item(
            Item={
                "exclusion_index_id": "exclusion_index",
                "exclusion_index_list": exclusion_index_list
            }
        )
    except Exception as exception:
        LOGGER.error(exception)
        return {
            "statusCode": 500,
                "message": "An error occurred adding to index.",
                "error": str(exception)
        }
    LOGGER.info("succcessfully added %s to index", exclusion_id)
    return response

def get_all():
    """get all exclusions from the exclusions table"""
    exclusion_index_list = get_index()
    keys_list = []
    for exclusion in exclusion_index_list:
        keys_list.append({"exclusion_id": exclusion})
    try:
        response = DYNAMODB_CLIENT.batch_get_item(
            RequestItems={
                EXCLUSION_TABLE_NAME: {
                    "Keys": keys_list,
                    "ConsistentRead": True
                }
            },
            ReturnConsumedCapacity="TOTAL"
        # Todo: consume the unprocessed keys
    )
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred getting all exclusions.",
                "error": str(exception)
        }
    return response

def get_by_id(data):
    """CRUD: get by exclusion_id"""
    try:
        response = EXCLUSION_TABLE.get_item(Key={"exclusion_id": data["exclusion_id"]})
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
        elif action == "get_by_id":
            dynamo_resp = get_by_id(body["data"])
        elif action == "get_index":
            dynamo_resp = get_index()
    #TODO: format error returns properly so apig can give proper error response reporting (rather than having to check cloud watch)
    except DuplicateExclusionIndex as exception:
        LOGGER.error(exception)
        return {
            "statusCode": 500,
                "message": "Duplicate exclusion ID detected. Please change the name of your added campaign.",
                "error": str(exception)
        }
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
