'''
Simple Lambda function that reads file from S3 bucket and saves
its content to DynamoDB table
'''
#!/usr/bin/env python3

import json
import os
import logging
import boto3
from decimal import Decimal
import csv
import io

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get('AWS_REGION', 'ap-southeast-1')
DB_TABLE_NAME = os.environ.get('DB_TABLE_NAME', 'transaction-records-table')

S3_CLIENT = boto3.client('s3')
DYNAMODB_CLIENT = boto3.resource('dynamodb', region_name=AWS_REGION)
DYNAMODB_TABLE = DYNAMODB_CLIENT.Table(DB_TABLE_NAME)

def get_data_from_file(bucket, key):
    '''
    Function reads CSV file uploaded to S3 bucket
    '''
    response = S3_CLIENT.get_object(Bucket=bucket, Key=key)

    content = response['Body'].read().decode("utf-8")
    reader = csv.reader(io.StringIO(content))
    next(reader)

    data = []
    for row in reader:
        item = {
            "id": str(row[0]),
            "cardId": str(row[1]),
            "merchant": str(row[2]),
            "mcc": str(row[3]),
            "currency": str(row[4]),
            "amount": float(row[5]),
            "sgdAmount": float(row[6]),
            "transactionId": str(row[7]),
            "date": str(row[8]),
            "cardPan": str(row[9]),
            "cardType": str(row[10])
        }
        data.append(item)
        LOGGER.info('Processing: %s', item)

    LOGGER.info('Successfully processed all records from %s/%s', bucket, key)

    return data

def save_data_to_db(data):
    '''
    Function saves data to DynamoDB table
    '''
    item = json.loads(json.dumps(data), parse_float=Decimal)
    result = DYNAMODB_TABLE.put_item(Item=item)
    return result

def handler(event, context):
    '''
    Main Lambda function method
    '''
    LOGGER.info('Event structure: %s', event)

    for record in event['Records']:
        s3_bucket = record['s3']['bucket']['name']
        s3_file = record['s3']['object']['key']

        data = get_data_from_file(s3_bucket, s3_file)
        LOGGER.info('Length of data is %s', len(data))

        for item in data:
            save_data_to_db(item)

    return {
        'StatusCode': 200,
        'Message': 'SUCCESS'
    }