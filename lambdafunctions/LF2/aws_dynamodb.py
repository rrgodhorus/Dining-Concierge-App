import boto3
import json

dynamodb = boto3.client('dynamodb')
TABLE_NAME = 'yelp-restaurants'

def fetch_restaurant_data_by_ids(restaurant_ids):

    # Prepare the keys for BatchGetItem request
    keys = [{'id': {'S': key}} for key in restaurant_ids]  # 'id' is the partition key attribute name

    # Query DynamoDB using BatchGetItem
    response = dynamodb.batch_get_item(
        RequestItems={
            TABLE_NAME: {  
                'Keys': keys
            }
        }
    )
    
    items = response.get('Responses', {}).get(TABLE_NAME, [])

    return items