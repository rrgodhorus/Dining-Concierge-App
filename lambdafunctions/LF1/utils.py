# --- Helpers that build all of the responses ---


def elicit_slot(session_attributes, active_contexts, intent, slot_to_elicit, message):
    return {
        'sessionState': {
            'activeContexts':[{
                'name': 'intentContext',
                'contextAttributes': active_contexts,
                'timeToLive': {
                    'timeToLiveInSeconds': 600,
                    'turnsToLive': 1
                }
            }],
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ElicitSlot',
                'slotToElicit': slot_to_elicit
            },
            'intent': intent,
        }
    }


def confirm_intent(active_contexts, session_attributes, intent, message):
    return {
        'sessionState': {
            'activeContexts': [active_contexts],
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ConfirmIntent'
            },
            'intent': intent
        }
    }


def close(session_attributes, active_contexts, fulfillment_state, intent, message):
    response = {
        'sessionState': {
            'activeContexts':[{
                'name': 'intentContext',
                'contextAttributes': active_contexts,
                'timeToLive': {
                    'timeToLiveInSeconds': 600,
                    'turnsToLive': 1
                }
            }],
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close',
            },
            'intent': intent,
        },
        'messages': [{'contentType': 'PlainText', 'content': message}]
    }

    return response


def delegate(session_attributes, active_contexts, intent, message):
    return {
        'sessionState': {
            'activeContexts':[{
                'name': 'intentContext',
                'contextAttributes': active_contexts,
                'timeToLive': {
                    'timeToLiveInSeconds': 600,
                    'turnsToLive': 1
                }
            }],
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Delegate',
            },
            'intent': intent,
        },
        'messages': [{'contentType': 'PlainText', 'content': message}]
    }


def initial_message(intent_name):
    response = {
            'sessionState': {
                'dialogAction': {
                    'type': 'ElicitSlot',
                    'slotToElicit': 'LocationSlot'
                },
                'intent': {
                    'confirmationState': 'None',
                    'name': intent_name,
                    'state': 'InProgress'
                }
            }
    }
    
    return response