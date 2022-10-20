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
import requests

import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
CAMPAIGN_TABLE_NAME = os.environ.get("CAMPAIGN_TABLE_NAME", "campaign_service_table")
CAMPAIGN_INDEX_TABLE_NAME = os.environ.get("CAMPAIGN_INDEX_TABLE_NAME", "campaign_index_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
CAMPAIGN_TABLE = DYNAMODB_CLIENT.Table(CAMPAIGN_TABLE_NAME)
CAMPAIGN_INDEX_TABLE = DYNAMODB_CLIENT.Table(CAMPAIGN_INDEX_TABLE_NAME)

APIG_URL = " https://kd61m94cag.execute-api.ap-southeast-1.amazonaws.com/dev/"


class DuplicateCampaignIndex(Exception):
    """Raised when campaign service tries to add a campaign whose index already exists
    Used to prevent duplicates in the index table from blocking the campaign get_all"""


def invoke_lambda(post_request: dict, end_point: str):
    """Packages a JSON message into a http request and invokes another service
    Returns a jsonified response object"""
    return requests.post(APIG_URL + end_point, json = post_request).json()


def create_campaign(data):
    campaign_item = data
    #set the campaign id
    campaign_id =  data["campaign_start_date"] + "_" + data["campaign_name"]
    campaign_item["campaign_id"] = campaign_id

    # check if campaign id already exists
    campaign_index_list = get_index()
    for campaign in campaign_index_list:
        if campaign_id == campaign:
            #TODO: integrate with outer campaign creation wrt updating of campaigns
            raise DuplicateCampaignIndex("Duplicate campaign id detected, aborting campaign creation")
        LOGGER.info(campaign)

    try:
        response = CAMPAIGN_TABLE.put_item(
            Item = campaign_item
        )
        LOGGER.info("campaign created")
        add_to_index(campaign_id)
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred creating the campaign.",
                "error": str(exception)
        }
    
    try:
        post_request = {
            "action": "add_new_campaign",
            "data": campaign_item
        }
        invoke_lambda(post_request, "calculation")
        LOGGER.info("campaign created")
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred invoking the calculation service.",
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

def get_by_id(campaign_id):
    """CRUD: get by campaign_id"""
    LOGGER.info("Attempting to get %s", campaign_id)
    try:
        response = CAMPAIGN_TABLE.get_item(Key={"campaign_id": campaign_id})
        LOGGER.info(json.dumps(response))
        # note: if the item is not found, response will not have key "item"
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred getting campaign by id.",
                "error": str(exception)
        }
    return response


def lambda_handler(event, context):
    """Main function that lambda passes trigger input into"""

    try:
        if "body" in event: #if the event comes from APIG
            body = json.loads(event["body"])
            action = body["action"]
        else: #if the event comes from lambda test
            body = event
            action = event["action"]
    except Exception as exception:
        return {
            "statusCode": 500,
            "message": "Incorrect input",
            "error": repr(exception),
        }

    try:
        if action == "create":
            dynamo_resp = create_campaign(body["data"])
        elif action == "get_all":
            dynamo_resp = get_all()
        elif action == "get_by_id":
            dynamo_resp = get_by_id(body["data"]["campaign_id"])
        elif action == "get_index":
            dynamo_resp = get_index()
    #TODO: format error returns properly so apig can give proper error response reporting (rather than having to check cloud watch)
    except DuplicateCampaignIndex as exception:
        LOGGER.error(exception)
        return {
            "statusCode": 500,
                "message": "Duplicate campaign ID detected. Please change the name of your added campaign.",
                "error": str(exception)
        }
    except Exception as exception:
        return {
            "statusCode": 500,
            "message": "An error occurred processing the action.",
            "error": str(exception),
        }

    return {
        "statusCode": 200,
        "body": json.dumps(dynamo_resp)
    }
