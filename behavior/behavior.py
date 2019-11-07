import numpy
import scipy.misc
import const
# import PIL  # import used for scipy.misc.imsave

from robot.body_movement_wrapper import BodyMovementWrapper
from robot.position_movement_wrapper import PositionMovementWrapper
from robot.sensing_wrapper import SensingWrapper
from robot.speech_wrapper import SpeechWrapper


class Behavior(object):

    def __init__(self):
        self.__robot = const.robot
        self.__initializeWrappers()

    def start_behavior(self):
        # self.__create_map(radius=0.5)
        self.__navigate()

    def __initializeWrappers(self):
        self.body_movement_wrapper = BodyMovementWrapper()
        self.position_movement_wrapper = PositionMovementWrapper()
        self.sensing_wrapper = SensingWrapper()
        self.speech_wrapper = SpeechWrapper()

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
        # scipy.misc.imsave('mapMitRadius{}.jpg'.format(radius), img)

    def __navigate(self):
        # Load a previously saved exploration
        self.sensing_wrapper.load_exploration_from_robot('/home/nao/group02HS19/map-4m.explo')
        # self.position_movement_wrapper.navigate_to_coordinate_on_map()

        # Relocalize the robot and start the localization process.
        pos = [0.01, 0.01]
        self.position_movement_wrapper.relocalize_in_map(pos)
        self.sensing_wrapper.start_localization()

        # Navigate to another place in the map
        self.position_movement_wrapper.navigate_to_coordinate_on_map([1., 0., 0.])

        # Check where the robot arrived
        print "I reached: " + str(self.sensing_wrapper.get_robot_position_in_map()[0])

        # Stop localization
        self.sensing_wrapper.stop_localization()