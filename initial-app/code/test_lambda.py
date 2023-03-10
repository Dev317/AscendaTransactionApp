import csv
import os
import unittest

import boto3
import mock
from moto import mock_dynamodb, mock_s3

S3_BUCKET_NAME = "file-upload-8de7e6fe-776a-4481-80c4-e4959b3dfc42"
DEFAULT_REGION = "us-east-1"

S3_TEST_FILE_KEY = "test/new_prices.csv"
TEST_CSV_FILE_HEADER = [
    "id",
    "card_id",
    "merchant",
    "mcc",
    "currency",
    "amount",
    "sgd_amount",
    "transaction_id",
    "date",
    "card_pan",
    "card_type",
]
TEST_CSV_FILE_CONTENT = [
    "7ce56f44-659a-453f-8bc4-5a102faada42",
    "0fd148a9-a350-4567-9e6d-d768ab9c1932",
    "Collier",
    4642,
    "SGD",
    285.96,
    0,
    "07110e8bf85f1a1229eaa5dcbdea68c51d537218143d0021945cfae8861e3efc",
    "27/8/2021",
    "6771-8964-5359-9669",
    "scis_platinummiles",
]
S3_TEST_FILE_CONTENT = [
    {
        "id": "7ce56f44-659a-453f-8bc4-5a102faada42",
        "cardId": "0fd148a9-a350-4567-9e6d-d768ab9c1932",
        "merchant": "Collier",
        "mcc": 4642,
        "currency": "SGD",
        "amount": 285.96,
        "sgdAmount": 0.0,
        "transactionId": "07110e8bf85f1a1229eaa5dcbdea68c51d537218143d0021945cfae8861e3efc",
        "date": "27/8/2021",
        "cardPan": "6771-8964-5359-9669",
        "cardType": "scis_platinummiles",
    }
]

DYNAMODB_TABLE_NAME = "transaction-records-table"


@mock_s3
@mock_dynamodb
@mock.patch.dict(os.environ, {"DB_TABLE_NAME": DYNAMODB_TABLE_NAME})
class TestLambdaFunction(unittest.TestCase):
    def setUp(self):
        # S3 Mock Setup
        with open("testfile.csv", "w", encoding="UTF-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(TEST_CSV_FILE_HEADER)
            writer.writerow(TEST_CSV_FILE_CONTENT)
        self.s3 = boto3.resource("s3", region_name=DEFAULT_REGION)
        self.s3_bucket = self.s3.create_bucket(Bucket=S3_BUCKET_NAME)
        self.s3_bucket.put_object(Key=S3_TEST_FILE_KEY, Body=open("testfile.csv", "rb"))

        # DynamoDB Mock Setup
        self.dynamodb = boto3.client("dynamodb", region_name="ap-southeast-1")

        self.table_dict = self.dynamodb.create_table(
            TableName=DYNAMODB_TABLE_NAME,
            KeySchema=[{"KeyType": "HASH", "AttributeName": "id"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 30, "WriteCapacityUnits": 30},
        )

        self.table = boto3.resource("dynamodb", region_name="ap-southeast-1").Table(
            DYNAMODB_TABLE_NAME
        )

    def test_get_data_from_file(self):
        from csv_processor import get_data_from_file

        file_content, _new_start_byte = get_data_from_file(
            S3_BUCKET_NAME, S3_TEST_FILE_KEY, 0, 1000
        )

        self.assertEqual(file_content, S3_TEST_FILE_CONTENT)

    def test_save_data_to_db(self):
        from csv_processor import save_data_to_db

        for item in S3_TEST_FILE_CONTENT:
            save_data_to_db(item)

        db_response = self.table.scan(Limit=1)

        db_records = db_response["Items"]

        while "LastEvaluatedKey" in db_response:
            db_response = self.table.scan(
                Limit=1, ExclusiveStartKey=db_response["LastEvaluatedKey"]
            )
            db_records += db_response["Items"]

        self.assertEqual(len(S3_TEST_FILE_CONTENT), len(db_records))

    """
    def test_handler(self):
        from csv_processor import handler

        event = {
            'Records': [
                {
                    's3': {
                        'bucket': {
                            'name': S3_BUCKET_NAME
                        },
                        'object': {
                            'key': S3_TEST_FILE_KEY
                        }
                    }
                }
            ]
        }

        result = handler(event, {})
        self.assertEqual(result, {'StatusCode': 200, 'Message': 'SUCCESS'})
    """
