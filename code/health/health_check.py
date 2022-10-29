"""Return health."""
import json
import logging
import os

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Lambda handler for getting the health."""
    status = os.environ["STATUS"]
    statusCode = 200

    logger.info("status: " + status)

    if status != "ok":
        statusCode = 500

    return {
        "statusCode": statusCode,
        "body": json.dumps({"status": status, "region": os.environ["AWS_REGION"]}),
    }
