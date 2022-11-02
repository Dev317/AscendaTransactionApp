# Run this to initialise base campaigns and exclusions on a a fresh set of dynamodb tables
# populates campaign service, exclusion service, calculation service
# make sure to change the dates as necessary


import requests

# replace with apig of system as necessary
# APIG_URL = "https://xxsnouhdr9.execute-api.ap-southeast-1.amazonaws.com/prod"
APIG_URL = "https://kd61m94cag.execute-api.ap-southeast-1.amazonaws.com/dev/"


def invoke_lambda(post_request: dict, end_point: str):
    """Packages a JSON message into a http request and invokes another service
    Returns a jsonified response object"""
    return requests.post(APIG_URL + end_point, json=post_request).json()

# sets the start and end dates for all 4 campaigns and standard exclusions
BASE_START_DATE = "09-06-2022"
BASE_END_DATE = "11-06-2022"

BASE_CAMPAIGNS = [
    {
        "campaign_name": "Grab promo",
        "campaign_start_date": "10-06-2022",
        "campaign_description": "Grab promo",
        "card_type": "scis_shopping",
        "campaign_end_date": "11-06-2022",
        "campaign_priority": "50",
        "campaign_conditions": [
            {
                "amount_greater_than": "100",
                "merchant_name_include": ["Grab"],
                "percentage_of_amount": "4",
                "calculation_reason": "Grab Promo - 4 miles per dollar with Grab, min spend 100 SGD"
            }
        ]
    },
    {
        "campaign_name": "Kaligo.com promo",
        "campaign_start_date": "10-06-2022",
        "campaign_description": "Kaligo.com promo",
        "card_type": "scis_premiummiles",
        "campaign_end_date": "11-06-2022",
        "campaign_priority": "50",
        "campaign_conditions": [
            {
                "merchant_name_include": ["Kaligo"],
                "percentage_of_amount": "6",
                "calculation_reason": "6 miles per dollar on all spend with Kaligo.com"
            }
        ]
    },
    {
        "campaign_name": "Kaligo.com promo",
        "campaign_start_date": "10-06-2022",
        "campaign_description": "Kaligo.com promo",
        "card_type": "scis_platinummiles",
        "campaign_end_date": "11-06-2022",
        "campaign_priority": "50",
        "campaign_conditions": [
            {
                "merchant_name_include": ["Kaligo"],
                "percentage_of_amount": "10",
                "calculation_reason": "10 miles per dollar on all spend with Kaligo.com"
            }
        ]
    },
    {
        "campaign_name": "Shell petrol promo",
        "campaign_start_date": "10-06-2022",
        "campaign_description": "Shell petrol promo",
        "card_type": "scis_freedom",
        "campaign_end_date": "11-06-2022",
        "campaign_priority": "50",
        "campaign_conditions": [
            {
                "mcc_include": ["5542"],
                "percentage_of_amount": "0.05",
                "calculation_reason": "5 percent cashback on all petrol spend with Shell till 31 December 2021"
            }
        ]
    },
    {
        "campaign_name": "SCIS Shopping Card Base",
        "campaign_start_date": BASE_START_DATE,
        "campaign_description": "SCIS Shopping Card Base campaign",
        "card_type": "scis_shopping",
        "campaign_end_date": BASE_END_DATE,
        "campaign_priority": "0",
        "campaign_conditions": [
            {
                "merchant_category_include": "Online",
                "percentage_of_amount": "10",
                "calculation_reason": "10 points/SGD on all online spend"
            },
            {
                "merchant_category_include": "Shopping",
                "percentage_of_amount": "4",
                "calculation_reason": "4 points/SGD on all shopping spend"
            },
            {
                "percentage_of_amount": "1",
                "calculation_reason": "1 point/SGD on spend"
            }
        ]
    },
    # {
    #     "campaign_name": "Shopee promo",
    #     "campaign_start_date": BASE_START_DATE,
    #     "campaign_description": "Shopee promo",
    #     "card_type": "scis_shopping",
    #     "campaign_end_date": "10-06-2022",
    #     "campaign_priority": "100",
    #     "campaign_conditions": [
    #         {
    #             "merchant_name_include": ["Shopee"],
    #             "percentage_of_amount": "5",
    #             "calculation_reason": "Shopee Promo - 5 points per dollar with Shopee"
    #         }
    #     ]
    # },
    {
        "campaign_name": "Freedom Card Base",
        "campaign_start_date": BASE_START_DATE,
        "campaign_description": "SCIS Freedom Card Base cashback amounts",
        "card_type": "scis_freedom",
        "campaign_end_date": BASE_END_DATE,
        "campaign_priority": "0",
        "campaign_conditions": [
            {
                "amount_greater_than": "2000",
                "percentage_of_amount": "0.03",
                "calculation_reason": "3 percent cashback for all expenditure above 2000 SGD"
            },
            {
                "amount_greater_than": "500",
                "percentage_of_amount": "0.01",
                "calculation_reason": "1 percent cashback for all expenditure above 500 SGD"
            },
            {
                "percentage_of_amount": "0.005",
                "calculation_reason": "0.5 percent cashback for all expenditure"
            }
        ]
    },
    {
        "campaign_name": "Platinum Miles Card Base",
        "campaign_start_date": BASE_START_DATE,
        "campaign_description": "SCIS Platinum Miles Card Base campaign",
        "card_type": "scis_platinummiles",
        "campaign_end_date": BASE_END_DATE,
        "campaign_priority": "0",
        "campaign_conditions": [
            {
                "mcc_type_include": "hotel",
                "currency_exclude": "SGD",
                "percentage_of_amount": "6",
                "calculation_reason": "6 miles/SGD on all foreign hotel spend"
            },
            {
                "mcc_type_include": "hotel",
                "percentage_of_amount": "3",
                "calculation_reason": "3 miles/SGD on all hotels spend"
            },
            {
                "currency_exclude": "SGD",
                "percentage_of_amount": "3",
                "calculation_reason": "3 miles/SGD on all foreign card spend"
            },
            {
                "percentage_of_amount": "1.4",
                "calculation_reason": "1.4 miles/SGD spent"
            }
        ]
    },
    {
        "campaign_name": "Premium Miles Card Base",
        "campaign_start_date": BASE_START_DATE,
        "campaign_description": "SCIS Premium Miles Card Base campaign",
        "card_type": "scis_premiummiles",
        "campaign_end_date": BASE_END_DATE,
        "campaign_priority": "0",
        "campaign_conditions": [
            {
                "mcc_type_include": "hotel",
                "percentage_of_amount": "3",
                "calculation_reason": "3 miles/SGD on all hotels spend"
            },
            {
                "currency_exclude": "SGD",
                "percentage_of_amount": "2.2",
                "calculation_reason": "2.2 miles/SGD on all foreign card spend"
            },
            {
                "percentage_of_amount": "1.1",
                "calculation_reason": "1.1 miles/SGD spent"
            }
        ]
    }
]

BASE_EXCLUSIONS = [
    {
        "exclusion_name": "Standard Exclusions",
        "exclusion_start_date": BASE_START_DATE,
        "exclusion_end_date": BASE_END_DATE,
        "card_type": ["scis_shopping", "scis_freedom", "scis_premiummiles", "scis_platinummiles"],
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

def create_campaigns(campaign_list: list):
    for campaign in campaign_list:
        try:
            post_request = {
                "action": "create",
                "data": campaign
            }
            invoke_lambda(post_request, "campaign")
        except Exception as exception:
            print("Failed to add campaign: ", campaign["campaign_name"])
            print(exception)


def create_exclusions(exclusion_list: list):
    for exclusion in exclusion_list:
        try:
            post_request = {
                "action": "create",
                "data": exclusion
            }
            invoke_lambda(post_request, "exclusion")
        except Exception as exception:
            print("Failed to add exclusion: ", exclusion["exclusion_name"])
            print(exception)

create_campaigns(BASE_CAMPAIGNS)
create_exclusions(BASE_EXCLUSIONS)

print("complete")

#mockup transactions
transaction1 = {
        "id": "7ce56f44-659a-453f-8bc4-5a102faada42",
        "card_id": "0fd148a9-a350-4567-9e6d-d768ab9c1932",
        "merchant": "Collier",
        "mcc": "4642",
        "currency": "SGD",
        "amount": "285.96",
        "sgd_amount": "2001",
        "transaction_id": "07110e8bf85f1a1229eaa5dcbdea68c51d537218143d0021945cfae8861e3efc",
        "transaction_date": "09-06-2022",
        "card_pan": "6771-8964-5359-9669",
        "card_type": "scis_freedom"
    }

get_reward(transaction1)


transaction2 = {
        "id": "7ce56f44-659a-453f-8bc4-5a102faada42",
        "card_id": "0fd148a9-a350-4567-9e6d-d768ab9c1932",
        "merchant": "Grab",
        "mcc": "4642",
        "currency": "SGD",
        "amount": "285.96",
        "sgd_amount": "132.81",
        "transaction_id": "07110e8bf85f1a1229eaa5dcbdea68c51d537218143d0021945cfae8861e3efc",
        "transaction_date": "09-06-2022",
        "card_pan": "6771-8964-5359-9669",
        "card_type": "scis_freedom"
    }

get_reward(transaction2)

transaction3 = {
        "id": "7ce56f44-659a-453f-8bc4-5a102faada42",
        "card_id": "0fd148a9-a350-4567-9e6d-d768ab9c1932",
        "merchant": "AXS",
        "mcc": "9399",
        "currency": "SGD",
        "amount": "285.96",
        "sgd_amount": "100.53",
        "transaction_id": "07110e8bf85f1a1229eaa5dcbdea68c51d537218143d0021945cfae8861e3efc",
        "transaction_date": "09-06-2022",
        "card_pan": "6771-8964-5359-9669",
        "card_type": "scis_freedom"
    }

get_reward(transaction3)

transaction4 = {
        "id": "7ce56f44-659a-453f-8bc4-5a102faada42",
        "card_id": "0fd148a9-a350-4567-9e6d-d768ab9c1932",
        "merchant": "Blacklisted Merchant",
        "mcc": "9399",
        "currency": "SGD",
        "amount": "285.96",
        "sgd_amount": "50.67",
        "transaction_id": "07110e8bf85f1a1229eaa5dcbdea68c51d537218143d0021945cfae8861e3efc",
        "transaction_date": "09-06-2022",
        "card_pan": "6771-8964-5359-9669",
        "card_type": "scis_freedom"
    }
