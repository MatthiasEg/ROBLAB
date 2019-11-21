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
        self.__got_face = False
        self.__first_person_detected = False
        self.__first_to_enter_callback = True
        self.__first_to_enter_callback_two = True

    def start_behavior(self):
        # self.body_movement_wrapper.move_head_up(10)
        self.speech_wrapper.say("hello")
        self.setup_customer_reception()
        # self.__navigate()
        # self.__ask_to_follow()
        # self.__recognize_persons()

    def setup_customer_reception(self):
        if not self.sensing_wrapper.is_face_detection_enabled():
            raise Exception('No Face detection possible with this system!')

        self.sensing_wrapper.reset_population()

        self.sensing_wrapper.set_maximum_detection_range_in_meters(3)
        self.sensing_wrapper.enable_face_recognition()
        self.sensing_wrapper.enable_face_tracking()
        # self.sensing_wrapper.enable_fast_mode()

        face_detected_subscriber = self.sensing_wrapper.get_memory_subscriber("FaceDetected")
        face_detected_subscriber.signal.connect(self.__on_human_tracked)
        self.sensing_wrapper.subscribe("huso")

        while not self.__first_person_detected:
            time.sleep(1)

        visible_people_subscriber = self.sensing_wrapper.get_memory_subscriber("PeoplePerception/VisiblePeopleList")
        visible_people_subscriber.signal.connect(self.__on_people_visible)
        self.sensing_wrapper.subscribe("VisiblePeopleList")

        while True:
            time.sleep(1)

    def __on_human_tracked(self, value):
        if value == []:  # empty value when the face disappears
            self.__got_face = False
        elif not self.__got_face:
            self.__got_face = True
            if self.__first_to_enter_callback:
                self.__first_to_enter_callback = False
                self.sensing_wrapper.unsubscribe("huso")
                self.speech_wrapper.say("Hello welcome to the restaurant dinner for one!")
                self.speech_wrapper.say("I would like to estimate the amount of people of your group.")
                self.speech_wrapper.say("Please come and stay in front of me.")
                self.__first_person_detected = True

    def __on_people_visible(self, list):
        if self.__first_to_enter_callback_two:
            self.__first_to_enter_callback_two = False
            self.sensing_wrapper.unsubscribe("VisiblePeopleList")
            print(list)
            self.speech_wrapper.say("Let me estimate the amount.")
            if len(list) == 1:
                self.speech_wrapper.say("I think you are only a single person")
            elif len(list) == 2:
                self.speech_wrapper.say("I think you are two people")

    def __on_just_arrived(self, id):
        print(id)
        self.speech_wrapper.animated_say("id %s just arrived!" % id)

    def __on_people_list(self, list):
        self.speech_wrapper.animated_say("list changed!" % list)
        print(list)

    def __on_population_updated(self, args):
        self.speech_wrapper.animated_say("population updated!")
        print("population updated")

    def __navigate(self):
        # Load a previously saved exploration
        self.sensing_wrapper.load_exploration_from_robot(
            '/home/nao/group02HS19/map-4m.explo')
        # self.position_movement_wrapper.navigate_to_coordinate_on_map()

        # Relocalize the robot and start the localization process.
        pos = [0., 0.]
        self.position_movement_wrapper.relocalize_in_map(pos)
        self.sensing_wrapper.start_localization()

        # Navigate to another place in the map
        self.position_movement_wrapper.navigate_to_coordinate_on_map([
            1., 0., 0.])

        # Check where the robot arrived
        print "I reached: " + \
              str(self.sensing_wrapper.get_robot_position_in_map()[0])

        # Stop localization
        self.sensing_wrapper.stop_localization()

    def __ask_to_follow(self):
        print('hi')
        self.body_movement_wrapper.moveArmsUp(Actuators.RArm, 120)
        time.sleep(1)
        self.body_movement_wrapper.moveArmsDown(Actuators.RArm, 160)

    def __recognize_persons(self):
        amount = 4
        if amount == 1:
            self.speech_wrapper.say("I am seeing one person")
        elif amount > 1 and amount < (const.max_persons + 1):
            self.speech_wrapper.say("I am seeing {} persons".format(amount))
        else:
            self.speech_wrapper.say("I am seeing {} persons".format(amount))

        self.person_amount = amount
        self.__ask_person_amount_correct()

    def __ask_person_amount(self):
        self.person_amount = None
        self.speech_wrapper.say("For how many people should I search a table?")
        self.speech_wrapper.say("We have tables for {} to {} persons".format(const.min_persons, const.max_persons))
        self.speech_wrapper.start_to_listen(
            const.persons_strings, const.speech_recognition_language, self.__ask_person_amount_callback)
        time.sleep(5)
        self.speech_wrapper.stop_listening()
        if self.person_amount is None:
            self.__ask_person_amount()
        else:
            self.__ask_person_amount_correct()

    def __ask_person_amount_callback(self, message):
        print('Ask Person amount triggered')

        m = message[0]
        if m != '':
            word_found = next((x for x in const.persons_strings if x in m), None)
            if word_found is not None:
                self.person_amount = const.persons_strings.index(word_found) + 1

        print(message)

    def __ask_person_amount_correct(self):
        if self.person_amount == 1:
            self.speech_wrapper.say(
                "Would you like me to search a table for a single person?")
        else:
            self.speech_wrapper.say(
                "Would you like me to search a table for {} people?".format(self.person_amount))

        self.speech_wrapper.start_to_listen(
            ['Yes', 'No'], const.speech_recognition_language, self.__ask_person_amount_correct_callback)
        time.sleep(5)
        self.speech_wrapper.stop_listening()

        if not hasattr(self, 'person_amount_correct'):
            self.__ask_person_amount_correct()
            return

        if self.person_amount_correct:
            print(self.person_amount)
            if self.person_amount < const.min_persons or self.person_amount > const.max_persons:
                self.speech_wrapper.say("Unfortunately, we do not have a table for this amount of people.")
                return
            self.__search_table()
        else:
            self.__ask_person_amount()

    def __initialize_wrappers(self):
        self.body_movement_wrapper = BodyMovementWrapper()
        self.position_movement_wrapper = PositionMovementWrapper()
        self.sensing_wrapper = SensingWrapper()
        self.speech_wrapper = SpeechWrapper()

    def __ask_person_amount_correct_callback(self, message):
        print('Ask Person triggered')
        if message[0] != '':
            if 'No' in message[0]:
                self.person_amount_correct = False
            elif 'Yes' in message[0]:
                self.person_amount_correct = True
        print(message)

    def __search_table(self):
        self.speech_wrapper.say("Please wait. I will search the perfect table for you")

    def __return_to_waiting_zone(self):
        # self.position_movement_wrapper.learn_home()
        # self.position_movement_wrapper.move(1, 2, 0)
        # self.position_movement_wrapper.go_to_home()
        pass

    def __assign_table(self):
        pass

    def __create_map(self, radius):
        # Wake up robot
        # Wake up robot
        self.__robot.ALMotion.wakeUp()  # Explore the environement, in a radius of 2 m.
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
        self.position_movement_wrapper.navigate_to_coordinate_on_map([
            0., 0., 0.])
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
