# CREATE
# invoked by transaction service (when threshold new records are added)\
# 1) Takes in a list of transaction records
# 2) For each transaction, get the policy for that card and date, then apply it
# 3) create and store that reward record, then fire a notification

# READ
# invoked by UI (customer)

# UPDATE
# ? luxury

import json
import datetime

# DELETE
# ? luxury
import logging
import os
from decimal import Decimal

import boto3
import requests
from boto3.dynamodb.conditions import Attr
from dateutil.parser import parse

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
REWARD_TABLE_NAME = os.environ.get("REWARD_TABLE_NAME", "reward_service_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
REWARD_TABLE = DYNAMODB_CLIENT.Table(REWARD_TABLE_NAME)

APIG_URL = os.environ.get(
    "APIG_URL", "https://xxsnouhdr9.execute-api.ap-southeast-1.amazonaws.com/prod/"
)


class NoPolicyFound(Exception):
    """Raised when there is no policy found"""


MCC_TYPES = {  # (incl, excl)
    "agricultural": range(1, 1500),
    "contracted": range(1500, 3000),
    "airlines": range(3000, 3300),
    "car_rental": range(3300, 3500),
    "hotel": range(3500, 4000),
    "utility": range(4800, 5000),
    "retail": range(5000, 5600),
    "clothing": range(5600, 5700),
    "miscellaneous": range(5700, 7300),
    "business": range(7300, 8000),
    "professional": range(8000, 9000),
    "government": range(9000, 10000),
}


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
    LOGGER.info("%s response: %s", end_point, lambda_response)
    return lambda_response


def convert_date(input_date: str):
    # return parse(date_input).strftime("%d-%m-%y")
    date_things = input_date.split("/")
    # LOGGER.info("date string: %s", str(date_things))
    in_day = date_things[0]
    in_mth = date_things[1]
    in_yr = date_things[2]
    # LOGGER.info("date items: %s %s %s", in_day, in_mth, in_yr)
    date_time_obj = datetime.date(
        year=int(in_yr), month=int(in_mth), day=int(in_day)
    )
    # LOGGER.info("here")
    return date_time_obj.strftime("%d-%m-%Y")

#   ______ .______       __    __   _______
#  /      ||   _  \     |  |  |  | |       \
# |  ,----"|  |_)  |    |  |  |  | |  .--.  |
# |  |     |      /     |  |  |  | |  |  |  |
# |  `----.|  |\  \----.|  `--"  | |  "--"  |
#  \______|| _| `._____| \______/  |_______/
# Functions for basic Create, Read, Update, Delete that call other services


def get_policy(card_type: str, policy_date: str) -> dict:
    # try:
    policy_date = convert_date(policy_date)
    post_request = {
        "action": "get_policy",
        "data": {"policy_date": policy_date, "card_type": card_type},
    }
    policy = invoke_lambda(post_request, "calculation")
    # except Exception as exception:
    #     print("error retrieving policy from calculation_service: " + str(exception))

    if "policy_date" in policy:
        return policy
    else:
        msg = "No matching policy found for %s and %s", card_type, policy_date
        raise NoPolicyFound(msg)


def apply_policy(policy: dict, transaction: dict) -> dict:
    """Takes a given policy and applies it to a given transaction to return a reward record"""
    reward = {
        "reward_id": transaction["transaction_id"][0:16]
        + transaction["card_id"][0:16],  # TODO a sensible reward id generator
        "card_id": transaction["card_id"],
        "card_type": transaction["card_type"],
        "date": transaction["transaction_date"],
        "merchant_name": transaction["merchant"],
        "is_exclusion": False,
        "currency": transaction["currency"],
        "original_amount": transaction["sgd_amount"],
        "reward_value": "0",
    }

    # check exclusions
    exclusion_mcc = policy["exclusion_conditions"]["mcc"]
    exclusion_merchant = policy["exclusion_conditions"]["merchant"]

    if transaction["mcc"] in exclusion_mcc:
        reward["is_exclusion"] = True
        reward["calculation_reason"] = exclusion_mcc[transaction["mcc"]]
        reward["reward_value"] = 0

    if transaction["merchant"] in exclusion_merchant:
        reward["is_exclusion"] = True
        reward["calculation_reason"] = exclusion_merchant[transaction["merchant"]]
        reward["reward_value"] = 0

    if not reward["is_exclusion"]:
        # apply policy
        campaign_conditions = policy["campaign_conditions"]
        reward_float = -1
        LOGGER.info("checking campaign conditions")
        for condition in campaign_conditions:
            reward_float = check_condition(transaction, condition)
            if reward_float > 0:
                reward["reward_value"] = str(round(reward_float, 2))
                reward["calculation_reason"] = condition["calculation_reason"]
                break

    LOGGER.info("final amount: %s", reward["reward_value"])
    return reward


def check_condition(transaction: dict, condition: dict) -> float:
    try:
        if "amount_greater_than" in condition:
            if float(transaction["sgd_amount"]) <= float(
                condition["amount_greater_than"]
            ):
                return -1
        if "mcc_include" in condition:
            if transaction["mcc"] not in condition["mcc_include"]:
                return -1
        if "mcc_exclude" in condition:
            if transaction["mcc"] in condition["mcc_exclude"]:
                return -1
        if "merchant_name_include" in condition:
            if transaction["merchant"] not in condition["merchant_name_include"]:
                return -1
        if "merchant_name_exclude" in condition:
            if transaction["merchant"] in condition["merchant_name_exclude"]:
                return -1
        if "currency_include" in condition:
            if transaction["currency"] not in condition["currency_include"]:
                return -1
        if "currency_exclude" in condition:
            if transaction["currency"] in condition["currency_exclude"]:
                return -1
        if (
            "mcc_type_include" in condition
        ):  # checks if the mcc is in a certain range#TODO handle multiple tpyes e.g. hotels, petrol and games
            if transaction["mcc"] not in MCC_TYPES[condition["mcc_type_include"]]:
                return -1
        if (
            "mcc_type_exclude" in condition
        ):  # checks if the mcc is not in a certain range
            if transaction["mcc"] in MCC_TYPES[condition["mcc_type_exclude"]]:
                return -1

        if "percentage_of_amount" in condition:
            return float(condition["percentage_of_amount"]) * float(
                transaction["sgd_amount"]
            )
        # else other calculation types to be implemented
    except Exception as exception:
        raise exception


def calculate_reward(transaction: dict) -> dict:
    """Takes a transaction, finds the right policy, then applies it, then returns the reward dict"""
    try:
        policy = get_policy(transaction["card_type"], transaction["transaction_date"])
        reward = apply_policy(policy, transaction)
        put_reward(reward)
        LOGGER.info("Reward stored: %s", reward["reward_id"])
    except Exception as exception:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred getting the reward.",
            "error": str(exception),
        }
    return reward


def batch_calculate_reward(transaction_list: list):
    """Takes a list of transaction dicts and invokes calculate_reward multiple times"""
    LOGGER.info("Batch processing begins...")
    errored_transactions = []
    for transaction in transaction_list:
        try:
            reward = calculate_reward(transaction)
            LOGGER.info(json.dumps(reward))
        except Exception as exception:
            errored_transactions.append(transaction)
            LOGGER.error(
                "Failed to calculate reward for transaction <%s>",
                transaction["transaction_id"],
            )
            LOGGER.error(exception)
    LOGGER.info("Rewards saved. Total errored values: %d", len(errored_transactions))
    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": "Successfully saved batch rewards.",
        "errored values": json.dumps(errored_transactions),
    }


def put_reward(reward: dict):
    """Takes a reward dict and stores it into dynamodb table"""
    try:
        item = json.loads(json.dumps(reward), parse_float=Decimal)
        LOGGER.info("Attempting to save reward %s to db", reward["reward_id"])
        response = REWARD_TABLE.put_item(Item=item)
        LOGGER.info("reward %s - %s saved to db", reward["reward_id"], reward["date"])
    except Exception as exception:
        LOGGER.error(str(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error adding the reward to db.",
            "error": str(exception),
        }
    return response


def get_all_by_card_id(card_id: str):
    response = REWARD_TABLE.scan(FilterExpression=Attr("card_id").eq(card_id))
    if "Items" not in response:
        return {"No results found"}
    LOGGER.info(str(response))
    data = response["Items"]

    while "LastEvaluatedKey" in response:
        LOGGER.info("Still has lastev key")
        response = REWARD_TABLE.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        data.extend(response["Items"])

    LOGGER.info("Fetched all, final: ")
    LOGGER.info(data)
    return data


def lambda_handler(event, context):
    """Main function that lambda passes trigger input into"""
    LOGGER.info("Reward service starting up")

    # try:
    if "body" in event:  # if the event comes from APIG
        body = json.loads(event["body"])
        LOGGER.info(type(event["body"]))
        LOGGER.info("this is body: %s", body)
        LOGGER.info(type(body))
        action = body["action"]
    else:  # if the event comes from lambda test
        body = event
        action = event["action"]
    # except Exception as exception:
    #     return {
    #         "statusCode": 500,
    #         "headers": {"Access-Control-Allow-Origin": "*"},
    #         "message": "Incorrect input",
    #         "error": repr(exception),
    #     }

    # try:
    # PRODUCTION ENDPOINTS
    if action == "calculate_reward":
        resp = calculate_reward(body["data"])
    elif action == "get_all_by_card_id":
        resp = get_all_by_card_id(body["data"]["card_id"])
    elif action == "batch_calculate_reward":
        LOGGER.info("batch_calculate_reward called")
        LOGGER.info(body["data"])
        resp = batch_calculate_reward(body["data"])
    elif action == "health":
        resp = "Service is healthy"

    # TESTING ENDPOINTS
    elif action == "test_get_policy":
        resp = get_policy(body["data"]["card_type"], body["data"]["policy_date"])
    else:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": "no such action",
        }
    # except Exception as exception:
    #     return {
    #         "statusCode": 500,
    #         "headers": {"Access-Control-Allow-Origin": "*"},
    #         "message": "An error occurred processing the action.",
    #         "error": str(exception),
    #     }

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(resp, cls=JSONEncoder),
    }
