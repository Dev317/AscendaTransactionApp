# Run this to initialise base campaigns and exclusions on a a fresh set of dynamodb tables
# populates campaign service, exclusion service, calculation service
# make sure to change the dates as necessary


import requests

# replace with apig of system as necessary
APIG_URL = "https://xxsnouhdr9.execute-api.ap-southeast-1.amazonaws.com/prod/"
# APIG_URL = "https://kd61m94cag.execute-api.ap-southeast-1.amazonaws.com/dev/"


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
                "calculation_reason": "Grab Promo - 4 miles per dollar with Grab, min spend 100 SGD",
            }
        ],
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
                "calculation_reason": "6 miles per dollar on all spend with Kaligo.com",
            }
        ],
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
                "calculation_reason": "10 miles per dollar on all spend with Kaligo.com",
            }
        ],
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
                "calculation_reason": "5 percent cashback on all petrol spend with Shell till 31 December 2021",
            }
        ],
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
                "calculation_reason": "10 points/SGD on all online spend",
            },
            {
                "merchant_category_include": "Shopping",
                "percentage_of_amount": "4",
                "calculation_reason": "4 points/SGD on all shopping spend",
            },
            {"percentage_of_amount": "1", "calculation_reason": "1 point/SGD on spend"},
        ],
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
                "calculation_reason": "3 percent cashback for all expenditure above 2000 SGD",
            },
            {
                "amount_greater_than": "500",
                "percentage_of_amount": "0.01",
                "calculation_reason": "1 percent cashback for all expenditure above 500 SGD",
            },
            {
                "percentage_of_amount": "0.005",
                "calculation_reason": "0.5 percent cashback for all expenditure",
            },
        ],
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
                "calculation_reason": "6 miles/SGD on all foreign hotel spend",
            },
            {
                "mcc_type_include": "hotel",
                "percentage_of_amount": "3",
                "calculation_reason": "3 miles/SGD on all hotels spend",
            },
            {
                "currency_exclude": "SGD",
                "percentage_of_amount": "3",
                "calculation_reason": "3 miles/SGD on all foreign card spend",
            },
            {
                "percentage_of_amount": "1.4",
                "calculation_reason": "1.4 miles/SGD spent",
            },
        ],
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
                "calculation_reason": "3 miles/SGD on all hotels spend",
            },
            {
                "currency_exclude": "SGD",
                "percentage_of_amount": "2.2",
                "calculation_reason": "2.2 miles/SGD on all foreign card spend",
            },
            {
                "percentage_of_amount": "1.1",
                "calculation_reason": "1.1 miles/SGD spent",
            },
        ],
    },
]

BASE_EXCLUSIONS = [
    {
        "exclusion_name": "Standard Exclusions",
        "exclusion_start_date": BASE_START_DATE,
        "exclusion_end_date": BASE_END_DATE,
        "card_type": [
            "scis_shopping",
            "scis_freedom",
            "scis_premiummiles",
            "scis_platinummiles",
        ],
        "exclusion_conditions": {
            "mcc": {
                "6051": "Quasi Cash Merchants - Prepaid top-ups",
                "9399": "Government Services-Not Elsewhere Classified | Excluded",
                "6540": "POI (Point of Interaction) Funding Transactions (Excluding MoneySend) | Taxis & public transport",
            },
            "merchant": {"Blacklisted Merchant": "Merchant has been blacklisted"},
        },
    }
]


def create_campaigns(campaign_list: list):
    for campaign in campaign_list:
        try:
            post_request = {"action": "create", "data": campaign}
            invoke_lambda(post_request, "campaign")
        except Exception as exception:
            print("Failed to add campaign: ", campaign["campaign_name"])
            print(exception)


def create_exclusions(exclusion_list: list):
    for exclusion in exclusion_list:
        try:
            post_request = {"action": "create", "data": exclusion}
            invoke_lambda(post_request, "exclusion")
        except Exception as exception:
            print("Failed to add exclusion: ", exclusion["exclusion_name"])
            print(exception)


def create_users(user_list: list):
    for user in user_list:
        try:
            post_request = {"action": "create", "data": user}
            invoke_lambda(post_request, "user")
        except Exception as exception:
            print("Failed to add user: ", user["first_name"])
            print(exception)


def create_rewards(transaction_list: list):
    # TODO do the transaction step!! especially the SQS part. this is just temp for testing of frontend
    for transaction in transaction_list:
        try:
            post_request = {"action": "calculate_reward", "data": transaction}
            invoke_lambda(post_request, "reward")
        except Exception as exception:
            print("Failed to calculate and add_reward: ", transaction["transaction_id"])
            print(exception)

def create_card_groups(cardgroup_list: list):
    for cardgroup in cardgroup_list:
        try:
            post_request = {"action": "create", "data": cardgroup}
            invoke_lambda(post_request, "card")
        except Exception as exception:
            print("Failed to add card group: ", cardgroup["group_name"])
            print(exception)


TEST_USERS = [
    {
        "user_id": "marcusgohsh",
        "first_name": "Marcus",
        "last_name": "Goh",
        "phone": "94223757",
        "email": "hi@marcu.sg",
        "created_at": "02-01-2022",
        "updated_at": "02-01-2022",
        "card_id": "marcus_card_id_1",
        "card_pan": "1234-1234-1234-1111",
        "card_type": "scis_freedom",
    },
    {
        "user_id": "marcusgohsh",
        "first_name": "Marcus",
        "last_name": "Goh",
        "phone": "94223757",
        "email": "hi@marcu.sg",
        "created_at": "02-01-2022",
        "updated_at": "02-01-2022",
        "card_id": "marcus_card_id_2",
        "card_pan": "1234-1234-1234-2222",
        "card_type": "scis_platinummiles",
    },
    {
        "user_id": "marcusgohsh",
        "first_name": "Marcus",
        "last_name": "Goh",
        "phone": "94223757",
        "email": "hi@marcu.sg",
        "created_at": "02-01-2022",
        "updated_at": "02-01-2022",
        "card_id": "marcus_card_id_3",
        "card_pan": "1234-1234-1234-3333",
        "card_type": "scis_premiummiles",
    },
    {
        "user_id": "marcusgohsh",
        "first_name": "Marcus",
        "last_name": "Goh",
        "phone": "94223757",
        "email": "hi@marcu.sg",
        "created_at": "02-01-2022",
        "updated_at": "02-01-2022",
        "card_id": "marcus_card_id_4",
        "card_pan": "1234-1234-1234-4444",
        "card_type": "scis_shopping",
    },
]


TEST_TRANSACTIONS = [
    {
        "id": "asdf1",
        "card_id": "marcus_card_id_1",
        "merchant": "Collier",
        "mcc": "4642",
        "currency": "SGD",
        "amount": "2001",
        "sgd_amount": "2001",
        "transaction_id": "testtx1",
        "transaction_date": "09-06-2022",
        "card_pan": "1234-1234-1234-1111",
        "card_type": "scis_freedom",
    },
    {
        "id": "asdf2",
        "card_id": "marcus_card_id_1",
        "merchant": "Grab",
        "mcc": "4642",
        "currency": "SGD",
        "amount": "285.96",
        "sgd_amount": "132.81",
        "transaction_id": "testtx2",
        "transaction_date": "09-06-2022",
        "card_pan": "1234-1234-1234-1111",
        "card_type": "scis_freedom",
    },
    {
        "id": "asdf3",
        "card_id": "marcus_card_id_1",
        "merchant": "AXS",
        "mcc": "9399",
        "currency": "SGD",
        "amount": "285.96",
        "sgd_amount": "100.53",
        "transaction_id": "testtx3",
        "transaction_date": "09-06-2022",
        "card_pan": "1234-1234-1234-1111",
        "card_type": "scis_freedom",
    },
    {
        "id": "asdf4",
        "card_id": "marcus_card_id_1",
        "merchant": "Blacklisted Merchant",
        "mcc": "9399",
        "currency": "SGD",
        "amount": "285.96",
        "sgd_amount": "50.67",
        "transaction_id": "testtx4",
        "transaction_date": "09-06-2022",
        "card_pan": "1234-1234-1234-1111",
        "card_type": "scis_freedom",
    },
]

CARD_GROUPS = [
    {
    "card_group": "scis_miles_group",
    "card_type": "scis_premiummiles",
    "card_name": "SCIS Premium Miles Card",
    "group_name": "SCIS Miles Programme",
    "group_description": "Rack up miles, reap more rewards.",
    "unit_prefix": "",
    "unit_suffix": " miles"
    },
    {
    "card_group": "scis_miles_group",
    "card_type": "scis_platinummiles",
    "card_name": "SCIS Platinum Miles Card",
    "group_name": "SCIS Miles Programme",
    "group_description": "Rack up miles, reap more rewards.",
    "unit_prefix": "",
    "unit_suffix": " miles"
    },
    {
    "card_group": "cashback_group",
    "card_type": "scis_shopping",
    "card_name": "SCIS Shopping Card",
    "group_name": "Cashback Programmes",
    "group_description": "Earn some quick cashback with SCIS!",
    "unit_prefix": "$",
    "unit_suffix": ""
    },
    {
    "card_group": "freedom_points_group",
    "card_type": "scis_freedom",
    "card_name": "SCIS Freedom Card",
    "group_name": "SCIS Freedom",
    "group_description": "Experience financial freedom with Freedom Points",
    "unit_prefix": "",
    "unit_suffix": " pts"
    }
]


def run():

    create_campaigns(BASE_CAMPAIGNS)
    create_exclusions(BASE_EXCLUSIONS)
    create_users(TEST_USERS)
    create_rewards(TEST_TRANSACTIONS)
    create_card_groups(CARD_GROUPS)
    print("complete")


run()
