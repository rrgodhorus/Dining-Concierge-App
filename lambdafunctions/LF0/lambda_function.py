import json
import boto3
from datetime import datetime, UTC

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

    message_to_lex = event['messages'][0]['unstructured']['text']
    print(message_to_lex)

    lex_client = boto3.client('lexv2-runtime', region_name='us-east-1')
    
    response = lex_client.recognize_text(
        botId='UYTUKLIOML',       # Replace with your bot's ID
        botAliasId='TSTALIASID', # Replace with your bot alias ID
        localeId='en_US',          # Language code (e.g., en_US)
        sessionId='123456',        # Unique session ID for tracking conversation
        text=message_to_lex  # User input message
    )

    print(response)

    return create_response_payload(response)