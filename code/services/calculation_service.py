# ON START
# 1) get all card_types from cards_service
# 2) for loop through all card types:
# 3)    run generate_policy for epoch date to today"s date

# generate_policy
# by start date to end date. e.g. 1 jan 2021 to today"s date, and by specific card type
# 1) For loop through dates             e.g. 1 jan 2021
# 2)    For loop through card_types     e.g. scis_freedom, then scis_premium_miles
# 3)       retrieve all campaign  for cardtype and date from campaign_service  through API gateway
# 4)       retrieve all exclusion for cardtype and date from exclusion_service through API gateway
# 5)       build the policy dict for this date
# 6)       save into calculation database, then go next

# ON ADD
# 1) receive a call from calc/excl service to update a specific date range, and for specific card
# 2) run generate_policy for the given dates and card

# ON UPDATE OFEXISTING CAMPAIGN (luxury)
# 1) fetch the original campaign
# 2) replace the campaign info with the new info

# READ
# called by reward_service

import json
import logging
import datetime
from datetime import date, timedelta
import time
import os
import requests
import boto3


EXCLUSION_SERVICE_TABLE = [
    {
    "exclusion_id": "09-06-2022_Standard Exclusions",
    "exclusion_name": "Standard Exclusions",
    "exclusion_start_date": "09-06-2022",
    "exclusion_end_date": "11-06-2022",
    "card_type": ["scis_shopping", "scis_freedom"],
    "exclusion_conditions": {
        "mcc":
            {
                "6051": "Quasi Cash Merchants - Prepaid top-ups",
                "9399": "Government Services-Not Elsewhere Classified | Excluded",
                "6540": "POI (Point of Interaction) Funding Transactions (Excluding MoneySend) | Taxis & public transport"
            },
        "merchant":
            {
                "Blacklisted Merchant": "Merchant has been blacklisted"
            }
        }
    }
]

# from database import CAMPAIGN_SERVICE_TABLE, POLICY_DATABASE, EXCLUSION_SERVICE_TABLE
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
POLICY_TABLE_NAME = os.environ.get("POLICY_TABLE_NAME", "calculation_policy_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
POLICY_TABLE = DYNAMODB_CLIENT.Table(POLICY_TABLE_NAME)

APIG_URL = " https://kd61m94cag.execute-api.ap-southeast-1.amazonaws.com/dev/"

def invoke_lambda(post_request: dict, end_point: str):
    """Packages a JSON message into a http request and invokes another service
    Returns a jsonified response object"""
    return requests.post(APIG_URL + end_point, json = post_request).json()


#   ______ .______       __    __   _______  
#  /      ||   _  \     |  |  |  | |       \ 
# |  ,----'|  |_)  |    |  |  |  | |  .--.  |
# |  |     |      /     |  |  |  | |  |  |  |
# |  `----.|  |\  \----.|  `--'  | |  '--'  |
#  \______|| _| `._____| \______/  |_______/ 
# Functions for basic Create, Read, Update, Delete that call other services


def get_all_card_types() -> list:  # TODO also create crud for card_service, and set up card)service
    return ["scis_freedom", "scis_premiummiles", "scis_platinummiles", "scis_shopping"]


def get_all_campaigns() -> list:  # TODO make a get_all call to campaign_service
    """Helper function to call on campaign service to retrieve ALL campaigns
    Returns a list of all campaign objects"""
    post_request = {
        "action": "get_all"
    }
    try:
        campaign_response = invoke_lambda(post_request, "campaign")
        return campaign_response["Responses"]["campaign_service_table"]
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred invoking the campaign service.",
                "error": str(exception)
        }


def get_all_exclusions() -> list: #TODO make get_all call to exclusion_service
    """Helper function to call on exclusion service to retrieve ALL exclusions"""
    exclusion_service_table = EXCLUSION_SERVICE_TABLE
    return exclusion_service_table


def get_policy(policy_id: str) -> dict:
    try:
        response = POLICY_TABLE.get_item(Key={"policy_id": policy_id})
        LOGGER.info("Attempting get policy from dynamodb, policy_id: %s", policy_id)
        LOGGER.info(json.dumps(response))
    except Exception as exception:
        return {
            "statusCode": 500,
                "message": "An error occurred getting policy by id.",
                "error": str(exception)
        }
    if "Item" in response:
        return response["Item"]
    else:
        return {}



def put_policy(policy, policy_id):
    """Saves a given policy dict to the database by way of PUT aka overwrite"""
    # try:
    #     POLICY_DATABASE[policy_id] = policy
    # except Exception as exception:
    #     print("save failed, error: " + str(exception))
    policy["policy_id"] = policy_id
    try:
        LOGGER.info("Attempting to save %s to db", policy_id)
        response = POLICY_TABLE.put_item(
            Item = policy
        )
        LOGGER.info("Policy %s saved to db", policy_id)
    except Exception as exception:
        LOGGER.error(str(exception))
        return {
            "statusCode": 500,
                "message": "An error occurred creating the campaign.",
                "error": str(exception)
        }
    return response


#  __    __   _______  __      .______    _______ .______          _______.
# |  |  |  | |   ____||  |     |   _  \  |   ____||   _  \        /       |
# |  |__|  | |  |__   |  |     |  |_)  | |  |__   |  |_)  |      |   (----`
# |   __   | |   __|  |  |     |   ___/  |   __|  |      /        \   \    
# |  |  |  | |  |____ |  `----.|  |      |  |____ |  |\  \----.----)   |   
# |__|  |__| |_______||_______|| _|      |_______|| _| `._____|_______/    
# Helper functions for miscellaneous tasks


def date_parse(input_date: str):
    """Helper function to convert our special date string into a python dattime object"""
    return datetime.date(year = int(input_date[6:]), month = int(input_date[3:5]), day = int(input_date[0:2]))


def generate_dates(start_date, end_date) -> list:
    """helper function to convert the start date and end date to a list of all days in the format: dd-mm-yy"""
        # Return list of datetime.date objects between start_date and end_date (inclusive).
    start_datetime = date_parse(start_date)
    stop_datetime = date_parse(end_date)
    date_list = []
    curr_date = start_datetime
    while curr_date <= stop_datetime:
        date_list.append(curr_date.strftime("%d-%m-%Y"))
        curr_date += timedelta(days=1)
    return date_list


def get_earlier_date(first_date: str, second_date: str):
    """Compares 2 given dates in string format, returns the earlier date.
    Necessary because of our unique date format"""
    first_datetime = date_parse(first_date)
    second_datetime = date_parse(second_date)
    return first_date if first_datetime <= second_datetime else second_date


def get_later_date(first_date: str, second_date: str):
    """Compares 2 given dates in string format, returns the earlier date.
    Necessary because of our unique date format"""
    first_datetime = date_parse(first_date)
    second_datetime = date_parse(second_date)
    return first_date if first_datetime >= second_datetime else second_date


# .______     ______    __       __    ______ ____    ____ 
# |   _  \   /  __  \  |  |     |  |  /      |\   \  /   / 
# |  |_)  | |  |  |  | |  |     |  | |  ,----' \   \/   /  
# |   ___/  |  |  |  | |  |     |  | |  |       \_    _/   
# |  |      |  `--'  | |  `----.|  | |  `----.    |  |     
# | _|       \______/  |_______||__|  \______|    |__|     
# Functions regarding the generation of policies with campaigns and exclusions


def generate_policies(left_bound_date, right_bound_date):
    """Initialisation function to populate an empty database with all campaigns and exclusions
    Can also be used to update existing policies for a given date range"""

    campaign_list = get_all_campaigns()
    for campaign in campaign_list:
        # set the dates to generate to the tighter range of the inputted date and the campaign's date
        start_date = get_later_date(left_bound_date, campaign["campaign_start_date"])
        end_date = get_earlier_date(right_bound_date, campaign["campaign_end_date"])
        date_list = generate_dates(start_date, end_date)
        for day in date_list:
            add_campaign_to_policy(campaign, day)

    print("generate_policies: done adding campaigns")
    exclusion_list = get_all_exclusions()
    for exclusion in exclusion_list:
        # set the dates to generate to the tighter range of the inputted date and the exclusion's date
        start_date = get_later_date(left_bound_date, exclusion["exclusion_start_date"])
        end_date = get_earlier_date(right_bound_date, exclusion["exclusion_end_date"])
        date_list = generate_dates(start_date, end_date)
        for day in date_list:
            add_exclusion_to_policy(exclusion, day)
    print("generate_policies: done adding exclusions")


def add_campaign_to_policy(new_campaign: dict, campaign_date: str):
    """Iterates through all the existing campaign conditions of a given date
    then inserts the new campaign's conditions in the right order"""
    campaign_test_logger(f"Adding {new_campaign['campaign_id']} to {campaign_date}")
    policy_id = str(new_campaign["card_type"]) + "/" + str(campaign_date)
    try:
        policy = get_policy(policy_id)
        campaign_test_logger("=========before=========")
        campaign_test_logger(json.dumps(policy, indent=4))

        # pre-format campaign conditions (insert the campaign id and campaign priority)
        for condition in new_campaign["campaign_conditions"]:
            condition["campaign_id"] = new_campaign["campaign_id"]
            condition["campaign_priority"] = new_campaign["campaign_priority"]

        if "campaign_conditions" in policy:  # check if there are any campaigns
            # iterate through campaign conditions from the back, until a priority higher than new is found
            # insert at that index
            # move on to next campaign condition
            # add conditions into the policy
            campaign_test_logger("stacking existing campaign")
            cur_index = len(policy["campaign_conditions"]) - 1
            campaign_test_logger(cur_index)
            # note: the following for loop is designed to run once first before beginning the loop, hence the while True
            while True:
                if cur_index == -1: # exit condition for when it reaches the topmost policy
                    campaign_test_logger(f"Found index to insert, inserting behind {cur_index}")
                    for condition in new_campaign["campaign_conditions"]:
                        policy["campaign_conditions"].insert(cur_index + 1, condition)
                        cur_index = cur_index + 1
                    break
                prior_existing = int(policy["campaign_conditions"][cur_index]["campaign_priority"])
                prior_new = int(new_campaign["campaign_priority"])
                campaign_test_logger(f"Comparing {prior_existing} to {prior_new}")
                if prior_existing > prior_new: #insert the incoming campaign right behind the next higher priority
                    campaign_test_logger(f"Found index to insert, inserting behind {cur_index}")
                    for condition in new_campaign["campaign_conditions"]:
                        policy["campaign_conditions"].insert(cur_index + 1, condition)
                        cur_index = cur_index + 1
                    break
                cur_index = cur_index - 1

        else:  # if there is no campaign or exclusion at all for this policy, simply add it
            campaign_test_logger("adding new campaign")
            policy["campaign_conditions"] = []
            for condition in new_campaign["campaign_conditions"]:
                policy["campaign_conditions"].append(condition)

        campaign_test_logger("=========after=========")
        campaign_test_logger(json.dumps(policy, indent=4))
        # save policy to db
        put_policy(policy, policy_id)
    except Exception as exception:
        print("exception encountered while adding campaign to policy:" + str(exception))


def add_new_campaign(new_campaign: dict):
    """Invoked by campaign service whenever a new campaign is created
    Adds a new campaign to current policies, across all the campaign's dates
    Iterates through all the dates of the campaign, and calls add_campaign_to_policy"""
    try:
        date_list = generate_dates(new_campaign["campaign_start_date"], new_campaign["campaign_end_date"])
        for date_to_add in date_list:
            add_campaign_to_policy(new_campaign, date_to_add)
    except Exception as exception:
        return {
            "statusCode": 500,
            "message": "error adding new campaign",
            "error": repr(exception),
        }
    
    return {
        "statusCode": 200,
        "body": "successfully appplied new campaign to existing policies"
    }


def add_exclusion_to_policy(new_exclusion: dict, exclusion_date: str):
    """Iterates through all the card_types in a given exlusion, and applies it to a given policy date"""
    exclusion_test_logger(f"Adding {new_exclusion['exclusion_id']} to {exclusion_date}")
    for card_type in new_exclusion["card_type"]:
        policy_id = str(card_type) + "/" + str(exclusion_date)
        try:
            policy = get_policy(policy_id)
            exclusion_test_logger("=========before=========")
            exclusion_test_logger(json.dumps(policy, indent=4))
            if policy:
                if "exclusion_conditions" not in policy: # in case where there is no existing exclusions, create a blank one
                    policy["exclusion_conditions"] = {
                        "mcc": {},
                        "merchant": {}
                    }
                for excl in new_exclusion["exclusion_conditions"]["mcc"]:
                    policy["exclusion_conditions"]["mcc"][excl] = new_exclusion["exclusion_conditions"]["mcc"][excl]
                for excl in new_exclusion["exclusion_conditions"]["merchant"]:
                    policy["exclusion_conditions"]["merchant"][excl] = new_exclusion["exclusion_conditions"]["merchant"][excl]
            else:
                policy = {
                    "exclusion_conditions": new_exclusion["exclusion_conditions"]
                }

            exclusion_test_logger("=========after=========")
            exclusion_test_logger(json.dumps(policy, indent=4))
            # save policy to db
            put_policy(policy, policy_id)
        except Exception as exception:
            print("exception encountered while adding exclusion to policy:" + str(exception))


def add_new_exclusion(new_exclusion: dict):
    """Invoked by exclusion service whenever a new exclusion is created
    Adds a new exclusion to current policies, across all the exclusion's dates
    Iterates through all the dates of the exclusion, and calls add_exclusion_to_policy"""
    date_list = generate_dates(
        new_exclusion["exclusion_start_date"], new_exclusion["exclusion_end_date"])
    for date_to_add in date_list:
        add_exclusion_to_policy(new_exclusion, date_to_add)
    
    return {
        "statusCode": 200,
        "body": "successfully applied new exclusion to existing policies"
    }


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
        if action == "add_new_campaign":
            resp = add_new_campaign(body["data"])
        elif action == "add_new_exclusion":
            resp = add_new_exclusion(body["data"])

        elif action== "test_get_policy":
            resp = get_policy(body["data"]["policy_id"])
        elif action == "test_get_campaign":
            resp = get_all_campaigns()
        elif action == "test_put_policy":
            resp = put_policy(body["data"], body["data"]["policy_id"])
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
# .___________. _______     _______.___________. __  .__   __.   _______ 
# |           ||   ____|   /       |           ||  | |  \ |  |  /  _____|
# `---|  |----`|  |__     |   (----`---|  |----`|  | |   \|  | |  |  __  
#     |  |     |   __|     \   \       |  |     |  | |  . `  | |  | |_ | 
#     |  |     |  |____.----)   |      |  |     |  | |  |\   | |  |__| | 
#     |__|     |_______|_______/       |__|     |__| |__| \__|  \______| 
# Functions for testing environment

def campaign_test_logger(log_msg):
    """Function to log all the events during campaign addition"""
    # print(log_msg)
    LOGGER.info(log_msg)
    pass

def exclusion_test_logger(log_msg):
    """Function to log all the events during exclusion addition"""
    LOGGER.info(log_msg)
    pass

# if __name__ == "__main__":
#     generate_policies("01-01-2020", "31-12-2022")
#     print("===========================after generating==========================")
#     print(json.dumps(POLICY_DATABASE, indent=4))

#     test_new_campaign = {
#         "campaign_name": "Test promo",
#         "campaign_start_date": "08-06-2022",
#         "campaign_description": "Test promo",
#         "card_type": "scis_shopping",
#         "campaign_end_date": "11-06-2022",
#         "campaign_id": "01-06-2021_Test promo",
#         "campaign_priority": "21",
#         "campaign_conditions": [
#             {
#                 "campaign": "Test Promo Top"
#             },
            
#             {
#                 "campaign": "Test Promo Bottom"
#             }
#         ]
#     }
#     add_new_campaign(test_new_campaign)
#     print("===========================after adding new campaign==========================")
#     print(json.dumps(POLICY_DATABASE, indent=4))