class SpeechWrapper:

    def __init__(self, robot):
        self.__robot = robot

    def say(self, text):
        self.__robot.ALAnimatedSpeech.say(text)
