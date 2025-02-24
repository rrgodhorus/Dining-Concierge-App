import boto3
import requests
from requests.auth import HTTPBasicAuth
import json
import os

def get_restaurant_ids_by_cuisine(cuisine):
    region = 'us-east-1'  
    service = 'es'
    host = 'search-restaurant-opensearch-k7o45uftizt7p7fhrpipjugcdm.us-east-1.es.amazonaws.com'
    index = 'restaurants'  

    # It would be better to use AWS Secrets Manager, but it's not completely free
    opensearch_username = os.environ['OPENSEARCH_USERNAME'] 
    opensearch_password = os.environ['OPENSEARCH_PASSWORD']

    query = {
        "query": {
            "match": {
                "Cuisine": cuisine
            }
        },
        "size": 5  # We limit to 5 results
    }

    auth = HTTPBasicAuth(opensearch_username, opensearch_password)
    
    url = f'https://{host}/{index}/_search'
    headers = { "Content-Type": "application/json" }
    
    response = requests.post(url, auth=auth, headers=headers, json=query)

    restaurant_ids = [hit['_source']['RestaurantID'] for hit in response.json()['hits']['hits']]

    return restaurant_ids
