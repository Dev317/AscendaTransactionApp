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

import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
EXCLUSION_TABLE_NAME = os.environ.get("EXCLUSION_TABLE_NAME", "exclusion_service_table")
EXCLUSION_INDEX_TABLE_NAME = os.environ.get("EXCLUSION_INDEX_TABLE_NAME", "exclusion_index_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
EXCLUSION_TABLE = DYNAMODB_CLIENT.Table(EXCLUSION_TABLE_NAME)
EXCLUSION_INDEX_TABLE = DYNAMODB_CLIENT.Table(EXCLUSION_INDEX_TABLE_NAME)

def create_exclusion(data):
    #TODO fix the ID convention
    exclusion_id = data["exclusion_start_date"] + "_" + data["exclusion_end_date"]
    try:
        response = EXCLUSION_TABLE.put_item(
            Item={
                "exclusion_id": exclusion_id,
                "exclusion_start_date": data["exclusion_start_date"],
                "exclusion_end_date": data["exclusion_end_date"],
                "card_type": data["card_type"],
                "exclusion_conditions": data["exclusion_conditions"]
            }
        )
        LOGGER.info("exclusion created")
        add_to_index(exclusion_id)
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred creating the exclusion.",
                "error": str(exception)
        }
    return response

def get_index():
    """helper function to get the list of exclusions, returns a list of strings"""
    try:
        index_response = EXCLUSION_INDEX_TABLE.get_item(Key={"exclusion_index_id": "exclusion_index"})
        LOGGER.info(index_response)
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

    if event["action"] == "create":
        dynamo_resp = create_exclusion(event["data"])
    elif event["action"] == "get_all":
        dynamo_resp = get_all()
    elif event["action"] == "get_by_id":
        dynamo_resp = get_by_id(event["data"])
    elif event["action"] == "get_index":
        dynamo_resp = get_index()

    return {
        "statusCode": 200,
        "body": dynamo_resp
    }
