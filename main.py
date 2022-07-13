import pyttsx3
from fuzzywuzzy import process
import json
import random
import time
import threading
import Modules
import colorama as c
import asyncio


def output(text: str):
    return c.Fore.CYAN + text + c.Fore.RESET


class Assistant:
    def __init__(self, rate, voiceId, matchingPercent, maxIdle):
        # Initalize TTS Engine
        self.engine = pyttsx3.init()

        # Set TTS Engine Properties
        self.rate = rate
        self.voiceId = voiceId
        self.engine.setProperty("rate", self.rate)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[self.voiceId].id)

        # Set Assistant Settings
        self.matchingPercent = matchingPercent # Set minimum matching percentage to match intents
        self.maxIdle = maxIdle # Maximum Time for the user 
        self.idleTime = 0
        self.isIdle = False

        # Load Intents
        with open("Intents.json", 'r') as f:
            self.intents = json.load(f)
        
        # Start Tracking Idle Mode
        idle = threading.Thread(target=self.trackIdle)
        idle.start()

    def handleCommand(self, command):
        if command is None:
            print("hi")
            return
        responses = None
        matched = self.matchIntent(command)
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
                    self.broadcast(["hi", ["sds", "sdsd"], "s", ["2"]], sound=True, delay=0)

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

    def matchIntent(self, command):
        intents = []
        for item in self.intents:
            if item != "Unmatched":
                for response in self.intents[item]["intents"]:
                    intents.append(response)
        print(intents)
        highest = process.extractOne(command, intents)
        if highest[1] >= self.matchingPercent:
            return highest[0]
        else:
            return "Unmatched"

    def broadcast(self, text, sound=True, delay=0.7):
        if type(text) is str:
            print(output(text))
            if sound is True:
                if not text.startswith("https://") and not text.startswith("www"):
                    self.engine.say(text)
                    self.engine.runAndWait()
        elif type(text) is list:
            for t in text:
                time.sleep(delay)
                self.broadcast(t, sound=sound)
        else:
            exit("Unsupported datatype for self.broadcast()")

    def listen(self):
        command = input("Enter your command:\n")
        self.idleTime = 0
        return command

    async def trackIdle(self):
        while not self.idleTime < self.maxIdle:#keyboard.KEY_DOWN :#self.idleTime < self.maxIdle:
            time.sleep(1)
            self.idleTime += 1
        self.isIdle = True

    def get_holder_response(self, holder: str, placeholder: str, intent_options: list, response : str):
        holder = holder.lower()
        for i in intent_options:
            holder = holder.replace(i, "")
        return response.replace(f"{placeholder.upper()}", holder)


def main():
    assistant = Assistant(
        rate=180,
        voiceId=2,
        matchingPercent=90,
        maxIdle=180
    )
    while assistant.isIdle is False:
        try:
            command = assistant.listen()
            assistant.handleCommand(command)
        except Exception as error:
            assistant.broadcast(
                random.choice(assistant.intents["EXCEPTION"]["responses"]))
            assistant.broadcast(str(error))


if __name__ == "__main__":
    main()
