import json
import boto3
from datetime import datetime, UTC

lex_client = boto3.client('lexv2-runtime', region_name='us-east-1')

def create_response_payload(response):
    messages = response.get('messages', [])
    sessionId = response.get('sessionId', '')
    return {
        "messages": [{
            "type": "unstructured",
            "unstructured": {
                "id": sessionId,
                "text": m['content'],
                "timestamp": datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        } for m in messages]
    }

def lambda_handler(event, context):

    print(event)
    sessionId = event.get('sessionId', '123456') # We should get a unique session id from the frontend
    messages = event['body'].get('messages', [])
    print(f"{sessionId=}")

    message_to_lex = messages[0]['unstructured']['text']
    print(message_to_lex)

    response = lex_client.recognize_text(
        botId='UYTUKLIOML',       
        botAliasId='TSTALIASID', 
        localeId='en_US',         
        sessionId=sessionId,        
        text=message_to_lex  
    )

    print(response)

    return create_response_payload(response)