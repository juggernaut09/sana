# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Union, Optional
import re, requests
from rasa_sdk import Action, Tracker
from rasa_sdk.forms import FormAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
    FollowupAction,
    AllSlotsReset,
    BotUttered,
    SlotSet,
    SessionStarted
)
class ActionGetStarted(Action):
    def name(self) -> Text:
        return "action_get_started"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        buttons=[]
        buttons.append({
            "title": "about us",
            "payload": "about us"
        })
        buttons.append({
            "title": "Core offerings",
            "payload": "core offerings"
        })
        buttons.append({
            "title": "Industries We impact",
            "payload": "industries we impact"
        })
        buttons.append({
            "title": "Recent Stories",
            "payload": "recent stories"
        })
        buttons.append({
            "title": "Contact Us",
            "payload": "contact us"
        })
        buttons.append({
            "title": "AI Services",
            "payload": "Ai services"
        })
        buttons.append({
            "title": "Block Chain Services",
            "payload": "Block Chain"
        })
        buttons.append({
            "title": "Cloud and Bigdata Services",
            "payload": "Cloud and Bigdata"
        })
        dispatcher.utter_message(text="Hello, My name is Sana The Vitwit Bot.", buttons=buttons)


        return [UserUtteranceReverted()]
class ActionHelloWorld(Action):
    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return [UserUtteranceReverted()]
class ActionGreetUser(Action):
    def name(self) -> Text:
        return "action_greet_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_greet_user")
        return [UserUtteranceReverted()]

class ActionPause(Action):
    """Pause the conversation"""

    def name(self) -> Text:
        return "action_pause"

    def run(self, dispatcher, tracker, domain) -> List[EventType]:
        return [ConversationPaused()]

INTENT_DESCRIPTION_MAPPING_PATH = "actions/intent_description_mapping.csv"
class ActionDefaultAskAffirmation(Action):
    """Asks for an affirmation of the intent if NLU threshold is not met."""

    def name(self) -> Text:
        return "action_default_ask_affirmation"

    def __init__(self) -> None:
        import pandas as pd

        self.intent_mappings = pd.read_csv(INTENT_DESCRIPTION_MAPPING_PATH)
        self.intent_mappings.fillna("", inplace=True)
        self.intent_mappings.entities = self.intent_mappings.entities.map(
            lambda entities: {e.strip() for e in entities.split(",")}
        )

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        intent_ranking = tracker.latest_message.get("intent_ranking", [])
        if len(intent_ranking) > 1:
            diff_intent_confidence = intent_ranking[0].get(
                "confidence"
            ) - intent_ranking[1].get("confidence")
            if diff_intent_confidence < 0.2:
                intent_ranking = intent_ranking[:2]
            else:
                intent_ranking = intent_ranking[:1]

        # for the intent name used to retrieve the button title, we either use
        # the name of the name of the "main" intent, or if it's an intent that triggers
        # the response selector, we use the full retrieval intent name so that we
        # can distinguish between the different sub intents
        first_intent_names = [
            intent.get("name", "")
            if intent.get("name", "") not in ["out_of_scope", "faq"]
            else tracker.latest_message.get("response_selector")
            .get(intent.get("name", ""))
            .get("full_retrieval_intent")
            for intent in intent_ranking
        ]

        message_title = (
            "Sorry, I'm not sure I've understood " "you correctly 🤔 Do you mean..."
        )

        entities = tracker.latest_message.get("entities", [])
        entities = {e["entity"]: e["value"] for e in entities}

        entities_json = json.dumps(entities)

        buttons = []
        for intent in first_intent_names:
            button_title = self.get_button_title(intent, entities)
            if "/" in intent:
                # here we use the button title as the payload as well, because you
                # can't force a response selector sub intent, so we need NLU to parse
                # that correctly
                buttons.append({"title": button_title, "payload": button_title})
            else:
                buttons.append(
                    {"title": button_title, "payload": f"/{intent}{entities_json}"}
                )

        buttons.append({"title": "Something else", "payload": "/trigger_rephrase"})

        dispatcher.utter_message(message_title, buttons=buttons)

        return []

    def get_button_title(self, intent: Text, entities: Dict[Text, Text]) -> Text:
        default_utterance_query = self.intent_mappings.intent == intent
        utterance_query = (self.intent_mappings.entities == entities.keys()) & (
            default_utterance_query
        )

        utterances = self.intent_mappings[utterance_query].button.tolist()

        if len(utterances) > 0:
            button_title = utterances[0]
        else:
            utterances = self.intent_mappings[default_utterance_query].button.tolist()
            button_title = utterances[0] if len(utterances) > 0 else intent

        return button_title.format(**entities)


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        # Fallback caused by TwoStageFallbackPolicy
        if (
            len(tracker.events) >= 4
            and tracker.events[-4].get("name") == "action_default_ask_affirmation"
        ):

            dispatcher.utter_message(template="utter_restart_with_button")
            return [ConversationPaused()]

        # Fallback caused by Core
        else:
            dispatcher.utter_message(template="utter_default")
            return [UserUtteranceReverted()]

#### faq.py

backend_url = "http://localhost:5000"
class ActionImpactIndustries(Action):
    def name(self) -> Text:
        return "action_impact_industries"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Fintech\nEducation\nHealthcare\nAgritech\nPharmaceuticals\nInternet\nLogistics\nMedia& Entertainment")
        return [UserUtteranceReverted()]


class ActionRecentStories(Action):
    def name(self) -> Text:
        return "action_recent_stories"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="To see our recent story on AI see the link below:\nhttps://medium.com/vitwit/your-everyday-machine-learning-pipeline-a30e436c786c")
        dispatcher.utter_message(text="To see our recent story on Blockchain see the link below:\nhttps://medium.com/vitwit/chain-reaction-1-launching-inter-blockchain-communication-agoric-and-cosmos-5081cf71f3fa")
        dispatcher.utter_message(text="To see our recent story on Cloud computing and Bigdata see the link below:\nhttps://medium.com/@theakshaygupta/easily-setup-custom-vpc-on-aws-with-terraform-a7240bf7c734?source=---------2------------------")
        return [UserUtteranceReverted()]

class ContactForm(FormAction):
    def name(self) -> Text:
        """Unique identifier of the form"""
        return "contact_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["name", "mobile", "email"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "name": [self.from_text(intent="inform")],
            "email": [
                self.from_entity(entity="email"),
                self.from_text(intent="inform"),
            ],
            "mobile": [
                self.from_entity(entity="mobile"),
                self.from_text(intent="inform"),
            ]
        }

    def validate_mobile(self,
                    value: Text,
                    dispatcher: CollectingDispatcher,
                    tracker: Tracker,
                    domain: Dict[Text, Any]) -> Optional[Text]:

                    match = re.match("^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$", value)
                    if match:
                        # validation succeeded
                        return {'mobile': value}
                    else:
                        dispatcher.utter_message(text="Please check your mobile number you have typed")
                        # validation failed, set this slot to None, meaning the
                        # user will be asked for the slot again
                        return {'mobile': None}

    def validate_email(self,
                    value: Text,
                    dispatcher: CollectingDispatcher,
                    tracker: Tracker,
                    domain: Dict[Text, Any]) -> Optional[Text]:

                    match = re.match("[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+", value)
                    if match:
                        # validation succeeded
                        return {'email': value.lower()}
                    else:
                        dispatcher.utter_message(text='Please give a valid Email ID')
                        # validation failed, set this slot to None, meaning the
                        # user will be asked for the slot again
                        return {'email': None}

    def submit(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
            ) -> List[Dict]:
            my_obj = {
                "email": tracker.get_slot("email"),
                "mobile": tracker.get_slot("mobile"),
                "name": tracker.get_slot("name")
            }
            response = requests.post("{}/contactus".format(backend_url), json=my_obj)
            body = response.json()
            if response.status_code == 409 or response.status_code == 401 or response.status_code == 500:
                dispatcher.utter_message(text=body['message'])
                dispatcher.utter_message(text="If you have general questions about Vitwit,\n please head to our official website(https://vitwit.com/), otherwise contact\n us at [+91 63009 46153](mailto:contact@Vitwit.com) for anything else.")
                return[AllSlotsReset()]
            elif response.status_code == 200:
                dispatcher.utter_message(text="Dear, {} Your details have been successfully submitted, You will be contacted by our HR team shortly".format(tracker.get_slot("name")))
                dispatcher.utter_message(text="If you have general questions about Vitwit,\n please head to our official website(https://vitwit.com/), otherwise contact\n us at [+91 63009 46153](mailto:contact@Vitwit.com) for anything else.")
                return[UserUtteranceReverted(), AllSlotsReset()]


class ActionExplainSignupForm(Action):
    """Returns the explanation for the signup form questions"""

    def name(self) -> Text:
        return "action_explain_contact_form"

    def run(self, dispatcher, tracker, domain) -> List[EventType]:
        requested_slot = tracker.get_slot("requested_slot")

        if requested_slot not in SignupForm.required_slots(tracker):
            dispatcher.utter_message(
                text="Sorry, I didn't get that. Please rephrase or answer the question "
                "above."
            )
            return []

        dispatcher.utter_message(template=f"utter_explain_{requested_slot}")
        return []


### services.py

class ActionServiceAi(Action):
    def name(self) -> Text:
        return "action_service_ai"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Our Applied AI services will help scale your business by building fully autonomous & automated organisations")
        dispatcher.utter_message(text="To see our recent story on AI see the link below:\nhttps://medium.com/vitwit/your-everyday-machine-learning-pipeline-a30e436c786c")
        return [UserUtteranceReverted()]

class ActionServiceBC(Action):
    def name(self) -> Text:
        return "action_service_bc"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Blockchain is the future and it’s already here. Our expert Blockchain developers will help you in adopting the technology of the future.")
        dispatcher.utter_message(text="To see our recent story on Blockchain see the link below:\nhttps://medium.com/vitwit/chain-reaction-1-launching-inter-blockchain-communication-agoric-and-cosmos-5081cf71f3fa")
        return [UserUtteranceReverted()]


class ActionServiceCloud(Action):
    def name(self) -> Text:
        return "action_service_cloud"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="With our expertise in cloud computing & Big data, we deliver diverse range of cloud solutions to help you transform your business.")
        dispatcher.utter_message(text="To see our recent story on Cloud computing and Bigdata see the link below:\nhttps://medium.com/@theakshaygupta/easily-setup-custom-vpc-on-aws-with-terraform-a7240bf7c734?source=---------2------------------")
        return [UserUtteranceReverted()]


class ActionCoreOfferings(Action):
    def name(self) -> Text:
        return "action_core_offerings"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        buttons = []
        buttons.append({
            'title': "Artificial intelligence",
            'payload': 'Artificial Intelligence'
        })
        buttons.append({
            'title': "Block Chain",
            'payload': 'Block Chain'
        })
        buttons.append({
            'title': "Cloud Computing and Big Data",
            'payload': 'Cloud Computing and Big Data'
        })
        dispatcher.utter_message(text="We specialize in providing state of the art technology solutions in AI, Blockchain and Cloud Computing.", buttons=buttons)
        return [UserUtteranceReverted()]
