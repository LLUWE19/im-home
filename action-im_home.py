#!/usr/bin/env python2
# -*-: coding utf-8 -*-

"""
The "I'm Home" skill demonstrates the use of multi-turn dialogue with Snips as well as using the Hass API requests
to control devices in the living lab.

Telling Snips 'Im Home' will cause it to respond with a series of questions on how you would like the living lab to be
set up e.g. light and tv.

Once the "IM_HOME" intent has been triggered each other intent is classed as an answer to a question and will be called
back to the "user_gives_answer" function. Once snips has gathered enough information describing the desired settings
snips will make the call to the Hass API to carry out the settings.
"""

from hermes_python.hermes import Hermes
import requests as rq
import ConfigParser
import json
import io

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIGURATION_INI = "config.ini"

"""
Snips and home assistant both communicate using MQTT which is registered at the IP address of the PI.
"""
MQTT_IP_ADDR = "192.168.0.136"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

"""
Register required intents here, remember to include the user name before the name of the intent
"""
INTENT_IM_HOME = "LLUWE19:user_arrives_home"
INTENT_ANSWER = "LLUWE19:user_gives_answer"
INTENT_PERCENTAGE = "LLUWE19:user_gives_percentage"
INTENT_COLOR = "LLUWE19:user_gives_color"

"""Keep track of a previous question so we know where we are in the conversation"""
last_question = None

"""Keep track of the options the user requests"""
light_on = False
light_color = None
light_brightness = None
tv_on = False


class SnipsConfigParser(ConfigParser.SafeConfigParser):
    """THESE SHOULD BE MOVED INTO A SEPARATE HELPER FILE TO TIDY UP"""
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
    """
    Callback function registered to the "IM_HOME" intent. Acts as the entry point to the series of questions snips
    needs to ask to set up the home on arrival.
    """
    print("Intent callback: user arrived home.")
    global last_question
    sentence = "welcome home. would you like the lights on"
    print("Set up home for user, last question: ", sentence)
    last_question = sentence
    print("Continuing session")
    hermes.publish_continue_session(intent_message.session_id, sentence, [INTENT_ANSWER])


def user_gives_answer(hermes, intent_message):
    """
    The main function for managing the conversation. Each intent is registered to call back to this function and update
    the varibales that describe the living lab e.g. lights on, tv on. The conversation is tracked by remembering the
    last question asked. Once the details are known will then call the service to carry out the requests.
    """
    global light_brightness
    global light_color
    global light_on
    global tv_on
    global last_question

    print("light_brightness: ", light_brightness)
    print("light_color ", light_color)
    print("light_on: ", light_on)
    print("tv_on ", tv_on)
    print("Last_question: ", last_question)

    print("User is giving an answer...")
    print("Reading the config file")
    conf = read_configuration_file(CONFIGURATION_INI)
    autho = conf['secret']['http_api_password']
    header = {
        'Authorization': autho,
        "Content-Type": "application/json",
    }
    session_id = intent_message.session_id

    """
    Check and save any information the user has just given. Error checking and handling need to be implemented to ensure
    that the user is specifying valid values for each request.
    """
    answer = None
    if intent_message.slots.answer:
        answer = intent_message.slots.answer.first().value
        print("The user answered: " + answer)

    if intent_message.slots.color:
        print("message with color")
        light_color = intent_message.slots.color.first().value

    if intent_message.slots.percentage:
        print("message with brightness")
        light_brightness = intent_message.slots.percentage.first().value
        # Need to add some error checking to ensure that value is between 0 and 100 percent

    """Registering the users answers"""
    if last_question == "welcome home. would you like the lights on":
        if answer == "yes":
            light_on = True
            sentence = "okay. what color do you want the light"
            last_question = sentence
            hermes.publish_continue_session(session_id, sentence, [INTENT_COLOR])
        else:
            light_on = False
            sentence = "okay. did you want the tee vee on"
            last_question = sentence
            hermes.publish_continue_session(session_id, sentence, [INTENT_ANSWER])

    elif last_question == "okay. what color do you want the light":
        sentence = "okay. how bright do you want the light"
        last_question = sentence
        hermes.publish_continue_session(session_id, sentence, [INTENT_PERCENTAGE])

    elif last_question == "okay. how bright do you want the light":
        print("User responded with brightness")
        sentence = "okay. did you want the tee vee on"
        last_question = sentence
        hermes.publish_continue_session(session_id, sentence, [INTENT_ANSWER])

    elif last_question == "okay. did you want the tee vee on":
        if answer == "yes":
            tv_on = True
        else:
            tv_on = False
            print("Leaving the tv off")
        sentence = "okay. welcome home"

        """We now have enough information to call relevant services"""
        if light_on:
            print("Turning on the light")
            url = 'http://192.168.0.136:8123/api/services/light/turn_on'
            body = {
                "entity_id": "light.tall_lamp",
                "color_name": light_color,
                "brightness_pct": light_brightness
            }
            json_body = json.dumps(body)
            print(json_body)
            request = rq.post(url, data=json_body, headers=header)

        if tv_on:
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

    """
    Register the callback functions for each registered intent.
    """
    h.subscribe_intent(INTENT_IM_HOME, user_arrives_home) \
        .subscribe_intent(INTENT_ANSWER, user_gives_answer) \
        .subscribe_intent(INTENT_COLOR, user_gives_answer) \
        .subscribe_intent(INTENT_PERCENTAGE, user_gives_answer) \
        .start()









