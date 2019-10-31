class PositionMovementWrapper:

    def __init__(self, robot):
        self.__robot = robot

    def enable_collision_protection(self, enabled):
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled(
            "All", enabled)
        self.__robot.ALMotion.setCollisionProtectionEnabled("Arms", enabled)
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled(
            "Arms", enabled)
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled(
            "LArm", enabled)
        self.__robot.ALMotion.setExternalCollisionProtectionEnabled(
            "RArm", enabled)

        print('enabled collision protection: {}'.format(enabled))

    def enableAutonomousLife(self, enabled):
        # to disable whole autonomous life
        # connect to robot via ssh
        # nao stop
        # naoqi-bin --disable-life
        self.__robot.ALMotion.setAutonomousAbilityEnabled("BackgroundMovement", enabled)
        self.__robot.ALMotion.setAutonomousAbilityEnabled("BasicAwareness", enabled)
        self.__robot.ALMotion.setAutonomousAbilityEnabled("ListeningMovement", enabled)
        self.__robot.ALMotion.setAutonomousAbilityEnabled("SpeakingMovement", enabled)

        self.__robot.ALMotion.setIdlePostureEnabled('Body', enabled)
        self.__robot.ALMotion.setBreathEnabled('Body', enabled)

        print('enabled autonomous life: {}'.format(enabled))

    def move(self, x, y, theta):
        motion_service = self.__robot.session.service("ALMotion")
        # self.__robot.ALLocalization.move(x, y, theta)
        motion_service.moveTo(x, y, theta, _async=False)

    def learnHome(self):
        self.__robot.ALLocalization.learnHome()

    def goToHome(self):
        self.__robot.ALLocalization.goToHome()

    def getPositon(self):
        self.__robot.ALLocalization.getRobotPosition()

    def goToPosition(self, position):
        self.__robot.ALLocalization.goToPosition(position)
