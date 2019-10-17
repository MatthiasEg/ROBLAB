import math
from tools.Robot import Robot

from enum import Enum

from tools import Robot


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

    def open_left_hand(self):
        self.__robot.ALMotion.openHand("LHand")

    def close_left_hand(self):
        self.__robot.ALMotion.closeHand("LHand")

    def open_right_hand(self):
        self.__robot.ALMotion.openHand("RHand")

    def close_right_hand(self):
        self.__robot.ALMotion.closeHand("RHand")

    def move_head_up(self, deg):
        self.move_head_intern(-deg, 1)

    def move_head_down(self, deg):
        self.move_head_intern(deg, 1)

    def move_head_rght(self, deg):
        self.move_head_intern(deg, 0)

    def move_head_left(self, deg):
        self.move_head_intern(-deg, 0)

    def move_head_intern(self, deg, index):
        self.__robot.ALMotion.changeAngles(self.headJointNames[index], math.radians(deg), self.fractionMaxSpeed)
