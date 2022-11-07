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
DB_TABLE_NAME = os.environ.get("DB_TABLE_NAME", "campaign_service_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
DYNAMODB_TABLE = DYNAMODB_CLIENT.Table(DB_TABLE_NAME)


def create_campaign(data):
    response = DYNAMODB_TABLE.put_item(
        Item={
            "campaign_id": data["campaign_start_date"] + "_" + data["campaign_name"],
            "campaign_name": data["campaign_name"],
            "campaign_description": data["campaign_description"],
            "campaign_start_date": data["campaign_start_date"],
            "campaign_end_date": data["campaign_end_date"],
            "card_type": data["card_type"],
            "campaign_conditions": data["campaign_conditions"],
            "campaign_priority": data["campaign_priority"],
        }
    )
    return response


def lambda_handler(event, context):
    """main handler"""

    body = json.loads(event["body"])
    data = body["data"]

    try:
        if body["action"] == "create":
            dynamo_resp = create_campaign(data)
    except Exception as exception:
        return {
            "statusCode": 500,
            "message": "An error occurred creating the campaign.",
            "error": str(exception),
        }

    return {"statusCode": 200, "body": json.dumps(dynamo_resp)}
