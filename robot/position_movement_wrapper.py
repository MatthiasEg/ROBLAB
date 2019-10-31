import const


class PositionMovementWrapper:

    def __init__(self):
        self.__robot = const.robot

    def enable_collision_protection(self, enabled):
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled("All", enabled)
        self.__robot.ALMotion.setCollisionProtectionEnabled("Arms", enabled)
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled("Arms", enabled)
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled("LArm", enabled)
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled("RArm", enabled)

        print('enabled collision protection: {}'.format(enabled))

    def navigate_to_coordinate_on_map(self, coordinate_vector):
        self.__robot.ALNavigation.navigateToInMap(coordinate_vector)
