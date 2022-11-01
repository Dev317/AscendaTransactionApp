# CREATE
# invoked by transaction service (when threshold new records are added)\
# 1) Takes in a list of transaction records
# 2) For each transaction, get the policy for that card and date, then apply it
# 3) create and store that reward record, then fire a notification

# READ
# invoked by UI (customer)

# UPDATE
# ? luxury

# DELETE
# ? luxury
import logging
import os
import requests
import json

import boto3
from boto3.dynamodb.conditions import Key, Attr

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
REWARD_TABLE_NAME = os.environ.get("REWARD_TABLE_NAME", "reward_service_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
REWARD_TABLE = DYNAMODB_CLIENT.Table(REWARD_TABLE_NAME)

APIG_URL = os.environ.get("APIG_URL","https://kd61m94cag.execute-api.ap-southeast-1.amazonaws.com/dev/")


class NoPolicyFound(Exception):
    """Raised when there is no policy found"""

MCC_TYPES = { # (incl, excl)
    "agricultural": range(1,1500),
    "contracted": range(1500,3000),
    "airlines": range(3000,3300),
    "car_rental": range(3300,3500),
    "hotel": range(3500,4000),
    "utility": range(4800,5000),
    "retail": range(5000,5600),
    "clothing": range(5600,5700),
    "miscellaneous": range(5700,7300),
    "business": range(7300,8000),
    "professional": range(8000,9000),
    "government": range(9000,10000),
    }

def invoke_lambda(post_request: dict, end_point: str):
    """Packages a JSON message into a http request and invokes another service
    Returns a jsonified response object"""
    return requests.post(APIG_URL + end_point, json = post_request).json()

#   ______ .______       __    __   _______  
#  /      ||   _  \     |  |  |  | |       \ 
# |  ,----"|  |_)  |    |  |  |  | |  .--.  |
# |  |     |      /     |  |  |  | |  |  |  |
# |  `----.|  |\  \----.|  `--"  | |  "--"  |
#  \______|| _| `._____| \______/  |_______/ 
# Functions for basic Create, Read, Update, Delete that call other services

def get_policy(card_type:str, policy_date: str) -> dict:
    try:
        post_request = {
            "action": "get_policy",
            "data" : {
                "policy_date": policy_date,
                "card_type": card_type
            }
        }
        policy = invoke_lambda(post_request, "calculation")
    except Exception as exception:
        print("error retrieving policy from calculation_service: " + str(exception))
    
    if "policy_date" in policy:
        return policy
    else:
        msg = "No matching policy found for %s and %s", card_type, policy_date
        raise NoPolicyFound(msg)


def apply_policy(policy:dict, transaction:dict) -> dict:
    """Takes a given policy and applies it to a given transaction to return a reward record"""
    reward = {
        "reward_id": transaction["transaction_id"][0:16] + transaction["card_id"][0:16], #TODO a sensible reward id generator
        "card_id": transaction["card_id"],
        "card_type": transaction["card_type"],
        "date": transaction["transaction_date"],
        "merchant_name": transaction["merchant"],
        "is_exclusion": False,
        "currency": transaction["currency"],
        "original_amount": transaction["sgd_amount"],
        "reward_value": "0"
    }

    #check exclusions
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
        #apply policy
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
            if float(transaction["sgd_amount"]) <= float(condition["amount_greater_than"]):
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
        if "mcc_type_include" in condition: #checks if the mcc is in a certain range#TODO handle multiple tpyes e.g. hotels, petrol and games
            if transaction["mcc"] not in MCC_TYPES[condition["mcc_type_include"]]:
                return -1
        if "mcc_type_exclude" in condition: #checks if the mcc is not in a certain range
            if transaction["mcc"] in MCC_TYPES[condition["mcc_type_exclude"]]:
                return -1

        if "percentage_of_amount" in condition:
            return float(condition["percentage_of_amount"]) * float(transaction["sgd_amount"])
        #else other calculation types to be implemented
    except Exception as exception:
        raise exception


def calculate_reward(transaction: dict) -> dict:
    """Takes a transaction, finds the right policy, then applies it, then returns the reward dict"""
    try:
        policy = get_policy(transaction["card_type"], transaction["transaction_date"])
        reward = apply_policy(policy, transaction)
    except Exception as exception:
        return {
            "statusCode": 500,
            "message": "An error occurred getting the reward.",
            "error": str(exception),
        }
    return reward


def get_all_by_card_id(card_id: str):
    response = REWARD_TABLE.scan(FilterExpression=Attr("card_id").eq(card_id))
    data = response["Items"]

    while "LastEvaluatedKey" in response:
        response = REWARD_TABLE.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        data.extend(response["Items"])
    
    return data


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
        return {
            "statusCode": 500,
            "message": "Incorrect input",
            "error": repr(exception),
        }

    try:
        # PRODUCTION ENDPOINTS
        if action == "calculate_reward":
            resp = calculate_reward(body["data"])
        elif action == "get_all_by_card_id":
            resp = get_all_by_card_id(body["data"]["card_id"])

        # TESTING ENDPOINTS
        elif action == "test_get_policy":
            resp = get_policy(body["data"]["card_type"],body["data"]["policy_date"])
        else:
            resp = {
                "statusCode": 500,
                "body": "no such action"
            }
    except Exception as exception:
        return {
            "statusCode": 500,
            "message": "An error occurred processing the action.",
            "error": str(exception),
        }

    return {
        "statusCode": 200,
        "body": json.dumps(resp)
    }