import math

import const


class BodyMovementWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.headJointNames = ["HeadYaw", "HeadPitch"]
        self.hipJointNames = ["HipRoll", "HipPitch"]
        self.fractionMaxSpeed = 0.1

    def enable_autonomous_life(self, enabled):
        # to disable whole autonomous life
        self.__robot.session.service("ALAutonomousLife").setAutonomousAbilityEnabled("BackgroundMovement", enabled)
        self.__robot.session.service("ALAutonomousLife").setAutonomousAbilityEnabled("BasicAwareness", enabled)
        self.__robot.session.service("ALAutonomousLife").setAutonomousAbilityEnabled("ListeningMovement", enabled)
        self.__robot.session.service("ALAutonomousLife").setAutonomousAbilityEnabled("SpeakingMovement", enabled)

        self.__robot.ALMotion.setIdlePostureEnabled('Body', enabled)
        self.__robot.ALMotion.setBreathEnabled('Body', enabled)

        print('enabled autonomous life: {}'.format(enabled))

    def initial_position(self):
        self.__robot.ALRobotPosture.goToPosture("StandInit", self.fractionMaxSpeed)
        self.set_head_down(20)

    def move_head_up(self, deg):
        self.__move_head_intern(-deg, 1)

    def move_head_down(self, deg):
        self.__move_head_intern(deg, 1)

    def move_head_right(self, deg):
        self.__move_head_intern(-deg, 0)

    def move_head_left(self, deg):
        self.__move_head_intern(deg, 0)

    def __move_head_intern(self, deg, index):
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

    def set_hip_roll(self, deg):
        self.__set_hip_intern(deg, 0)

    def set_hip_pitch(self, deg):
        self.__set_hip_intern(deg, 1)

    def __set_hip_intern(self, deg, index):
        self.__robot.ALMotion.setAngles(self.hipJointNames[index], math.radians(deg), self.fractionMaxSpeed)
