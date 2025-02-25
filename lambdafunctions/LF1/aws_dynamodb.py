import boto3
import json

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'session-store'

def save_session(session_id, session_data):
    table = dynamodb.Table(TABLE_NAME)
    session_data['id'] = session_id
    response = table.put_item(
        Item=session_data
    )
    return response