#!/usr/bin/env python2
# -*-: coding utf-8 -*-

from hermes_python.hermes import Hermes


CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIGURATION_INI = "config.ini"

MQTT_IP_ADDR = "192.168.0.136"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

INTENT_IM_HOME = "LLUWE19:user_arrives_home"
INTENT_ANSWER = "LLUWE19:give_answer"

last_question = None
SessionStates = {}


def user_arrives_home(hermes, intent_message):
    print("User has arrived home")
    global last_question
    sentence = "welcome home... would you like the lights on"
    last_question = sentence
    hermes.publish_continue_session(intent_message.session_id, sentence, ["LLUWE19:give_answer"])


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
        else:
            print("Leaving the light off")
        sentence = "okay... do you want the tv on"
        last_question = sentence
        hermes.publish_continue_session(session_id, sentence, ["LLUWE19:give_answer"])
    elif last_question == "okay... do you want the tv on":
        if answer == "yes":
            print("Turning on the tv")
        else:
            print("Leaving the tv off")
        sentence = "okay... welcome home"
        last_question = sentence
        hermes.publish_end_session(session_id, sentence)


with Hermes(MQTT_ADDR) as h:

    h.subscribe_intent(INTENT_IM_HOME, user_arrives_home) \
        .subscribe_intent(INTENT_ANSWER, user_gives_answer) \
        .start()