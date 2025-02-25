import boto3
from utils import create_email_payload

ses_client = boto3.client('ses')
EMAIL_SENDER = "rr4433@nyu.edu"

def send_email(recipient_email, restaurants, cuisine, number_of_people, dining_date, dining_time):
    print(f"Sending email to {recipient_email}")
    email_payload = create_email_payload(restaurants, cuisine, number_of_people, dining_date, dining_time)
    response = ses_client.send_email(
        Source=EMAIL_SENDER,
        Destination={
            'ToAddresses': [recipient_email]
        },
        Message=email_payload
    )
    print(f"Email sent! Message ID: {response['MessageId']}")
    