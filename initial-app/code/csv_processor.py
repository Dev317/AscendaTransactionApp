"""
Simple Lambda function that reads file from S3 bucket and saves
its content to DynamoDB table
"""
#!/usr/bin/env python3

import json
import logging
import os
from decimal import Decimal

import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
DB_TABLE_NAME = os.environ.get("DB_TABLE_NAME", "transaction-records-table")

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 1000))

S3_CLIENT = boto3.client("s3")
DYNAMODB_CLIENT = boto3.resource("dynamodb", region_name=AWS_REGION)
DYNAMODB_TABLE = DYNAMODB_CLIENT.Table(DB_TABLE_NAME)


def get_filesize(bucket, key):
    try:
        obj = S3_CLIENT.head_object(Bucket=bucket, Key=key)
        LOGGER.info(f"File size: {obj['ContentLength']}")
        return obj["ContentLength"]
    except Exception as exc:
        raise exc


def get_data_from_file(bucket, key, start_byte, end_byte):
    """
    Function reads CSV file uploaded to S3 bucket
    """
    response = S3_CLIENT.get_object(
        Bucket=bucket, Key=key, Range=f"bytes={start_byte}-{end_byte}"
    )

    newline = "\r\n".encode()

    chunk = response["Body"].read()
    last_newline = chunk.rfind(newline)
    content = chunk[0 : last_newline + 1].decode("utf-8")

    records = content.splitlines()
    if start_byte == 0:
        records.pop(0)

    data = []
    for record in records:
        LOGGER.info(f"Reading {record}...")
        record_data = record.split(",")
        item = {
            "id": str(record_data[0]),
            "cardId": str(record_data[1]),
            "merchant": str(record_data[2]),
            "mcc": int(record_data[3]) if len(record_data[3]) > 0 else 0,
            "currency": str(record_data[4]),
            "amount": float(record_data[5]),
            "sgdAmount": float(record_data[6]),
            "transactionId": str(record_data[7]),
            "date": str(record_data[8]),
            "cardPan": str(record_data[9]),
            "cardType": str(record_data[10]),
        }
        data.append(item)
        LOGGER.info("Processing: %s", item)

    LOGGER.info(f"Successfully processed {len(data)} records from {bucket}/{key}")

    new_start_byte = start_byte + last_newline + 2
    return (data, new_start_byte)


def save_data_to_db(data):
    """
    Function saves data to DynamoDB table
    """
    item = json.loads(json.dumps(data), parse_float=Decimal)
    result = DYNAMODB_TABLE.put_item(Item=item)
    return result


def is_final_iteration(next_start_byte, file_size, chunk_size):
    if (next_start_byte + chunk_size) >= file_size:
        return True
    else:
        return False


def handler(event, context):
    """
    Main Lambda function method
    """
    LOGGER.info("Event structure: %s", json.dumps(event))

    s3_bucket = event["s3_bucket"]
    s3_file = event["s3_file"]

    file_size = get_filesize(s3_bucket, s3_file)

    if "handler" not in event:
        # First invocation
        start_byte = 0
        end_byte = CHUNK_SIZE

        if end_byte > file_size:
            end_byte = file_size

        LOGGER.info(f"New invocation - Start Byte: {start_byte}, End Byte: {end_byte}")

        data, next_start_byte = get_data_from_file(
            s3_bucket, s3_file, start_byte, end_byte
        )

        for item in data:
            save_data_to_db(item)
            # put calculatiton code here
            # put save_reward_to_db here
            # todo: error handling to catch failed calculations and flag it

        final_iteration = is_final_iteration(start_byte, file_size, CHUNK_SIZE)
        event["handler"] = {
            "results": {"startByte": next_start_byte, "finished": final_iteration}
        }
    else:
        start_byte = event["handler"]["results"]["startByte"]
        end_byte = start_byte + CHUNK_SIZE

        LOGGER.info(f"Continued - Start Byte: {start_byte}, End Byte: {end_byte}")

        if end_byte > file_size:
            end_byte = file_size

        final_iteration = is_final_iteration(start_byte, file_size, CHUNK_SIZE)

        data, next_start_byte = get_data_from_file(
            s3_bucket, s3_file, start_byte, end_byte
        )

        for item in data:
            save_data_to_db(item)

        event["handler"]["results"] = {
            "startByte": next_start_byte,
            "finished": final_iteration,
        }

    return event
