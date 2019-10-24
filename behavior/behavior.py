import numpy
import scipy.misc
import const
import PIL

from robot.body_movement_wrapper import BodyMovementWrapper
from robot.position_movement_wrapper import PositionMovementWrapper
from robot.sensing_wrapper import SensingWrapper
from robot.speech_wrapper import SpeechWrapper


class Behavior:

    def __init__(self):
        self.__robot = const.robot

    def start_behavior(self):
        body_movement_wrapper = BodyMovementWrapper(self.__robot)
        position_movement_wrapper = PositionMovementWrapper(self.__robot)
        sensing_wrapper = SensingWrapper(self.__robot)
        speech_wrapper = SpeechWrapper(self.__robot)
        # speech_wrapper.say("Hello, its working now!")

        self.__create_map(radius=0.5)

    def __create_map(self, radius):
        # Wake up robot
        self.__robot.ALMotion.wakeUp()

        # Explore the environement, in a radius of 2 m.
        error_code = self.__robot.ALNavigation.explore(radius)
        if error_code != 0:
            print "Exploration failed."
            return
        # Saves the exploration on disk
        path = self.__robot.ALNavigation.saveExploration()
        print "Exploration saved at path: \"" + path + "\""
        # Start localization to navigate in map
        self.__robot.ALNavigation.startLocalization()
        # Come back to initial position
        self.__robot.ALNavigation.navigateToInMap([0., 0., 0.])
        # Stop localization
        self.__robot.ALNavigation.stopLocalization()
        # Retrieve and display the map built by the robot
        result_map = self.__robot.ALNavigation.getMetricalMap()
        map_width = result_map[1]
        map_height = result_map[2]
        img = numpy.array(result_map[4]).reshape(map_width, map_height)
        img = (100 - img) * 2.55  # from 0..100 to 255..0
        img = numpy.array(img, numpy.uint8)

        # save image to project root
        scipy.misc.imsave('map.jpg', img)
