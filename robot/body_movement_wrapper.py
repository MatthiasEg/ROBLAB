import math
import time

import motion
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
        self.hipJointNames = ["HipRoll", "HipPitch"]
        # Using 10% of maximum joint speed
        self.fractionMaxSpeed = 0.1
        self.motion_service = self.__robot.session.service("ALMotion")
        self.armJointNamesL = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw"]
        self.armJointNamesR = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]

    def enable_move_arms(self, enabled):
        self.motion_service.setMoveArmsEnabled(enabled, enabled)

    def move_arms_thread(self):
        self.set_arms_up(Actuators.BOTH, 90)
        self.set_elbow_left(Actuators.RArm, 45)
        self.set_elbow_right(Actuators.LArm, 45)
        time.sleep(0.1)

        self.motion_service.angleInterpolation('RElbowRoll',[math.radians(-1)],[0.2],False)
        self.motion_service.angleInterpolation('LElbowRoll',[math.radians(-1)],[0.2],False)
        time.sleep(0.1)
        self.motion_service.angleInterpolation('RElbowRoll',[math.radians(1)],[0.2],False)
        self.motion_service.angleInterpolation('LElbowRoll',[math.radians(1)],[0.2],False)

    def move_arms_back_thread(self):
         self.set_arms_up(Actuators.BOTH, 70)
         time.sleep(0.1)

    def drop_arms_thread(self):
        self.move_arms_down(Actuators.BOTH, 40)
        time.sleep(2)
        self.move_elbow_right(Actuators.RArm, 50)
        self.move_elbow_left(Actuators.LArm, 50)

    def move_arms(self, actuator, armArr):
        # Arm Right (for left arm mirror the movement)
        # [   arm             { - : up, + : down } | Range: -119.5 to 119.5
        #     shoulder        { - : right side horizontal movement, + : left side horizontal movement } | Range: -89.5 to -0.5
        #     elbow rotation  { + : clockwise, - : anti-clockwise } | Range: -119.5 to 119.5
        #     elbow movement  { + : right to left, - : left to right } | Range: 0.5 to 89.5
        #     wrist rotation  { + : clockwise, - : anti-clockwise } | -104.5 to 104.5
        # ]

        armArr = [ x * motion.TO_RAD for x in armArr] # convert the degrees to radiants

        if actuator == Actuators.LArm:
            self.motion_service.angleInterpolationWithSpeed(self.armJointNamesL, armArr, self.fractionMaxSpeed)
        elif actuator == Actuators.RArm:
            self.motion_service.angleInterpolationWithSpeed(self.armJointNamesR, armArr, self.fractionMaxSpeed)
        elif actuator == Actuators.BOTH:
            self.motion_service.angleInterpolationWithSpeed(self.armJointNamesL, armArr, self.fractionMaxSpeed)
            self.motion_service.angleInterpolationWithSpeed(self.armJointNamesR, armArr, self.fractionMaxSpeed)

    def __moveArms_intern(self, actuator, deg, index):
        if actuator == Actuators.LArm:
            self.motion_service.changeAngles(self.armJointNamesL[index], math.radians(deg), self.fractionMaxSpeed)
        elif actuator == Actuators.RArm:
            self.motion_service.changeAngles(self.armJointNamesR[index], math.radians(deg), self.fractionMaxSpeed)
        elif actuator == Actuators.BOTH:
            # Move left hand without compromising last position
            self.motion_service.changeAngles(self.armJointNamesL[index], math.radians(deg), self.fractionMaxSpeed)
            # Move right hand without compromising last position
            self.motion_service.changeAngles(self.armJointNamesR[index], math.radians(deg), self.fractionMaxSpeed)

    def __setArms_intern(self, actuator, deg, index):
            if actuator == Actuators.LArm:
                self.motion_service.setAngles(self.armJointNamesL[index], math.radians(deg), self.fractionMaxSpeed)
            elif actuator == Actuators.RArm:
                self.motion_service.setAngles(self.armJointNamesR[index], math.radians(deg), self.fractionMaxSpeed)
            elif actuator == Actuators.BOTH:
                # Move left hand without compromising last position
                self.motion_service.setAngles(self.armJointNamesL[index], math.radians(deg), self.fractionMaxSpeed)
                # Move right hand without compromising last position
                self.motion_service.setAngles(self.armJointNamesR[index], math.radians(deg), self.fractionMaxSpeed)

    def set_arms_up(self, actuator, deg):
        self.__setArms_intern(actuator, -deg, 0)

    def move_arms_up(self, actuator, deg):
        self.__moveArms_intern(actuator, -deg, 0)

    def move_arms_down(self, actuator, deg):
        self.__moveArms_intern(actuator, deg, 0)

    def move_shoulder_right(self, actuator, deg):
        self.__moveArms_intern(actuator, -deg, 1)

    def move_shoulder_left(self, actuator, deg):
        self.__moveArms_intern(actuator, deg, 1)

    def set_elbow_left(self, actuator, deg):
        self.__setArms_intern(actuator, deg, 3)

    def set_elbow_right(self, actuator, deg):
        self.__setArms_intern(actuator, -deg, 3)

    def move_elbow_left(self, actuator, deg):
        self.__moveArms_intern(actuator, deg, 3)

    def move_elbow_right(self, actuator, deg):
        self.__moveArms_intern(actuator, -deg, 3)

    def rotate_elbow_right(self, actuator, deg):
        self.__moveArms_intern(actuator, deg, 2)

    def rotate_elbow_left(self, actuator, deg):
        self.__moveArms_intern(actuator, -deg, 2)
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

    def initial_position(self):
        self.__robot.ALRobotPosture.goToPosture("StandInit", self.fractionMaxSpeed)
        self.set_head_down(0)

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

    def set_hip_roll(self, deg):
        self.__set_hip_intern(deg, 0)

    def set_hip_pitch(self, deg):
        self.__set_hip_intern(deg, 1)

    @staticmethod
    def __calculate_degree_from_percentage(max_degree, percentage):
        return max_degree * (float(percentage) / 100.0)

    def __set_head_intern(self, deg, index):
        self.__robot.ALMotion.setAngles(self.headJointNames[index], math.radians(deg), self.fractionMaxSpeed)

    def get_head_angle_horizontal(self):
        return self.__robot.ALMotion.getAngles(self.headJointNames[0], False)

    def __set_hip_intern(self, deg, index):
        self.__robot.ALMotion.setAngles(self.hipJointNames[index], math.radians(deg), self.fractionMaxSpeed)
