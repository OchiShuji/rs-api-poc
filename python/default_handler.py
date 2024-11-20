import boto3
import json
import os

API_ENDPOINT = os.environ["API_ENDPOINT"]
STAGE = os.environ["STAGE"]


def lambda_handler(event,context):
    apigw_management = boto3.client('apigatewaymanagementapi', endpoint_url=f"{API_ENDPOINT}/{STAGE}")
    try:
        connectionId = event.get('requestContext', {}).get('connectionId')
    except Exception:
        return {
            "statusCode": 503
        }
    text = "To invoke Bedrock API, set request.body.action = 'sendtext'"
    apigw_management.post_to_connection(ConnectionId=connectionId, Data=text)

    return {
        "statusCode": 200
    }