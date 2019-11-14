import math

import const


class PositionMovementWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.enable_collision_protection(True)

    def enable_collision_protection(self, enabled):
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled("All", enabled)
        self.__robot.ALMotion.setCollisionProtectionEnabled("Arms", enabled)
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled("Arms", enabled)
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled("LArm", enabled)
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled("RArm", enabled)

        print('enabled collision protection: {}'.format(enabled))

    def move_to(self, x, y, theta):
        self.__robot.ALMotion.moveTo(x, y, theta * math.pi / 180)

    def move(self, vx, vy, omega):
        # moves with velocity vx forward, vy to the left and omega anticlockwise
        self.__robot.ALMotion.move(vx, vy, omega * math.pi / 180)

    def stop_movement(self):
        self.__robot.ALMotion.stopMove()

    def learnHome(self):
        self.__robot.ALLocalization.learnHome()

    def goToHome(self):
        self.__robot.ALLocalization.goToHome()

    def getPositon(self):
        self.__robot.ALLocalization.getRobotPosition()

    def goToPosition(self, position):
        self.__robot.ALLocalization.goToPosition(position)
        
    def navigate_to_coordinate_on_map(self, coordinate_vector):
        self.__robot.ALNavigation.navigateToInMap(coordinate_vector)
