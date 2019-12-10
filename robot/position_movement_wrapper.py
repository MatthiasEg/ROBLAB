import math

import const


class PositionMovementWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.enable_collision_protection(True)
        self.__robot.ALMotion.setSmartStiffnessEnabled(True)
        self.collision_avoided = False

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

    def learn_home(self):
        self.__robot.ALLocalization.learnHome()

    def go_to_home(self):
        self.__robot.ALLocalization.goToHome()

    def is_home(self):
        return self.__robot.ALLocalization.isInCurrentHome()

    def get_positon(self):
        return self.__robot.ALLocalization.getRobotPosition()

    def go_to_position(self, position):
        self.__robot.ALLocalization.goToPosition(position)

    def navigate_to_coordinate_on_map(self, coordinate_vector):
        self.__robot.ALNavigation.navigateToInMap(coordinate_vector)

    def navigate_back_to_reception(self):
        # file_transfer = FileTransfer(const.robot)
        # file_transfer.push("../maps/2014-04-04T035759.612Z.explo", "/home/nao/2014-04-04T035759.612Z.explo")
        # self.__robot.ALNavigation.stopLocalization()
        # self.__robot.ALNavigation.stopLocalization()
        self.__robot.ALNavigation.loadExploration("/home/nao/maps_2014-04-04T035759.612Z.explo")
        self.__robot.ALNavigation.startLocalization()
        self.__robot.ALNavigation.relocalizeInMap([0., 0., 0.])
        # self.move_to(-10, 0, 0)
        self.__robot.ALNavigation.navigateToInMap([0., 0., 0.])
        self.__robot.ALNavigation.stopLocalization()
