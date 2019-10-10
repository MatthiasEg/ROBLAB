import math

from enum import Enum


class Actuators(Enum):
    LArm = 1
    RArm = 2
    BOTH = 3
    HIPS = 4
    ALL = 5


class BodyMovementWrapper:

    def __init__(self, robot):
        self.__robot = robot
        self.headJointNames = ["HeadYaw", "HeadPitch"]
        # Using 10% of maximum joint speed
        self.fractionMaxSpeed = 0.1

    def openLeftHand(self):
        self.__robot.ALMotion.openHand("LHand")

    def closeLeftHand(self):
        self.__robot.ALMotion.closeHand("LHand")

    def openRightHand(self):
        self.__robot.ALMotion.openHand("RHand")

    def closeRightHand(self):
        self.__robot.ALMotion.closeHand("RHand")

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
