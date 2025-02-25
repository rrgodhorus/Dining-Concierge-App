import json
import time
import os
import dateutil.parser
from datetime import datetime, timedelta
import logging
import boto3

from utils import elicit_slot, confirm_intent, close, delegate, initial_message

from aws_sqs import push_to_queue
from aws_dynamodb import save_session

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)



# --- Helper Functions ---


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(value):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary of the Slots section in the payloads.
    Note that this function would have negative impact on performance.
    """
    try:
        return value["value"]["interpretedValue"]
    except:
        return None

def isvalid_date(date_str, date_format="%Y-%m-%d"):
    try:
        date_obj = datetime.strptime(date_str, date_format)
        
        today = datetime.now().date()

        print("today: ", today, "given date: ", date_obj.date())
        
        # Check if the date is not in the past and within a month
        if today <= date_obj.date() <= today + timedelta(days=30):
            return True
        else:
            return False
    except ValueError:
        return False  # Invalid date format

def isvalid_time(time):
    formats = ["%I:%M %p", "%H:%M"]  # 12-hour with AM/PM and 24-hour format
    for time_format in formats:
        try:
            datetime.strptime(time, time_format)
            return True
        except ValueError:
            continue  # Try the next format
    return False  # If neither format worked, return False

def isvalid_number_of_people(number_of_people):
    try:
        if 0 < int(number_of_people) <= 10:
            return True
    except ValueError:
        return False


VALID_CUISINES = {"Chinese","Thai","Mexican","Italian","Japanese"}
VALID_CITIES = {"New York", "NYC", "Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"}

def validate_slots(intent_request):
    logger.debug('diningSuggestions intent: validate slots')

    intent = intent_request["sessionState"]["intent"]
    slots = intent.get("slots", {})

    location = try_ex(slots['LocationSlot'])
    cuisine = try_ex(slots['CuisineSlot'])
    dining_date = try_ex(slots['DiningDateSlot'])
    dining_time = try_ex(slots['DiningTimeSlot'])
    number_of_people = try_ex(slots['NumberOfPeopleSlot'])
    email = try_ex(slots['EmailSlot'])

    next_slot = intent_request.get("proposedNextState", {}).get("dialogAction", {}).get("slotToElicit", None)

    error_slot = None
    error_message = None

    print(location, cuisine, dining_time, number_of_people, email)

    if not location or location not in VALID_CITIES:
        error_slot = 'LocationSlot'
        error_message = 'Please provide a valid city (We currently support only New York City and its boroughs).'
    
    elif not cuisine or cuisine not in VALID_CUISINES:
        error_slot = 'CuisineSlot'
        error_message = f'Please enter a valid cuisine: ({", ".join(VALID_CUISINES)})'
    
    elif not dining_date or not isvalid_date(dining_date):
        error_slot = 'DiningDateSlot'
        error_message = 'Please enter a valid date that\'s not more than a month away.'
    
    elif not dining_time or not isvalid_time(dining_time):
        error_slot = 'DiningTimeSlot'
        error_message = 'Please enter a valid time in either 12-hour (AM/PM) or 24-hour format.'
    
    elif not number_of_people or not isvalid_number_of_people(number_of_people):
        error_slot = 'NumberOfPeopleSlot'
        error_message = 'Please enter a valid group size (1 to 10)'
    
    elif not email:
        error_slot = 'EmailSlot'
        error_message = 'Please enter a valid email address.'
    
    print(error_slot, error_message)

    # If the next slot is the error slot, clear the error message (because it hasn't been prompted yet)
    if error_slot == next_slot:
        error_slot = None

    if error_slot:
        return {
            "sessionState": {
                "dialogAction": {
                    "type": "ElicitSlot",
                    "slotToElicit": error_slot,
                },
                "intent": intent
            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": error_message
                }
            ]
        }

    return {
        "sessionState": {
            "dialogAction": {"type": "Delegate"},
            "intent": intent
        }
    }


""" --- Functions that control the bot's behavior --- """

def get_dining_suggestions(intent_request):
    logger.debug('diningSuggestions intent: fullfillment')

    slots = intent_request['sessionState']['intent']['slots']

    sessionId = intent_request['sessionId']
    
    location = try_ex(slots['LocationSlot'])
    cuisine = try_ex(slots['CuisineSlot'])
    dining_date = try_ex(slots['DiningDateSlot'])
    dining_time = try_ex(slots['DiningTimeSlot'])
    number_of_people = try_ex(slots['NumberOfPeopleSlot'])
    email = try_ex(slots['EmailSlot'])

    print(location, cuisine, dining_time, number_of_people, email)

    confirmation_status = intent_request['sessionState']['intent']['confirmationState']
    session_attributes = intent_request['sessionState'].get("sessionAttributes") or {}

    print(confirmation_status)

    intent = intent_request['sessionState']['intent']
    active_contexts = {}

    # Message to be sent
    message_body = {
        'location': location,
        'cuisine': cuisine,
        'dining_date': dining_date,
        'dining_time': dining_time,
        'number_of_people': number_of_people,
        'email': email
    }

    print("message_body= ", message_body)

    if confirmation_status == 'Confirmed':
            intent['confirmationState'] = "Confirmed"
            intent['state'] = "Fulfilled"
            
            response = push_to_queue(message_body)

            print("SQS response= ",response)

            # Now save this session to the DynamoDB table 
            save_session(sessionId, message_body)

            return close(
                session_attributes,
                active_contexts,
                'Fulfilled',
                intent,
                'You can expect my suggestions in your inbox shortly.'
            )

    
# --- Intents ---

def handle_dining_suggestions(intent_request):
    logger.debug('handle_dining_suggestions')

    if intent_request['invocationSource'] == 'DialogCodeHook':
        return validate_slots(intent_request)

    # Else for FullFillmentCodeHook
    return get_dining_suggestions(intent_request)

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    logger.debug(intent_request)   

    intent = intent_request['sessionState']['intent'] 
    session_attributes = intent_request['sessionState'].get("sessionAttributes") or {}
    active_contexts = {}
    
    intent_name = intent['name']

    if intent_name == 'DiningSuggestionsIntent':
        return handle_dining_suggestions(intent_request)
    
    elif intent_name == 'GreetingIntent':
        return close(
                session_attributes,
                active_contexts,
                'Fulfilled',
                intent,
                'Hello! How can I assist you today?'
            )
    
    elif intent_name == 'ThankYouIntent':
        return close(
                session_attributes,
                active_contexts,
                'Fulfilled',
                intent,
                'You\'re welcome! Let me know if you need anything else.'
            )
    

    return Exception('Intent with name ' + intent_name + ' not supported')

# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
   
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    print("Received event:", json.dumps(event))
    
    return dispatch(event)