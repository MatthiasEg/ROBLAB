import time

import numpy
import scipy.misc
import const
# import PIL  # import used for scipy.misc.imsave

from robot.body_movement_wrapper import BodyMovementWrapper
from robot.position_movement_wrapper import PositionMovementWrapper
from robot.sensing_wrapper import SensingWrapper
from robot.speech_wrapper import SpeechWrapper
from robot.body_movement_wrapper import Actuators


class Behavior(object):

    def __init__(self):
        self.__robot = const.robot
        self.__initialize_wrappers()
        self.got_face = False

    def start_behavior(self):
        # self.__create_map(radius=0.5)
        self.speech_wrapper.say("hello")
        # self.setup_customer_reception()
        # self.__navigate()
        # self.__ask_to_follow()
        

    def setup_customer_reception(self):
        if not self.sensing_wrapper.is_face_detection_enabled():
            raise Exception('No Face detection possible with this system!')

        self.sensing_wrapper.set_maximum_detection_range_in_meters(3)
        self.sensing_wrapper.enable_face_recognition()
        self.sensing_wrapper.enable_face_tracking()

        subscriber = self.sensing_wrapper.get_memory_subscriber("FaceDetected")
        subscriber.signal.connect(self.on_human_tracked)

        while True:
            time.sleep(1)
        self.__navigate()

    def __initialize_wrappers(self):
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

        scipy.misc.imsave('mapMitRadius{}.jpg'.format(radius), img)

    def on_human_tracked(self, value):

        """
               Callback for event FaceDetected.
               """
        if value == []:  # empty value when the face disappears
            self.got_face = False
        elif not self.got_face:  # only speak the first time a face appears
            self.got_face = True
        print "I saw a face!"
        self.speech_wrapper.say("I see you!")
        # First Field = TimeStamp.
        timeStamp = value[0]
        print "TimeStamp is: " + str(timeStamp)

        # Second Field = array of face_Info's.
        faceInfoArray = value[1]
        for j in range(len(faceInfoArray) - 1):
            faceInfo = faceInfoArray[j]

            # First Field = Shape info.
            faceShapeInfo = faceInfo[0]

            # Second Field = Extra info (empty for now).
            faceExtraInfo = faceInfo[1]

            print "Face Infos :  alpha %.3f - beta %.3f" % (faceShapeInfo[1], faceShapeInfo[2])
            print "Face Infos :  width %.3f - height %.3f" % (faceShapeInfo[3], faceShapeInfo[4])
            print "Face Extra Infos :" + str(faceExtraInfo)

    def __navigate(self):
        # Load a previously saved exploration
        self.sensing_wrapper.load_exploration_from_robot('/home/nao/group02HS19/map-4m.explo')
        # self.position_movement_wrapper.navigate_to_coordinate_on_map()

        # Relocalize the robot and start the localization process.
        pos = [0., 0.]
        self.position_movement_wrapper.relocalize_in_map(pos)
        self.sensing_wrapper.start_localization()

        # Navigate to another place in the map
        self.position_movement_wrapper.navigate_to_coordinate_on_map([1., 0., 0.])

        # Check where the robot arrived
        print "I reached: " + str(self.sensing_wrapper.get_robot_position_in_map()[0])

        # Stop localization
        self.sensing_wrapper.stop_localization()

    def __ask_to_follow(self):
        print('hi')
        self.body_movement_wrapper.moveArmsUp(Actuators.RArm, 120)
        time.sleep(1)
        self.body_movement_wrapper.moveArmsDown(Actuators.RArm, 160)

    def patrick(self):
        self.body_movement_wrapper.enableMoveArms(True)
        self.speech_wrapper.say('Learning home')
        self.position_movement_wrapper.learn_home()
        self.speech_wrapper.say('wiggle wiggle')
        self.position_movement_wrapper.move(1,2,0)
        self.speech_wrapper.say('wiggle wiggle')
        self.position_movement_wrapper.move(2,1,0)
        self.speech_wrapper.say("I'm going home bitch")
        self.position_movement_wrapper.go_to_home()