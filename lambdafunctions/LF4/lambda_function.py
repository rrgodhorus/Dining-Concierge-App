import json
import boto3

from aws_dynamodb import retrieve_session_data
from aws_sqs import push_to_queue

def prepare_response(item):
    location = item.get("location")
    cuisine = item.get("cuisine")
    dining_date = item.get("dining_date")
    dining_time = item.get("dining_time")
    number_of_people = item.get("number_of_people")
    email = item.get("email")

    return f"{cuisine} restaurants in {location} on {dining_date} at {dining_time} for {number_of_people} people"

def insert_into_queue(item):
    message = {
        "location" : item.get("location","LOCATION"),
        "cuisine" : item.get("cuisine","CUISINE"),
        "dining_date" : item.get("dining_date", "DATE"),
        "dining_time" : item.get("dining_time", "TIME"),
        "number_of_people" : item.get("number_of_people", "PEOPLE"),
        "email" : item.get("email", "EMAIL")
    }
    response = push_to_queue(message)

def lambda_handler(event, context):
    print(event)
    http_method = event.get("httpMethod", "GET")
    session_id = event.get("sessionId")

    item = retrieve_session_data(session_id) # Query Dynamodb for session

    if not item:
        return {
            "saved_session": ""
        }

    if http_method == "POST":
        insert_into_queue(item)

    saved_session = prepare_response(item)
        
    return {
        "saved_session": saved_session
    }
    
    
