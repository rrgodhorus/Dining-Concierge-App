import boto3
from aws_opensearch import get_restaurant_ids_by_cuisine
from aws_sqs import load_messages_from_queue, delete_message_from_queue
from aws_dynamodb import fetch_restaurant_data_by_ids
from aws_ses import send_email

def lambda_handler(event, context):
    
    messages = load_messages_from_queue()

    if not messages:
        print("No messages found in the queue.")
        return

    for message in messages:
        print(f"Processing message: {message}")
        recipient_email = message['body']['email']
        cuisine = message['body']['cuisine']
        number_of_people = message['body'].get('number_of_people', "")
        dining_date = message['body'].get('dining_date', "")
        dining_time = message['body'].get('dining_time', "")
        print(f"{recipient_email=} {cuisine=}")

        restaurant_ids = get_restaurant_ids_by_cuisine(cuisine)
        print(f"Restaurant IDs: {restaurant_ids}")

        restaurants = fetch_restaurant_data_by_ids(restaurant_ids)

        send_email(recipient_email, restaurants, cuisine, number_of_people, dining_date, dining_time)
            
        delete_message_from_queue(message['receipt_handle'])
