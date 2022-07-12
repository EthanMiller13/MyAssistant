import keyboard
import pyttsx3
from fuzzywuzzy import process
import json
import random
import time
import threading
import Modules
import colorama as c
import asyncio


def cyan(text: str): return c.Fore.CYAN + text + c.Fore.RESET


class Assistant:
    def __init__(self, rate, voice_id, matching_percent, max_idle_time):
        self.engine = pyttsx3.init()
        self.rate = rate
        self.voice_id = voice_id
        self.matching_percent = matching_percent
        self.engine.setProperty("rate", self.rate)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[self.voice_id].id)
        with open("Intents.json", 'r') as f:
            self.intents = json.load(f)
        self.max_idle_time = max_idle_time
        self.idle_time = 0
        self.idle = False

        #idle = threading.Thread(target=self.track_idle)
        #idle.start()

    def handle_command(self, command):
        if command == '':
            return
        responses = None
        matched = self.match(command)
        intent = None
        for item in self.intents:
            if item != "UNMATCHED" and matched in self.intents[item]["intents"]:
                responses = self.intents[item]["responses"]
                intent = item
        if responses is None:
            responses = self.intents["UNMATCHED"]["responses"]
            intent = "UNMATCHED"

        print(matched + f"({intent})")

        response = random.choice(responses)
        actions = self.intents[intent]["actions"]
        if len(actions) != 0:
            for action in actions:
                if action.endswith("joke"):
                    self.broadcast(["hi", ["sds", "sdsd"], "s", ["2"]], say=True, delay=0)

                elif action.endswith("date"):
                    self.broadcast(response.replace("{DATE}", Modules.get_date()))

                elif action.endswith("time"):
                    self.broadcast(response.replace("{TIME}", Modules.get_time()))

                elif action.endswith("googlesearch"):
                    intent_options = ["hi Bixby, search for ", "search for "]
                    search_key = command.lower()
                    for i in intent_options:
                        search_key = search_key.replace(i, "")
                    result = Modules.googlesearch(search_key)
                    if result is None:
                        response = random.choice(self.intents[intent]["error-responses"])
                        self.broadcast(response.replace("{SEARCH_KEY}", search_key))
                    else:
                        self.broadcast(response.replace("{SEARCH_KEY}", search_key))
                        self.broadcast(result)

                elif action.endswith("wikisearch"):
                    intent_options = ["who is ", "what is ", "tell me about ", "?", 'a', "an"]
                    search_key = command.lower()
                    for i in intent_options:
                        search_key = search_key.replace(i, "")
                    result = Modules.wikisearch(search_key)
                    if result is None:
                        response = random.choice(self.intents[intent]["error-responses"])
                        self.broadcast(response.replace("{SEARCH_KEY}", search_key))
                    else:
                        self.broadcast(response.replace("{SEARCH_KEY}", search_key))
                        self.broadcast(result[:result.find(".", 5)+1])

        else:
            if intent == "UNMATCHED":
                result = Modules.wikisearch(command)
                if result is None:
                    self.broadcast(random.choice(self.intents["UNMATCHED"]["responses"]))
                else:
                    response = random.choice(self.intents["Wikipedia"]["responses"])
                    self.broadcast(response.replace("{SEARCH_KEY}", command))
                    self.broadcast(result[:result.find(".", 5) + 1])
            else:
                self.broadcast(response)

    def match(self, command):
        intents = []
        for item in self.intents:
            if item != "Unmatched":
                for response in self.intents[item]["intents"]:
                    intents.append(response)
        print(intents)
        highest = process.extractOne(command, intents)
        if highest[1] >= self.matching_percent:
            return highest[0]
        else:
            return "Unmatched"

    def broadcast(self, text, say=True, delay=0.7):
        if type(text) is str:
            print(cyan(text))
            if say is True:
                if not text.startswith("https://") and not text.startswith("www"):
                    self.engine.say(text)
                    self.engine.runAndWait()
        elif type(text) is list:
            for t in text:
                time.sleep(delay)
                self.broadcast(t, say=say)

        else:
            exit("Unsupported datatype for self.broadcast()")

    def listen(self):
        command = input("Enter your command:\n")
        self.idle_time = 0
        return command

    async def track_idle(self):
        while not self.idle_time < self.max_idle_time:#keyboard.KEY_DOWN :#self.idle_time < self.max_idle_time:
            time.sleep(1)
            self.idle_time += 1
        self.idle = True

    def get_holder_response(self, holder: str, placeholder: str, intent_options: list, response : str):
        holder = holder.lower()
        for i in intent_options:
            holder = holder.replace(i, "")
        return response.replace(f"{placeholder.upper()}", holder)


def main():
    assistant = Assistant(
        rate=180,
        voice_id=2,
        matching_percent=90,
        max_idle_time=180
    )
    while assistant.idle is False:
        try:
            command = assistant.listen()
            assistant.handle_command(command)
        except Exception as error:
            assistant.broadcast(
                random.choice(assistant.intents["EXCEPTION"]["responses"]))
            assistant.broadcast(str(error))


if __name__ == "__main__":
    main()
