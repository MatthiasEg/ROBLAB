from tools.Robot import Robot
from tools.PepperConfiguration import PepperConfiguration


class SuperRobot:

    def __init__(self, name):
        config = PepperConfiguration(name)
        self.__robot = Robot(config)

    def say(self, text):
        self.__robot.ALAnimatedSpeech.say(text)
