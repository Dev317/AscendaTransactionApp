# CREATE
# invoked by CSV processor, invoked by UI (admin)

# READ
# invoked by reward_service

# UPDATE
# ? luxury

# DELETE
# ? luxury

import json

# When threshold transaction records are added, will invoke reward_service to generate new rewards
# after bulk processing a csv, will sort the records by card type then date,
#  then invoke reward service in batches
#  (to improve speed by caching, where many txs with the same policy can be calculated at the same timeimport json
import logging
import os
from decimal import Decimal

import boto3
import requests
from boto3.dynamodb.conditions import Attr

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
TRANSACTION_TABLE_NAME = os.environ.get(
    "TRANSACTION_TABLE_NAME", "transaction_service_table"
)

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
TRANSACTION_TABLE = DYNAMODB_CLIENT.Table(TRANSACTION_TABLE_NAME)

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
    LOGGER.info("%s invoked", end_point)
    LOGGER.info(post_request)
    lambda_response = requests.post(APIG_URL + end_point, json=post_request).json()
    LOGGER.info(lambda_response)
    return lambda_response


def create_transaction(data: dict):
    """Takes in a dict of transaction data (from csv processor/APIG) and creates DB object"""
    transaction_item = json.loads(json.dumps(data), parse_float=Decimal)
    # TODO input verification to check that the fields are correctly set? or relegate to frontend?

    try:
        response = TRANSACTION_TABLE.put_item(Item=transaction_item)
        LOGGER.info("transaction created")
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred creating the transaction.",
            "error": str(exception),
        }
    return response


def batch_create_transactions(transaction_list: list):
    """Takes a list of transaction dicts and invokes create_transaction multiple times,
    Then enqueues the batch transactions to generate rewards"""
    errorred_transactions = []
    LOGGER.info("Creating a batch of %d transactions", len(transaction_list))
    for transaction in transaction_list:
        try:
            create_transaction(transaction)
        except Exception as exception:
            errorred_transactions.append(transaction)
            LOGGER.error(
                "Transaction <%s> failed to be saved", transaction["transaction_id"]
            )
            LOGGER.error(exception)
    LOGGER.info(
        "Transactions saved. Total errored values: %d", len(errorred_transactions)
    )

    LOGGER.info("Transaction list: %s", transaction_list)

    post_request = {"action": "batch_calculate_reward", "data": transaction_list}
    res = invoke_lambda(post_request, "reward")

    LOGGER.info("response from reward service received")
    LOGGER.info(json.dumps(res))

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": "Successfully processed batch of transactions",
    }


def get_by_card_id(card_id: str):
    """CRUD: get all transactions by card_id (aka partition key)"""
    LOGGER.info("Attempting to get %s", card_id)
    try:
        # response = TRANSACTION_TABLE.get_item(Key={"card_id": card_id})
        response = TRANSACTION_TABLE.scan(FilterExpression=Attr("card_id").eq(card_id))
        LOGGER.info(json.dumps(response))
        # note: if the item is not found, response will not have key "item"
    except Exception as exception:
        LOGGER.error("ERROR: %s", repr(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred getting transactions by card_id.",
            "error": str(exception),
        }
    return response


def get_by_card_type(user_id: str, card_type: str):
    response = "response"
    return response


def lambda_handler(event, context):
    """Main function that lambda passes trigger input into"""

    try:
        if "Records" in event:  # if the event comes from SQS
            transactions = list()
            for message in event["Records"]:
                transactions += json.loads(message["body"])
            LOGGER.info("total messages: %d", len(event["Records"]))
            action = "batch_create"
        elif "body" in event:  # if the event comes from APIG
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
            resp = create_transaction(body["data"])
        elif action == "get_by_card_id":
            resp = get_by_card_id(body["data"]["card_id"])
        elif action == "get_by_id":
            resp = get_by_card_type(body["data"]["user_id"], body["data"]["card_type"])
        elif action == "batch_create":
            resp = batch_create_transactions(transactions)
        elif action == "test_reward":
            resp = invoke_lambda(
                {"action": "batch_calculate_reward", "data": body["data"]}, "reward"
            )
        elif action == "health":
            resp = "Service is healthy"
        else:
            LOGGER.error("ERROR: %s", repr(exception))
            return {
                "statusCode": 500,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": "no such action",
            }
    # TODO: format error returns properly so apig can give proper error response reporting (rather than having to check cloud watch)
    except Exception as exception:
        LOGGER.error(repr(exception))
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
