import const
import random


class SpeechWrapper:

    def __init__(self):
        self.__robot = const.robot

    def animated_say(self, text):
        self.__robot.ALAnimatedSpeech.animated_say(text)

    def say(self, text):
        self.__robot.ALTextToSpeech.say(text)

    def say_random(self, list):
        self.say(random.choice(list))

    def start_to_listen(self, vocabulary, language, callback):
        # self.__robot.ALMemory.subscribeToEvent("SpeechRecognition", module, callback)
        self.subscriber = self.__robot.ALMemory.subscriber("WordRecognized")
        self.subscriber.signal.connect(callback)
        # self.subscriber.signal.connect(callback)
        # SpeechRecognition = ALProxy("SpeechRecognition")
        self.__robot.ALSpeechRecognition.pause(True)
        self.__robot.ALSpeechRecognition.setLanguage(language)
        self.__robot.ALSpeechRecognition.setVocabulary(vocabulary, True)
        self.__robot.ALSpeechRecognition.pause(False)
        self.__robot.ALSpeechRecognition.subscribe("SpeechDetection", 200, 0.5)
        # SpeechRecognition.calibrate()
        # SpeechRecognition.enableAutoDetection()

    def stop_listening(self):
        self.__robot.ALSpeechRecognition.unsubscribe("SpeechDetection")
