import const


class SensingWrapper:

    def __init__(self, robot):
        self.__robot = const.robot

    def explore(self, radius):
        return self.__robot.ALNavigation.explore(radius)

    def save_exploration_to_robot(self):
        return self.__robot.ALNavigation.saveExploration()

    def start_localization(self):
        return self.__robot.ALNavigation.startLocalization()

    def stop_localization(self):
        return self.__robot.ALNavigation.stopLocalization()

    def get_metrical_map(self):
        return self.__robot.ALNavigation.getMetricalMap()
