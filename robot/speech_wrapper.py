import const


class SpeechWrapper:

    def __init__(self):
        self.__robot = const.robot

    def animated_say(self, text):
        self.__robot.ALAnimatedSpeech.animated_say(text)

    def say(self, text):
        self.__robot.ALTextToSpeech.say(text)
