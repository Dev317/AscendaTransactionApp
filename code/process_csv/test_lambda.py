import csv
import json
import unittest

import boto3
from moto import mock_s3, mock_sqs

S3_BUCKET_NAME = "file-upload-8de7e6fe-776a-4481-80c4-e4959b3dfc42"
DEFAULT_REGION = "us-east-1"

S3_TEST_FILE_KEY = "test/new_prices.csv"
TEST_CSV_FILE_HEADER = [
    "id",
    "transaction_id",
    "merchant",
    "mcc",
    "currency",
    "amount",
    "transaction_date",
    "card_id",
    "card_pan",
    "card_type",
]
# "cfc76f33-467d-48aa-96ab-d79394710a2b","27099f9663444ec56ae1dc920514bc4b451a8ed2e998bc176dec1ee56d4cd8a9","Williamson","5122","SGD",9306.49,"2021-09-01","01eca9de-9ff3-4d16-be03-75f228fc207f","4462-0971-1327-7064","scis_premiummiles"
TEST_CSV_FILE_CONTENT = [
    "cfc76f33-467d-48aa-96ab-d79394710a2b",
    "27099f9663444ec56ae1dc920514bc4b451a8ed2e998bc176dec1ee56d4cd8a9",
    "Williamson",
    5122,
    "SGD",
    9306.49,
    "2021-09-01",
    "01eca9de-9ff3-4d16-be03-75f228fc207f",
    "4462-0971-1327-7064",
    "scis_platinummiles",
]
S3_TEST_FILE_CONTENT = [
    {
        "id": "cfc76f33-467d-48aa-96ab-d79394710a2b",
        "transaction_id": "27099f9663444ec56ae1dc920514bc4b451a8ed2e998bc176dec1ee56d4cd8a9",
        "merchant": "Williamson",
        "mcc": 5122,
        "currency": "SGD",
        "amount": 9306.49,
        "sgd_amount": 9306.49,
        "transaction_date": "2021-09-01",
        "card_id": "01eca9de-9ff3-4d16-be03-75f228fc207f",
        "card_pan": "4462-0971-1327-7064",
        "card_type": "scis_platinummiles",
    }
]


@mock_s3
@mock_sqs
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

        # SQS Mock Setup
        self.sqs = boto3.resource("sqs")
        self.queue = self.sqs.create_queue(QueueName="test-transactions-queue")

    def test_get_data_from_file(self):
        from csv_processor import get_data_from_file

        file_content, _new_start_byte = get_data_from_file(
            S3_BUCKET_NAME, S3_TEST_FILE_KEY, 0, 1000
        )

        self.assertEqual(file_content, S3_TEST_FILE_CONTENT)

    def test_send_message_to_queue(self):
        import csv_processor
        from csv_processor import send_message_to_queue

        csv_processor.SQS_QUEUE_URL = self.queue.url

        send_message_to_queue(S3_TEST_FILE_CONTENT)

        sqs_messages = self.queue.receive_messages()

        self.assertEqual(json.loads(sqs_messages[0].body), S3_TEST_FILE_CONTENT)

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
