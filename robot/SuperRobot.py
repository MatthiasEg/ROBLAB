import math
import time

from tools.Robot import Robot
from enum import Enum

from tools.PepperConfiguration import PepperConfiguration


class Actuators(Enum):
    LArm = 1
    RArm = 2
    BOTH = 3
    HIPS = 4
    ALL = 5


class Quantity(Enum):
    QUARTER = 1
    HALF = 2
    FULL = 3


class SuperRobot:

    def __init__(self, name):
        config = PepperConfiguration(name)
        self.__robot = Robot(config)
        self.headJointNames = ["HeadYaw", "HeadPitch"]
        # Using 10% of maximum joint speed<<r
        self.fractionMaxSpeed = 0.1

    def say(self, text):
        self.__robot.ALAnimatedSpeech.say(text)

    def openLeftHand(self):
        self.__robot.ALMotion.openHand("LHand")

    def closeLeftHand(self):
        self.__robot.ALMotion.openHand("LHand")

    def openRightHand(self):
        self.__robot.ALMotion.openHand("RHand")

    def closeRightHand(self):
        self.__robot.ALMotion.openHand("RHand")

    def moveHeadUp(self, deg):
        self.__moveHeadIntern(-deg, 1)

    def moveHeadDown(self, deg):
        self.__moveHeadIntern(deg, 1)

    def moveHeadRight(self, deg):
        self.__moveHeadIntern(deg, 0)

    def moveHeadLeft(self, deg):
        self.__moveHeadIntern(-deg, 0)

    def __moveHeadIntern(self, deg, index):
        self.__robot.ALMotion.changeAngles(self.headJointNames[index], math.radians(deg), self.fractionMaxSpeed)
