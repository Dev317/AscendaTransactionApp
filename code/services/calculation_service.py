import datetime
import json
import logging
import os
from datetime import timedelta
from decimal import Decimal

import boto3
import requests

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
POLICY_TABLE_NAME = os.environ.get(
    "POLICY_TABLE_NAME", "calculation_service_table")

DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
POLICY_TABLE = DYNAMODB_CLIENT.Table(POLICY_TABLE_NAME)

APIG_URL = os.environ.get(
    "APIG_URL", "https://xxsnouhdr9.execute-api.ap-southeast-1.amazonaws.com/prod/"
)

TESTING_TOGGLE = os.environ.get("TESTING_TOGGLE", False)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def invoke_lambda(post_request: dict, end_point: str):
    """Packages a JSON message into a http request and invokes another service
    Returns a jsonified response object"""
    return requests.post(APIG_URL + end_point, json=post_request).json()


#   ______ .______       __    __   _______
#  /      ||   _  \     |  |  |  | |       \
# |  ,----'|  |_)  |    |  |  |  | |  .--.  |
# |  |     |      /     |  |  |  | |  |  |  |
# |  `----.|  |\  \----.|  `--'  | |  '--'  |
#  \______|| _| `._____| \______/  |_______/
# Functions for basic Create, Read, Update, Delete that call other services


def get_all_campaigns() -> list:
    """Helper function to call on campaign service to retrieve ALL campaigns
    Returns a list of all campaign objects"""
    post_request = {"action": "get_all"}
    try:
        return invoke_lambda(post_request, "campaign")
    except Exception as exception:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred invoking the campaign service.",
            "error": str(exception),
        }


def get_all_exclusions() -> list:
    """Helper function to call on exclusion service to retrieve ALL exclusions
    Returns a list of all exclusion objects"""
    post_request = {"action": "get_all"}
    try:
        return invoke_lambda(post_request, "exclusion")
    except Exception as exception:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred invoking the exclusion service.",
            "error": str(exception),
        }


def get_policy(card_type: str, policy_date: dict) -> dict:
    """CRUD: get a single policy from the polcy table by a given card_type and policy_date
    Returns a policy in dict form"""
    try:
        response = POLICY_TABLE.get_item(
            Key={"card_type": card_type, "policy_date": policy_date}
        )
        LOGGER.info(
            "Attempting get policy from dynamodb, %s - %s", card_type, policy_date
        )
        LOGGER.info(json.dumps(response))
    except Exception as exception:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred getting policy by id.",
            "error": str(exception),
        }
    if "Item" in response:
        return response["Item"]
    else:
        return {}


def put_policy(policy):
    """Saves a given policy dict to the database by way of PUT aka overwrite"""
    try:
        LOGGER.info(
            "Attempting to save %s - %s to db",
            policy["card_type"],
            policy["policy_date"],
        )
        response = POLICY_TABLE.put_item(Item=policy)
        LOGGER.info(
            "Policy %s - %s saved to db", policy["card_type"], policy["policy_date"]
        )
    except Exception as exception:
        LOGGER.error(str(exception))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "An error occurred creating the campaign.",
            "error": str(exception),
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
    return datetime.date(
        year=int(input_date[6:]), month=int(input_date[3:5]), day=int(input_date[0:2])
    )


def generate_dates(start_date, end_date) -> list:
    """helper function to convert the start date and end date to a list of all days in the format: dd-mm-yy"""
    # TODO: stepping function to split this into different lambda chunks: generation of just 10 entries already takes 5 seconds
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
    LOGGER.info("entered gen policies")
    campaign_list = get_all_campaigns()
    for campaign in campaign_list:
        # set the dates to generate to the tighter range of the inputted date and the campaign's date
        start_date = get_later_date(
            left_bound_date, campaign["campaign_start_date"])
        end_date = get_earlier_date(
            right_bound_date, campaign["campaign_end_date"])
        date_list = generate_dates(start_date, end_date)
        for day in date_list:
            add_campaign_to_policy(campaign, day)

    LOGGER.info("generate_policies: done adding campaigns")
    exclusion_list = get_all_exclusions()
    for exclusion in exclusion_list:
        # set the dates to generate to the tighter range of the inputted date and the exclusion's date
        start_date = get_later_date(
            left_bound_date, exclusion["exclusion_start_date"])
        end_date = get_earlier_date(
            right_bound_date, exclusion["exclusion_end_date"])
        date_list = generate_dates(start_date, end_date)
        for day in date_list:
            add_exclusion_to_policy(exclusion, day)
    LOGGER.info("generate_policies: done adding exclusions")

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": "Sucessfully regenerated",
    }


def add_campaign_to_policy(new_campaign: dict, campaign_date: str):
    """Iterates through all the existing campaign conditions of a given date
    then inserts the new campaign's conditions in the right order"""
    campaign_test_logger(
        f"Adding {new_campaign['campaign_name']} to {campaign_date}")
    # policy_id = str(new_campaign["card_type"]) + "/" + str(campaign_date)
    try:
        policy = get_policy(new_campaign["card_type"], campaign_date)
        campaign_test_logger("=========before=========")
        campaign_test_logger(json.dumps(policy, indent=4))

        # pre-format campaign conditions (insert the campaign id and campaign priority)
        for condition in new_campaign["campaign_conditions"]:
            condition["campaign_name"] = new_campaign["campaign_name"]
            condition["campaign_priority"] = new_campaign["campaign_priority"]

        if not policy:
            policy = {
                "card_type": new_campaign["card_type"],
                "policy_date": campaign_date,
            }

        # TODO check if this campaign is already in the policy, if it is, replace it! (UPDATE of CRUD)

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
                if (
                    cur_index == -1
                ):  # exit condition for when it reaches the topmost policy
                    campaign_test_logger(
                        f"Found index to insert, inserting behind {cur_index}"
                    )
                    for condition in new_campaign["campaign_conditions"]:
                        policy["campaign_conditions"].insert(
                            cur_index + 1, condition)
                        cur_index = cur_index + 1
                    break
                prior_existing = int(
                    policy["campaign_conditions"][cur_index]["campaign_priority"]
                )
                prior_new = int(new_campaign["campaign_priority"])
                campaign_test_logger(
                    f"Comparing {prior_existing} to {prior_new}")
                if (
                    prior_existing > prior_new
                ):  # insert the incoming campaign right behind the next higher priority
                    campaign_test_logger(
                        f"Found index to insert, inserting behind {cur_index}"
                    )
                    for condition in new_campaign["campaign_conditions"]:
                        policy["campaign_conditions"].insert(
                            cur_index + 1, condition)
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
        put_policy(policy)
    except Exception as exception:
        LOGGER.error(
            "exception encountered while adding campaign to policy: %s", str(
                exception)
        )


def add_new_campaign(new_campaign: dict):
    """Invoked by campaign service whenever a new campaign is created
    Adds a new campaign to current policies, across all the campaign's dates
    Iterates through all the dates of the campaign, and calls add_campaign_to_policy"""
    try:
        LOGGER.info("entering add_new_campaign for loop")
        date_list = generate_dates(
            new_campaign["campaign_start_date"], new_campaign["campaign_end_date"]
        )
        for date_to_add in date_list:
            add_campaign_to_policy(new_campaign, date_to_add)
    except Exception as exception:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "message": "error adding new campaign",
            "error": repr(exception),
        }

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": "successfully appplied new campaign to existing policies",
    }


def add_exclusion_to_policy(new_exclusion: dict, exclusion_date: str):
    """Applies new exclusion it to a given policy date"""
    exclusion_test_logger(
        f"Adding {new_exclusion['exclusion_name']} to {exclusion_date}"
    )

    # for card_type in new_exclusion["card_type"]:
    # policy_id = str(card_type) + "/" + str(exclusion_date)
    try:
        policy = get_policy(new_exclusion["card_type"], exclusion_date)
        exclusion_test_logger("=========before=========")
        exclusion_test_logger(json.dumps(policy, indent=4))
        if policy:
            if (
                "exclusion_conditions" not in policy
            ):  # in case where there is no existing exclusions, create a blank one
                policy["exclusion_conditions"] = {"mcc": {}, "merchant": {}}
            for excl in new_exclusion["exclusion_conditions"]["mcc"]:
                policy["exclusion_conditions"]["mcc"][excl] = new_exclusion[
                    "exclusion_conditions"
                ]["mcc"][excl]
            for excl in new_exclusion["exclusion_conditions"]["merchant"]:
                policy["exclusion_conditions"]["merchant"][excl] = new_exclusion[
                    "exclusion_conditions"
                ]["merchant"][excl]
        else:
            policy = {
                "card_type": new_exclusion["card_type"],
                "policy_date": exclusion_date,
                "exclusion_conditions": new_exclusion["exclusion_conditions"],
            }

        exclusion_test_logger("=========after=========")
        exclusion_test_logger(json.dumps(policy, indent=4))
        # save policy to db
        put_policy(policy)
    except Exception as exception:
        LOGGER.error(
            "exception encountered while adding exclusion to policy: %s", str(
                exception)
        )


def add_new_exclusion(new_exclusion: dict):
    """Invoked by exclusion service whenever a new exclusion is created
    Adds a new exclusion to current policies, across all the exclusion's dates
    Iterates through all the dates of the exclusion, and calls add_exclusion_to_policy"""
    date_list = generate_dates(
        new_exclusion["exclusion_start_date"], new_exclusion["exclusion_end_date"]
    )
    for date_to_add in date_list:
        add_exclusion_to_policy(new_exclusion, date_to_add)

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": "successfully applied new exclusion to existing policies",
    }


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
        if action == "add_new_campaign":
            resp = add_new_campaign(body["data"])
        elif action == "add_new_exclusion":
            resp = add_new_exclusion(body["data"])
        elif action == "refresh_policies":
            resp = generate_policies(
                body["data"]["start_date"], body["data"]["end_date"]
            )
        elif action == "get_policy":
            resp = get_policy(body["data"]["card_type"],
                              body["data"]["policy_date"])
        elif action == "health":
            resp = "Service is healthy"

        # TESTING ENDPOINTS
        elif action == "test_get_campaign":
            resp = get_all_campaigns()
        elif action == "test_get_exclusions":
            resp = get_all_exclusions()
        elif action == "test_put_policy":
            resp = put_policy(body["data"])
        else:
            return {
                "statusCode": 500,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": "no such action",
            }
    except Exception as exception:
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
    if TESTING_TOGGLE:
        LOGGER.info(log_msg)


def exclusion_test_logger(log_msg):
    """Function to log all the events during exclusion addition"""
    if TESTING_TOGGLE:
        LOGGER.info(log_msg)
