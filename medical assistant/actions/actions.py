from typing import Any, Text, Dict, List, Set, Union
import json
import random
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import os
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.forms import FormValidationAction
from datetime import datetime
from rasa_sdk.events import UserUtteranceReverted
from datetime import datetime


class AskEmail(Action):

    def name(self) -> Text:
        return "action_ask_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Enter you email :-")

        return []


class AskPassword(Action):

    def name(self) -> Text:
        return "action_ask_password"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Enter password")

        return []


class Actionaskname(Action):
    def name(self) -> Text:
        return "action_ask_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Enter name")

        return []


class ActionSubmit(Action):

    def name(self) -> Text:
        return "action_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("<Action submit>")
        email = tracker.get_slot("email")
        name = tracker.get_slot("name")
        dispatcher.utter_message(text=f"Hey {name}, you Email is {email}.")

        return [ SlotSet("name", None), SlotSet("password", None),
                SlotSet("email", None)]


class ValidateLogInForm(FormValidationAction):
    def __init__(self):
        self.event_history = set()

    def name(self) -> Text:
        return "validate_user_log_in_form"

    def check_intent_and_question(self, intent_name, tracker, dispatcher):
        for d in tracker.events[::-1]:
            if d.get("event") == "bot":
                last_bot = d
                intent_list = ["email", "Confirm password", "password", "name"]
                self.event_history.add(last_bot['text'])
                if intent_name in last_bot['text']:
                    return True, self.event_history
                else:
                    if last_bot['text'] == "Enter password":
                        dispatcher.utter_message(
                            text="Password length should be more the 8 charaters and contain atleast "
                                 "1 digit ")
                    else:
                        dispatcher.utter_message(
                            text="Invalid " + next((msg for msg in intent_list if msg in last_bot['text']), None))
                    return False, self.event_history

    async def required_slots(
            self,
            domain_slots: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
        print('<log in Form>')
        return ["email", "password", "name"]

    async def validate_email(
            self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        is_intent_question, is_already_filled = self.check_intent_and_question("email", tracker, dispatcher)
        if not is_intent_question:
            if "Enter you email :-" not in is_already_filled:
                return {"email": None}
            else:
                return {"email": slot_value}

        if "@" not in slot_value:
            dispatcher.utter_message(text="Wrong email format")
            return {"email": None}

        return {"email": slot_value}

    async def validate_OTP(
            self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        # is_intent_question, is_already_filled = self.check_intent_and_question("password", tracker, dispatcher)
        # if not is_intent_question:
        #     if "Enter password" not in is_already_filled:
        #         return {"password": None}
        #     else:
        #         return {"password": slot_value}
        if slot_value == "123456":
            return {"OTP": slot_value}

    # async def validate_name(
    #         self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    # ) -> Dict[Text, Any]:
    #
    #     return {"name": slot_value}


class ValidateSignupForm(FormValidationAction):
    def __init__(self):
        self.event_history = set()

    def name(self) -> Text:
        return "validate_user_sign_up_form"

    async def required_slots(
            self,
            domain_slots: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
        print('<sign Form>')
        return ["email", "OTP", "name"]

    def check_intent_and_question(self, intent_name, tracker, dispatcher):
        for d in tracker.events[::-1]:
            if d.get("event") == "bot":
                last_bot = d
                intent_list = ["email", "OTP", "name"]
                self.event_history.add(last_bot['text'])
                if intent_name in last_bot['text']:
                    return True, self.event_history
                else:
                    dispatcher.utter_message(
                        text="Invalid " + next((msg for msg in intent_list if msg in last_bot['text']), None))
                    return False, self.event_history

    async def validate_email(
            self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        is_intent_question, is_already_filled = self.check_intent_and_question("email", tracker, dispatcher)
        if not is_intent_question:
            if "Enter you email :-" not in is_already_filled:
                return {"email": None}
            else:
                return {"email": slot_value}

        if "@" not in slot_value:
            dispatcher.utter_message(text="Wrong email format")
            return {"email": None}

        return {"email": slot_value}

    async def validate_OTP(
            self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        is_intent_question, is_already_filled = self.check_intent_and_question("OTP", tracker, dispatcher)
        if not is_intent_question:
            if "Enter OTP" not in is_already_filled:
                return {"OTP": None}
            else:
                return {"OTP": slot_value}

        if slot_value == 123456:
            dispatcher.utter_message(text="Wrong OTP")
            return {"OTP": None}

        return {"OTP": slot_value}

    # async def validate_confirm_password(self, slot_value: Any, dispatcher: CollectingDispatcher,
    #                                     tracker: Tracker,
    #                                     domain: Dict[str, Any]) -> Dict[str, None]:
    #
    #     password = tracker.get_slot("password")
    #     confirm_password = slot_value
    #     is_intent_question, is_already_filled = self.check_intent_and_question("confirm_password", tracker, dispatcher)
    #     if not is_intent_question:
    #         if "Confirm password" not in is_already_filled:
    #             return {"confirm_password": None}
    #         else:
    #             return {"confirm_password": slot_value}
    #     if password == confirm_password:
    #         return {"confirm_password": slot_value}
    #     else:
    #         dispatcher.utter_message(text="Password Mismatch")
    #         return {"confirm_password": None}

    async def validate_name(
            self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("validate name")
        is_intent_question, is_already_filled = self.check_intent_and_question("name", tracker, dispatcher)
        if not is_intent_question:
            if "Enter name" not in is_already_filled:
                return {"name": None}
            else:
                return {"name": slot_value}

        print(slot_value)
        return {"name": slot_value}


