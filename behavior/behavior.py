import numpy
import scipy.misc
import const
import PIL  # import used for scipy.misc.imsave

from robot.body_movement_wrapper import BodyMovementWrapper
from robot.position_movement_wrapper import PositionMovementWrapper
from robot.sensing_wrapper import SensingWrapper
from robot.speech_wrapper import SpeechWrapper


class Behavior(object):

    def __init__(self):
        self.__robot = const.robot
        self.__initializeWrappers()

    def start_behavior(self):
        self.__create_map(radius=0.5)

    def __initializeWrappers(self):
        self.body_movement_wrapper = BodyMovementWrapper(self.__robot)
        self.position_movement_wrapper = PositionMovementWrapper(self.__robot)
        self.sensing_wrapper = SensingWrapper(self.__robot)
        self.speech_wrapper = SpeechWrapper(self.__robot)

    def __create_map(self, radius):
        # Wake up robot
        self.__robot.ALMotion.wakeUp()

        # Explore the environement, in a radius of 2 m.
        error_code = self.sensing_wrapper.explore(radius)
        if error_code != 0:
            print "Exploration failed."
            return
        # Saves the exploration on disk
        path = self.sensing_wrapper.save_exploration_to_robot()
        print "Exploration saved at path: \"" + path + "\""
        # Start localization to navigate in map
        self.sensing_wrapper.start_localization()
        # Come back to initial position
        self.position_movement_wrapper.navigate_to_coordinate_on_map([0., 0., 0.])
        # Stop localization
        self.sensing_wrapper.stop_localization()
        # Retrieve and display the map built by the robot
        result_map = self.sensing_wrapper.get_metrical_map()
        map_width = result_map[1]
        map_height = result_map[2]
        img = numpy.array(result_map[4]).reshape(map_width, map_height)
        img = (100 - img) * 2.55  # from 0..100 to 255..0
        img = numpy.array(img, numpy.uint8)

        # save image to project root
        scipy.misc.imsave('map.jpg', img)
