import boto3
import json
import os

API_ENDPOINT = os.environ["API_ENDPOINT"]
STAGE = os.environ["STAGE"]
MODEL_ID = os.environ["MODEL_ID"]

def lambda_handler(event,context):
    brt = boto3.client(service_name='bedrock-runtime')
    apigw_management = boto3.client('apigatewaymanagementapi', endpoint_url=f"{API_ENDPOINT}/{STAGE}")

    connectionId = event.get('requestContext', {}).get('connectionId')

    text = event.get('body', {}).get('text')
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31", 
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{text}"
                    }
                ]
            }
        ],
        "max_tokens": 1024
    })
    
    modelId = MODEL_ID
    accept = 'application/json'
    contentType = 'application/json'

    try:
        response = brt.invoke_model_with_response_stream(body=body, modelId=modelId, accept=accept, contentType=contentType)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"{e}"
        }

    for event in response.get("body"):
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk['type'] == 'content_block_delta' and chunk['delta']['type'] == 'text_delta':
            print(chunk['delta']['text'])
            try:
                apigw_management.post_to_connection(ConnectionId=connectionId, Data=json.dumps(chunk['delta']['text']))
            except Exception as e:
                return {
                    "statusCode": 500,
                    "body": f"{e}"
                }

    return {
        "statusCode": 200
    }
