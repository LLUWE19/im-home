#!/usr/bin/env python2
# -*-: coding utf-8 -*-

from hermes_python.hermes import Hermes
import requests as rq
import ConfigParser
import json
import io

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIGURATION_INI = "config.ini"

MQTT_IP_ADDR = "192.168.0.136"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

INTENT_IM_HOME = "LLUWE19:user_arrives_home"
INTENT_ANSWER = "LLUWE19:user_gives_answer"
INTENT_PERCENTAGE = "LLUWE19:user_gives_percentage"
INTENT_COLOR = "LLUWE19:user_gives_color"

last_question = None
light_on = False
light_color = None
light_brightness = None
tv_on = False
SessionStates = {}


class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section: {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()


def user_arrives_home(hermes, intent_message):
    print("Intent callback: user arrived home.")
    global last_question
    sentence = "welcome home... would you like the lights on"
    print("Set up home for user, last question: ", sentence)
    last_question = sentence
    print("Continuing session")
    hermes.publish_continue_session(intent_message.session_id, sentence, [INTENT_ANSWER])


def user_gives_answer(hermes, intent_message):
    global light_brightness
    global light_color
    global light_on
    global tv_on
    global last_question

    print("User is giving an answer...")
    print("Reading the config file")
    conf = read_configuration_file(CONFIGURATION_INI)
    autho = conf['secret']['http_api_password']
    header = {
        'Authorization': autho,
        "Content-Type": "application/json",
    }
    session_id = intent_message.session_id

    answer = None

    if intent_message.slots.answer:
        answer = intent_message.slots.answer.first().value
        print("The user answered: " + answer)

    if intent_message.slots.color:
        light_color = intent_message.slots.color.first().value

    if intent_message.slots.percentage:
        light_brightness = intent_message.slots.percentage.first().value

    if last_question == "welcome home... would you like the lights on":
        if answer == "yes":
            light_on = True
            sentence = "okay... what color do you want the light"
        else:
            light_on = False
            sentence = "okay... did you want the tee vee on"
        last_question = sentence
        hermes.publish_continue_session(session_id, sentence, [INTENT_COLOR])

    if last_question == "okay... what color do you want the light":
        sentence = "okay... how bright do you want the light"
        last_question = sentence
        hermes.publish_continue_session(session_id, sentence, [INTENT_PERCENTAGE])

    if last_question == "okay... how bright do you want the light":
        print("User responded with brightness")
        sentence = "okay... did you want the tee vee on"
        last_question = sentence
        hermes.publish_continue_session(session_id, sentence, [INTENT_ANSWER])

    if last_question == "okay... did you want the tee vee on":
        if answer == "yes":
            tv_on = True
        else:
            tv_on = False
            print("Leaving the tv off")
        sentence = "okay... welcome home"

        print("Turning on the light")
        url = 'http://192.168.0.136:8123/api/services/light/turn_on'
        body = {
            "entity_id": "light.tall_lamp",
            "color": light_color,
            "brightness": light_brightness
        }
        json_body = json.dumps(body)
        request = rq.post(url, data=json_body, headers=header)

        print("Turning on the tv")
        url = 'http://192.168.0.136:8123/api/services/switch/turn_on'
        body = {
            "entity_id": "switch.living_room_tv"
        }
        json_body = json.dumps(body)
        request = rq.post(url, data=json_body, headers=header)

        last_question = sentence
        hermes.publish_end_session(session_id, sentence)


with Hermes(MQTT_ADDR) as h:

    h.subscribe_intent(INTENT_IM_HOME, user_arrives_home) \
        .subscribe_intent(INTENT_ANSWER, user_gives_answer) \
        .subscribe_intent(INTENT_COLOR, user_gives_answer) \
        .subscribe_intent(INTENT_PERCENTAGE, user_gives_answer) \
        .start()









