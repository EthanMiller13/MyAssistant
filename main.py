import pyttsx3
from fuzzywuzzy import process
import json
import random
import time
import Actions
import colorama as c


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
            self.intentsJson = json.load(f)
        
        self.commandIntents = [] # User Accssesible Commands
        self.ignoredClassifiers = ["UNMATCHED", "EXCEPTION", "IDLE"] # System intents
        for item in self.intentsJson:
            if item not in self.ignoredClassifiers:
                for intent in self.intentsJson[item]["intents"]:
                    self.commandIntents.append(intent)
        
        # Start Tracking Idle Mode
        #idle = threading.Thread(target=self.trackIdle)
        #idle.start()

    def matchIntent(self, command):
        highestMatch = process.extractOne(command, self.commandIntents)
        if highestMatch[1] >= self.matchingPercent:
            intent = highestMatch[0]
            return intent
        else:
            intent = "UNMATCHED"
            return intent

    def getIntentClassifier(self, intent: str):
        for classifier in self.intentsJson:
            if classifier not in self.ignoredClassifiers and intent in self.intentsJson[classifier]["intents"]:
                return classifier

    def broadcast(self, message, sound: bool=True, delay: float=0.7):
        if type(message) is str:
            print(output(message))
            if sound is True:
                if not message.startswith("https://") and not message.startswith("www"):
                    self.engine.say(message)
                    self.engine.runAndWait()
        elif type(message) is list:
            for item in message:
                time.sleep(delay)
                self.broadcast(item, sound=sound)
        else:
            exit(f"Unsupported datatype for self.broadcast() ({type(message)})")

    def listen(self):
        command = input("Enter your command:\n")
        self.idleTime = 0
        return command

    def trackIdle(self):
        while not self.idleTime < self.maxIdle:#keyboard.KEY_DOWN :#self.idleTime < self.maxIdle:
            time.sleep(1)
            self.idleTime += 1
        self.isIdle = True

    def handleCommand(self, command):
        if command == '':
            return
        matchedIntent = self.matchIntent(command)
        classifier = self.getIntentClassifier(matchedIntent)
        if classifier is None:
            classifier = "UNMATCHED"

        allResponses = self.intentsJson[classifier]["responses"]
        response = random.choice(allResponses)
        actions = self.intentsJson[classifier]["actions"]

        for action in actions:
            exec(f"result = {action}")
            


def main():
    assistant = Assistant(
        rate=180,
        voiceId=2,
        matchingPercent=90,
        maxIdle=60
    )
    while assistant.isIdle is False:
        try:
            command = assistant.listen()
            assistant.handleCommand(command)
        except Exception as error:
            assistant.broadcast(
                random.choice(assistant.intentsJson["EXCEPTION"]["responses"]))
            assistant.broadcast(str(error))
            raise error


if __name__ == "__main__":
    main()
