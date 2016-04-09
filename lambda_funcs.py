#!/usr/bin/env python2

from __future__ import print_function

from pathgen import get_instructions
from db_connection import Database


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId'] +
          ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SetDeviceWaypoint":
        return set_device_waypoint(intent, session)
    elif intent_name == "TravelTo":
        return travel_to(intent, session)
    elif intent_name == "WhereAmI":
        return where_am_i(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Where do you want to go?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "To get directions, ask how to get to a certain place."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying not to get lost. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def set_device_waypoint(intent, session):
    card_title = "Set device location"
    if 'Waypoint' not in intent['slots']:
        return simple_response(
            card_title,
            "I'm not sure where you want to set the location. Please try again",
            "I'm not sure where you want to set the location. You can tell me by saying, "
            "set device waypoint to Room 3180",
            False)
    db = Database()
    waypoint_name = intent['slots']['Waypoint']['value']
    waypoint = db.waypoint_by_name(waypoint_name)
    if not waypoint:
        return no_such_place_response(card_title, waypoint_name)
    db.set_device_waypoint(waypoint)
    return simple_response(
        card_title,
        "Device location set to " + waypoint.name,
        None,
        True)


def where_am_i(intent, session):
    card_title = "Where am I"
    db = Database()
    waypoint = db.get_device_waypoint()
    answer = "You are in " + waypoint.name + ". Do you want to go somewhere?"
    return simple_response(card_title, answer, answer, False)


def travel_to(intent, session):
    card_title = "Directions"
    if 'Waypoint' not in intent['slots']:
        return simple_response(
            card_title,
            "I'm not sure where you want to go. Please try again",
            "I'm not sure where you want to go. You can tell me by saying, "
            "how to get to Room 3180",
            False)
    waypoint_name = intent['slots']['Waypoint']['value']
    answer = ""
    end_session = True
    reprompt = None
    if waypoint_name.lower() == "rome":
        answer = "All roads lead to Rome."
    else:
        db = Database()
        target_wp = db.waypoint_by_name(waypoint_name)
        if not target_wp:
            return no_such_place_response(card_title, waypoint_name)
        device_wp = db.get_device_waypoint()
        answer = get_instructions(
            db.get_whole_fucking_graph(),
            device_wp.node_id,
            target_wp.node_id)
    return simple_response(
        card_title,
        answer,
        reprompt,
        end_session)


def no_such_place_response(title, name):
    answer = "I don't know a place named " + name + ". Please try again."
    return simple_response(title, answer, answer, False)

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def simple_response(title, output, reprompt_text, end_session):
    return build_response({}, build_speechlet_response(title, output, reprompt_text, end_session))
