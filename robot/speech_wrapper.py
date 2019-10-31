import const


class SpeechWrapper:

    def __init__(self):
        self.__robot = const.robot

    def say(self, text):
        self.__robot.ALAnimatedSpeech.say(text)
