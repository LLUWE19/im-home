#!/usr/bin/env python2
# -*-: coding utf-8 -*-

from hermes_python.hermes import Hermes
import requests as rq
import configparser
import json

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIGURATION_INI = "config.ini"

MQTT_IP_ADDR = "192.168.0.136"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

INTENT_IM_HOME = "LLUWE19:user_arrives_home"
INTENT_ANSWER = "LLUWE19:user_gives_answer"

last_question = None
SessionStates = {}

config = configparser.ConfigParser()
config.read('config.ini')
autho = config['secret']['api_password']  # Reading the api_password from the config file

header = {
    'Authorization': autho,
    'content-type': 'application/json',
}


def user_arrives_home(hermes, intent_message):
    print("User has arrived home")
    global last_question
    sentence = "welcome home... would you like the lights on"
    last_question = sentence
    hermes.publish_continue_session(intent_message.session_id, sentence, [INTENT_ANSWER])


def user_gives_answer(hermes, intent_message):
    print("User is giving an answer")
    global last_question
    answer = None
    session_id = intent_message.session_id

    if intent_message.slots.answer:
        answer = intent_message.slots.answer.first().value

    if last_question == "welcome home... would you like the lights on":
        if answer == "yes":
            print("Turning on the light")
            url = 'http://192.168.0.136:8123/api/services/light/turn_on'
            body = {
                "entity_id": "light.tall_lamp"
            }
            json_body = json.dumps(body)
            request = rq.post(url, headers=header)
        else:
            print("Leaving the light off")
        sentence = "okay... do you want the tv on"
        last_question = sentence
        hermes.publish_continue_session(session_id, sentence, [INTENT_ANSWER])
    elif last_question == "okay... do you want the tv on":
        if answer == "yes":
            print("Turning on the tv")
            url = 'http://192.168.0.136:8123/api/services/switch/turn_on'
            body = {
                "entity_id": "switch.living_room_tv"
            }
            json_body = json.dumps(body)
            request = rq.post(url, headers=header)
        else:
            print("Leaving the tv off")
        sentence = "okay... welcome home"
        last_question = sentence
        hermes.publish_end_session(session_id, sentence)


with Hermes(MQTT_ADDR) as h:

    h.subscribe_intent(INTENT_IM_HOME, user_arrives_home) \
        .subscribe_intent(INTENT_ANSWER, user_gives_answer) \
        .start()