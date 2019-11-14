import math
import time
import motion
import const

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

    def __init__(self):
        self.__robot = const.robot
        self.headJointNames = ["HeadYaw", "HeadPitch"]
        # Using 10% of maximum joint speed
        self.fractionMaxSpeed = 0.1
        self.motion_service = self.__robot.session.service("ALMotion")
        self.armJointNamesL = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw"]
        self.armJointNamesR = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]

    def enableMoveArms(self, enabled):
        self.motion_service.setMoveArmsEnabled(enabled, enabled)
    
    def moveArmsThread(self):
        self.setArmsUp(Actuators.BOTH, 90)
        self.setElbowLeft(Actuators.RArm, 45)
        self.setElbowRight(Actuators.LArm, 45)
        time.sleep(0.1)
        
        self.motion_service.angleInterpolation('RElbowRoll',[math.radians(-1)],[0.2],False)
        self.motion_service.angleInterpolation('LElbowRoll',[math.radians(-1)],[0.2],False)
        time.sleep(0.1)
        self.motion_service.angleInterpolation('RElbowRoll',[math.radians(1)],[0.2],False)
        self.motion_service.angleInterpolation('LElbowRoll',[math.radians(1)],[0.2],False)

    def moveArmsBackThread(self):
         self.setArmsUp(Actuators.BOTH, 70)
         time.sleep(0.1)

    def dropArmsThread(self):
        self.moveArmsDown(Actuators.BOTH, 40)
        time.sleep(2)
        self.moveElbowRight(Actuators.RArm, 50)
        self.moveElbowLeft(Actuators.LArm, 50)

    def moveArms(self, actuator, armArr):
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

    def setArmsUp(self, actuator, deg):
        self.__setArms_intern(actuator, -deg, 0)

    def moveArmsUp(self, actuator, deg):
        self.__moveArms_intern(actuator, -deg, 0)

    def moveArmsDown(self, actuator, deg):
        self.__moveArms_intern(actuator, deg, 0)

    def moveShoulderRight(self, actuator, deg):
        self.__moveArms_intern(actuator, -deg, 1)

    def moveShoulderLeft(self, actuator, deg):
        self.__moveArms_intern(actuator, deg, 1)

    def setElbowLeft(self, actuator, deg):
        self.__setArms_intern(actuator, deg, 3)

    def setElbowRight(self, actuator, deg):
        self.__setArms_intern(actuator, -deg, 3)

    def moveElbowLeft(self, actuator, deg):
        self.__moveArms_intern(actuator, deg, 3)

    def moveElbowRight(self, actuator, deg):
        self.__moveArms_intern(actuator, -deg, 3)

    def rotateElbowRight(self, actuator, deg):
        self.__moveArms_intern(actuator, deg, 2)

    def rotateElbowLeft(self, actuator, deg):
        self.__moveArms_intern(actuator, -deg, 2)

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
