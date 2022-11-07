# content of test_sysexit.py
import boto3
from boto3.dynamodb.conditions import Attr
from intialise import create_users

client = boto3.client("dynamodb")

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


def test_user_service():
    create_users(TEST_USERS)

    table = boto3.resource("dynamodb", region_name="ap-southeast-1").Table(
        "user_service_table"
    )
    response = table.scan(FilterExpression=Attr("user_id").eq("marcusgohsh"))

    assert len(response["Items"]) == len(TEST_USERS)


# def test_reward_service():
#     create_rewards(TEST_TRANSACTIONS)

#     table = boto3.resource("dynamodb", region_name="ap-southeast-1").Table(
#             "reward_service_table"
#         )
#     response = table.scan(FilterExpression=Attr('card_id').eq('marcus_card_id_1'))

#     assert len(response['Items']) == 2
