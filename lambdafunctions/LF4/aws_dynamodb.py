import boto3
import json

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'session-store'
table = dynamodb.Table(TABLE_NAME)

def retrieve_session_data(session_id):
    response = table.get_item(Key={"id": session_id})
    return response.get('Item', {})