class PositionMovementWrapper:

    def __init__(self, robot):
        self.__robot = robot

    def enableCollisionProtection(self, enabled):
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled("All", enabled)
        self.__robot.ALMotion.setCollisionProtectionEnabled("Arms", enabled)
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled("Arms", enabled)
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled("LArm", enabled)
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled("RArm", enabled)

        print('enabled collision protection: {}'.format(enabled))
