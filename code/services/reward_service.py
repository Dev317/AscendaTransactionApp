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

import json
import logging
import datetime
from datetime import date, timedelta
import time
from database import CAMPAIGN_SERVICE_TABLE, POLICY_DATABASE, EXCLUSION_SERVICE_TABLE

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

#   ______ .______       __    __   _______
#  /      ||   _  \     |  |  |  | |       \
# |  ,----'|  |_)  |    |  |  |  | |  .--.  |
# |  |     |      /     |  |  |  | |  |  |  |
# |  `----.|  |\  \----.|  `--'  | |  '--'  |
#  \______|| _| `._____| \______/  |_______/
# Functions for basic Create, Read, Update, Delete that call other services


def get_policy(
    card_type: str, policy_date: str
) -> dict:  # TODO read from calculation_service
    policy_id = str(card_type) + "/" + str(policy_date)
    try:
        policy = POLICY_DATABASE[policy_id]
    except Exception as exception:
        print("error retrieving policy from calculation_service: " + str(exception))
    return policy


def calculate_reward(policy: dict, transaction: dict) -> dict:
    """Takes a given policy and applies it to a given transaction to return a reward record"""
    reward = {
        "reward_id": transaction["transaction_id"][0:16]
        + policy["policy_id"],  # TODO add policy id to the policy itself?
        "card_id": transaction["cardId"],
        "card_type": transaction["cardType"],
        "date": transaction["date"],
        "merchant_name": transaction["merchant"],
        "is_exclusion": False,
        "currency": transaction["currency"],
        "original_amount": transaction["sgdAmount"],
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
        try:

            if "amount_greater_than" in policy:
                if float(transaction["sgdAmount"]) <= float(
                    policy["amount_greater_than"]
                ):
                    return -1
            if "mcc_include" in policy:
                if transaction["mcc"] not in policy["mcc_include"]:
                    return -1
            if "mcc_exclude" in policy:
                if transaction["mcc"] in policy["mcc_exclude"]:
                    return -1
            if "merchant_name_include" in policy:
                if transaction["merchant"] not in policy["merchant_name_include"]:
                    return -1
            if "merchant_name_exclude" in policy:
                if transaction["merchant"] in policy["merchant_name_exclude"]:
                    return -1
            if "currency_include" in policy:
                if transaction["currency"] not in policy["currency_include"]:
                    return -1
            if "currency_exclude" in policy:
                if transaction["currency"] in policy["currency_exclude"]:
                    return -1
            if (
                "mcc_type_include" in policy
            ):  # checks if the mcc is in a certain range#TODO handle multiple tpyes e.g. hotels, petrol and games
                if transaction["mcc"] not in MCC_TYPES[policy["mcc_type_include"]]:
                    return -1
            if (
                "mcc_type_exclude" in policy
            ):  # checks if the mcc is not in a certain range
                if transaction["mcc"] in MCC_TYPES[policy["mcc_type_exclude"]]:
                    return -1

            if "percentage_of_amount" in policy:
                return float(policy["percentage_of_amount"]) * float(
                    transaction["sgdAmount"]
                )
            # else other calculation types to be implemented

        except Exception as exception:
            raise exception
