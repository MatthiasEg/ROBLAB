import math

from enum import Enum

import const


class Actuators(Enum):
    LArm = 1
    RArm = 2
    BOTH = 3
    HIPS = 4
    ALL = 5


class BodyMovementWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.headJointNames = ["HeadYaw", "HeadPitch"]
        # Using 10% of maximum joint speed
        self.fractionMaxSpeed = 0.1
        self.enable_autonomous_life(False)
        self.enable_move_arms(False)

    def enable_autonomous_life(self, enabled):
        # to disable whole autonomous life
        self.__robot.session.service("ALAutonomousLife").setAutonomousAbilityEnabled("BackgroundMovement", enabled)
        self.__robot.session.service("ALAutonomousLife").setAutonomousAbilityEnabled("BasicAwareness", enabled)
        self.__robot.session.service("ALAutonomousLife").setAutonomousAbilityEnabled("ListeningMovement", enabled)
        self.__robot.session.service("ALAutonomousLife").setAutonomousAbilityEnabled("SpeakingMovement", enabled)

        self.__robot.ALMotion.setIdlePostureEnabled('Body', enabled)
        self.__robot.ALMotion.setBreathEnabled('Body', enabled)

        print('enabled autonomous life: {}'.format(enabled))

    def enable_move_arms(self, enabled):
        self.__robot.ALMotion.setMoveArmsEnabled(enabled, enabled)

    def initial_position(self):
        self.__robot.ALRobotPosture.goToPosture("StandInit", self.fractionMaxSpeed)
        self.set_head_down(30)

    def initial_position_stand(self):
        self.__robot.ALRobotPosture.goToPosture("Stand", self.fractionMaxSpeed)

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

    def move_head_right(self, deg):
        self.move_head_intern(-deg, 0)

    def move_head_left(self, deg):
        self.move_head_intern(deg, 0)

    def move_head_intern(self, deg, index):
        self.__robot.ALMotion.changeAngles(self.headJointNames[index], math.radians(deg), self.fractionMaxSpeed)

    def set_head_up(self, percentage):
        """Sets the fixed head angle upwards.

        :param float percentage: Position in percentage relative to max angle.
        """
        deg = self.__calculate_degree_from_percentage(-40.5, percentage)
        self.__set_head_intern(deg, 1)

    def set_head_down(self, percentage):
        """Sets the fixed head angle downwards.

        :param float percentage: Position in percentage relative to max angle.
        """
        deg = self.__calculate_degree_from_percentage(36.5, percentage)
        self.__set_head_intern(deg, 1)

    def set_head_right(self, percentage):
        """Sets the fixed head angle downwards.

        :param float percentage: Position in percentage relative to max angle.
        """
        deg = self.__calculate_degree_from_percentage(-119.5, percentage)
        self.__set_head_intern(deg, 0)

    def set_head_left(self, percentage):
        """Sets the fixed head angle downwards.

        :param float percentage: Position in percentage relative to max angle.
        """
        deg = self.__calculate_degree_from_percentage(119.5, percentage)
        self.__set_head_intern(deg, 0)

    @staticmethod
    def __calculate_degree_from_percentage(max_degree, percentage):
        return max_degree * (float(percentage) / 100.0)

    def __set_head_intern(self, deg, index):
        self.__robot.ALMotion.setAngles(self.headJointNames[index], math.radians(deg), self.fractionMaxSpeed)
