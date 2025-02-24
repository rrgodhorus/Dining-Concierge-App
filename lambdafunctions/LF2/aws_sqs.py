import boto3
import json

sqs = boto3.client('sqs')
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/908027405464/din_rec_queue'

def load_messages_from_queue():

    # Poll for messages from SQS
    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        AttributeNames=['All'],
        MaxNumberOfMessages=1,
        MessageAttributeNames=['All'],
        VisibilityTimeout=30,
        WaitTimeSeconds=0
    )

    messages = [ {
        'body': json.loads(message['Body']),
        'receipt_handle': message['ReceiptHandle']
     } for message in response.get('Messages',[])]

    return messages

def delete_message_from_queue(receipt_handle):
    sqs.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=receipt_handle
    )