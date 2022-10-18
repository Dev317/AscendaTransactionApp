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

import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
CAMPAIGN_TABLE_NAME = os.environ.get("CAMPAIGN_TABLE_NAME", "campaign_service_table")
CAMPAIGN_INDEX_TABLE_NAME = os.environ.get("CAMPAIGN_INDEX_TABLE_NAME", "campaign_index_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
CAMPAIGN_TABLE = DYNAMODB_CLIENT.Table(CAMPAIGN_TABLE_NAME)
CAMPAIGN_INDEX_TABLE = DYNAMODB_CLIENT.Table(CAMPAIGN_INDEX_TABLE_NAME)

def create_campaign(data):
    campaign_id = data["campaign_start_date"] + "_" + data["campaign_name"]
    try:
        response = CAMPAIGN_TABLE.put_item(
            Item={
                "campaign_id": campaign_id,
                "campaign_name": data["campaign_name"],
                "campaign_description": data["campaign_description"],
                "campaign_start_date": data["campaign_start_date"],
                "campaign_end_date": data["campaign_end_date"],
                "card_type": data["card_type"],
                "campaign_conditions": data["campaign_conditions"],
                "campaign_priority": data["campaign_priority"]
            }
        )
        LOGGER.info("campaign created")
        add_to_index(campaign_id)
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred creating the campaign.",
                "error": str(exception)
        }
    return response

def get_index():
    """helper function to get the list of campaigns, returns a list of strings"""
    try:
        index_response = CAMPAIGN_INDEX_TABLE.get_item(Key={"index_id": "campaign_index"})
        campaign_index_list = index_response["Item"]["campaign_index_list"]
    except Exception as exception:
        LOGGER.error(exception)
        return {
            "statusCode": 500,
                "message": "An error occurred retrieving index.",
                "error": str(exception)
        }
    LOGGER.info("index retrieved")
    return campaign_index_list

def add_to_index(campaign_id):
    """function that adds a campaign name to the index object table, returns the add response"""
    LOGGER.info("adding %s to index", campaign_id)
    try:
        campaign_index_list = get_index()
        for campaign in campaign_index_list:
            LOGGER.info(campaign)
        campaign_index_list.append(campaign_id)
        response = CAMPAIGN_INDEX_TABLE.put_item(
            Item={
                "index_id": "campaign_index",
                "campaign_index_list": campaign_index_list
            }
        )
    except Exception as exception:
        LOGGER.error(exception)
        return {
            "statusCode": 500,
                "message": "An error occurred adding to index.",
                "error": str(exception)
        }
    LOGGER.info("succcessfully added %s to index", campaign_id)
    return response

def get_all():
    """get all campaigns from the campaigns table"""
    campaign_index_list = get_index()
    keys_list = []
    for campaign in campaign_index_list:
        keys_list.append({"campaign_id": campaign})
    try:
        response = DYNAMODB_CLIENT.batch_get_item(
            RequestItems={
                CAMPAIGN_TABLE_NAME: {
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
                "message": "An error occurred getting all campaigns.",
                "error": str(exception)
        }
    return response

def get_by_id(data):
    try:
        response = CAMPAIGN_TABLE.get_item(Key={"campaign_id": data["campaign_id"]})
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred getting campaign by id.",
                "error": str(exception)
        }
    return response

def lambda_handler(event, context):
    """main handler"""

    if event["action"] == "create":
        dynamo_resp = create_campaign(event["data"])
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
