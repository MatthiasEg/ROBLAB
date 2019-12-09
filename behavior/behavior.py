import json
import os
import time

import const
import numpy as np
import scipy.misc
from person_amount_estimator import PersonAmountEstimator
from robot.body_movement_wrapper import BodyMovementWrapper
from robot.position_movement_wrapper import PositionMovementWrapper
from robot.sensing_wrapper import SensingWrapper
from robot.speech_wrapper import SpeechWrapper
from robot.table_goal_position_state import GoalTableFound, MultipleTableGoalsFound, GoalTableNotFound
from robot.table_search_state import TableFound, TableOccupied, TableNotFound, TableStateError
from robot.tablet_wrapper import TabletWrapper
from robot.sound_wrapper import SoundWrapper

from threading import Thread


class Behavior(object):

    def __init__(self):
        self.__robot = const.robot
        self.__initialize_wrappers()
        self.__load_locales()
        self.__init_behavior_state()

    def __init_behavior_state(self):
        self.__person_amount_estimator = PersonAmountEstimator()
        self.__wait_for_new_customers = True
        self.__got_face = False
        self.__first_person_detected = False
        self.__first_to_enter_callback = True
        self.__first_to_enter_callback_two = True
        self.__person_amount = 0
        self.__person_amount_correct = False
        self.__waiting_for_an_answer = False
        self.__recognized_words_certainty = 0
        self.__counter_no_user_interaction = 0

    def __initialize_wrappers(self):
        self.body_movement_wrapper = BodyMovementWrapper()
        self.__position_movement_wrapper = PositionMovementWrapper()
        self.__sensing_wrapper = SensingWrapper()
        self.__speech_wrapper = SpeechWrapper()
        self.__tablet_wrapper = TabletWrapper()
        self.__sound_wrapper = SoundWrapper()

    def start_behavior(self):
        self.__robot.ALNavigation.stopLocalization()
        self.__robot.ALNavigation.loadExploration("/home/nao/2019-12-09T180032.136Z.explo")
        self.__robot.ALNavigation.relocalizeInMap([0., 0., 0.])
        self.__robot.ALNavigation.startLocalization()

        while True:
            print("starting")
            self.body_movement_wrapper.initial_position()
            self.__setup_customer_reception()
            self.__check_person_amount()
            self.__speech_wrapper.say(self.__sentences["searchTable"])
            self.__position_movement_wrapper.move_to(0, 0, 180)
            while True:
                search_state = self.__search_table()
                if isinstance(search_state, TableFound):
                    self.__ask_to_follow()
                    self.__go_to_table(search_state.goal_location)
                    time.sleep(3)
                    self.__position_movement_wrapper.move_to(0, 0, 180)
                    self.body_movement_wrapper.set_head_up(30)
                    self.body_movement_wrapper.set_head_left(0)
                    self.body_movement_wrapper.enable_autonomous_life(True)
                    time.sleep(.5)
                    self.__assign_table()
                    time.sleep(2)
                    self.body_movement_wrapper.enable_autonomous_life(False)
                    break
                else:
                    if self.__person_amount < const.max_persons:
                        self.__person_amount += 1
                        continue
                    else:
                        if isinstance(search_state, TableOccupied):
                            self.__say_table_occupied()
                        elif isinstance(search_state, TableNotFound):
                            self.__speech_wrapper.animated_say(self.__sentences["noTablesForAmount"])
                        elif isinstance(search_state, TableStateError):
                            self.__speech_wrapper.animated_say(self.__sentences["error"])
                        break
            self.__init_behavior_state()
            self.__robot.ALNavigation.navigateToInMap([0., 0., 0.])

    def __setup_customer_reception(self):
        if not self.__sensing_wrapper.is_face_detection_enabled():
            raise Exception('No Face detection possible with this system!')

        self.__sensing_wrapper.reset_population()

        self.__sensing_wrapper.set_maximum_detection_range_in_meters(3)
        self.__sensing_wrapper.enable_face_recognition()
        self.__sensing_wrapper.enable_face_tracking()
        self.__sensing_wrapper.enable_fast_mode()

        self.body_movement_wrapper.enable_autonomous_life(True)

        face_detected_subscriber = self.__sensing_wrapper.get_memory_subscriber("FaceDetected")
        face_detected_subscriber.signal.connect(self.__on_human_detected)
        self.__sensing_wrapper.start_face_detection("detect_face")

        while not self.__first_person_detected:
            time.sleep(0.1)

        for i in range(const.people_counting_number_of_retries):
            # self.__tablet_wrapper.showImage(os.path.join(os.getcwd(), const.path_to_pictures, const.img_people_recognized + '.jpg'), 10)
            if self.__person_amount < 1:
                self.__counter_no_user_interaction += 1
                self.__speech_wrapper.say(self.__sentences["seeingNoPersons"])
                self.__speech_wrapper.say(self.__sentences["estimateAmountOfPeopleAgain"])
                self.__person_amount = self.__count_people(const.people_counting_time)
                continue

            if not self.__ask_person_amount_correct():
                self.__speech_wrapper.say(self.__sentences["estimateAmountOfPeopleAgain"])
                self.__person_amount = self.__count_people(const.people_counting_time)
            else:
                break

        if not self.__person_amount_correct:
            self.__ask_person_amount_correct()

        self.body_movement_wrapper.enable_autonomous_life(False)

    def __count_people(self, time_to_estimate):
        self.__person_amount_estimator = PersonAmountEstimator()
        self.__person_amount_estimator.start_estimation()
        time.sleep(time_to_estimate)
        self.__person_amount_estimator.stop_estimation()
        return self.__person_amount_estimator.get_estimated_person_amount()

    def __on_human_detected(self, value):
        if value == []:  # empty value when the face disappears
            self.__got_face = False
        elif not self.__got_face:
            self.__got_face = True
            if self.__first_to_enter_callback:
                self.__first_to_enter_callback = False

                self.__sensing_wrapper.stop_face_detection("detect_face")
                self.__wait_for_new_customers = False
                self.__person_amount_estimator.start_estimation()
                self.__speech_wrapper.animated_say(self.__sentences["greeting"])
                self.__speech_wrapper.say(self.__sentences["estimateAmountOfPeople"])
                self.__speech_wrapper.say(self.__sentences["stayInFrontOfMe"])
                self.__person_amount_estimator.stop_estimation()
                self.__person_amount = self.__person_amount_estimator.get_estimated_person_amount()
                self.__first_person_detected = True

    def __check_person_amount(self):
        while not self.__person_amount_correct or self.__person_amount < const.min_persons or self.__person_amount > const.max_persons:
            if self.__person_amount_correct and (
                    self.__person_amount < const.min_persons or self.__person_amount > const.max_persons):
                self.__speech_wrapper.animated_say(self.__sentences["noTablesForAmount"])

            if self.__ask_person_amount() is not None:
                if self.__recognized_words_certainty > 0.55:
                    self.__person_amount_correct = True
                    continue
                else:
                    self.__ask_person_amount_correct()

    def __ask_person_amount(self):
        self.__person_amount = None
        self.__speech_wrapper.animated_say(self.__sentences["askAmountToSearch"])
        self.__speech_wrapper.animated_say(
            self.__sentences["availableTables"].format(const.min_persons, const.max_persons))

        self.__speech_wrapper.start_to_listen(
            self.__vocabularies["personAmount"],
            const.speech_recognition_language,
            const.speech_recognition_precision,
            self.__on_person_amount_answered)

        self.__waiting_for_an_answer = True
        while self.__waiting_for_an_answer:
            time.sleep(1)

        self.__speech_wrapper.stop_listening()

        return self.__person_amount

    def __on_person_amount_answered(self, message):
        print('Ask Person amount triggered')
        print(message)

        m = message[0]
        if m != '':
            word_found = next((x for x in self.__vocabularies["personAmount"] if x in m.decode('utf-8')), None)
            if word_found is not None:
                self.__recognized_words_certainty = message[1]
                self.__person_amount = self.__vocabularies["personAmount"].index(word_found) + 1
                self.__waiting_for_an_answer = False

    def __ask_person_amount_correct(self):
        if self.__person_amount == 1:
            self.__speech_wrapper.animated_say(self.__sentences["askToSearchTableForOnePerson"])
        elif self.__person_amount == 0:
            return False
        else:
            self.__speech_wrapper.animated_say(
                self.__sentences["askToSearchTableForMultiplePersons"].format(self.__person_amount))

        self.__speech_wrapper.start_to_listen(
            self.__vocabularies["yes"] + self.__vocabularies["no"],
            const.speech_recognition_language,
            const.speech_recognition_precision,
            self.__on_person_amount_correct_answered)

        self.__waiting_for_an_answer = True
        while self.__waiting_for_an_answer:
            time.sleep(1)

        self.__speech_wrapper.stop_listening()

        return self.__person_amount_correct

    def __on_person_amount_correct_answered(self, message):
        print('Ask Person triggered')
        print(message)
        if message[0] != '':
            msg = message[0].replace('<...>', '').strip()
            if msg in self.__vocabularies["no"]:
                self.__person_amount_correct = False
                self.__waiting_for_an_answer = False
            elif msg in self.__vocabularies["yes"]:
                self.__person_amount_correct = True
                self.__waiting_for_an_answer = False

    def __search_table(self):
        self.body_movement_wrapper.enable_autonomous_life(False)
        self.body_movement_wrapper.set_head_down(0)
        self.body_movement_wrapper.set_head_right(0)
        time.sleep(3)

        try:
            while True:
                goal_state = self.__sensing_wrapper.get_red_cups_center_position(self.__person_amount)
                if isinstance(goal_state, GoalTableFound):
                    goal_location = goal_state.goal_location
                    detected_persons = self.__sensing_wrapper.get_object_positions("person")
                    table_occupied = self.__is_table_occupied(detected_persons, goal_location)
                    if table_occupied:
                        return TableOccupied()
                    else:
                        return TableFound(goal_location)
                else:
                    if not self.__search_for_correct_table(goal_state.previous_goal_location):
                        return TableNotFound()
        except Exception, e:
            print(e)
            self.__position_movement_wrapper.stop_movement()
            return TableStateError()

    @staticmethod
    def __is_table_occupied(detected_persons, goal_center):
        if len(detected_persons) > 0:
            person_x_positions = map(lambda r: r["centerX"], detected_persons)
            goal_x = goal_center[0]
            range_min = goal_x - 100 if goal_x - 100 >= 0 else 0
            range_max = goal_x + 100 if goal_x + 100 <= 640 else 640

            for x_coord in person_x_positions:
                if range_min <= x_coord <= range_max:
                    return True
        return False

    def __ask_to_follow(self):
        self.__speech_wrapper.animated_say(self.__sentences["askToFollow"])

    def _go_home_by_cup(self):
        self.body_movement_wrapper.set_head_left(0)
        self.body_movement_wrapper.set_head_up(0)
        self.body_movement_wrapper.set_hip_pitch(-5)
        self.body_movement_wrapper.set_hip_roll(0)
        self.__go_to_table(None, True)

    def __go_to_table(self, goal_center, is_home=False):
        self.body_movement_wrapper.set_head_left(0)
        self.body_movement_wrapper.set_head_up(0)
        self.body_movement_wrapper.set_hip_pitch(-5)
        self.body_movement_wrapper.set_hip_roll(0)
        # self.__move_towards_goal_location(goal_center)
        while True:
            time_movement_start = round(time.time() * 1000)
            distance_meters = self.__sensing_wrapper.get_sonar_distance("Front")
            if float(distance_meters) >= 2.0 and not self.__position_movement_wrapper.collision_avoided:
                if float(distance_meters) >= 1.5:
                    goal_state = self.__sensing_wrapper.get_red_cups_center_position(self.__person_amount)
                    if isinstance(goal_state, GoalTableFound):
                        goal_location = goal_state.goal_location
                        now = round(time.time() * 1000)
                        diff = now - time_movement_start
                        if diff <= 1000:
                            self.__move_towards_goal_location(goal_location)
                        else:
                            self.__position_movement_wrapper.move(0.5, 0, 0)
                    elif isinstance(goal_state, MultipleTableGoalsFound):
                        self.__position_movement_wrapper.stop_movement()
                        self.__speech_wrapper.say(
                            "Unfortunately, I lost track of the right table. Let me have another look around.")
                        self.__search_table()
                    else:
                        self.__position_movement_wrapper.move(0.5, 0, 0)
                else:
                    self.__position_movement_wrapper.stop_movement()
                    break
            else:
                if float(distance_meters) <= 1.1:
                    self.__position_movement_wrapper.collision_avoided = False
                    self.__position_movement_wrapper.stop_movement()
                    print("movement finished")
                    break
                else:
                    self.__position_movement_wrapper.move(0.5, 0, 0)

    def __move_towards_goal_location(self, goal_center):
        pixels_to_move_x = (640 / 2) - goal_center[0]
        degrees_to_move_x = int(round(pixels_to_move_x / 15.0))
        print("table goal position: %s, move_x: %s" % (goal_center, degrees_to_move_x))
        self.__position_movement_wrapper.move(0.5, 0, degrees_to_move_x)

    def __search_for_correct_table(self, previous_goal_location, is_home=False):
        self.__speech_wrapper.say(self.__sentences["moreTimeToSearch"])
        direction_multiplier = 1  # left
        if previous_goal_location is not None and previous_goal_location[0] > (640 / 2):
            direction_multiplier = -1  # right

        degrees_per_step = 20
        max_turns = int(round(360 / degrees_per_step))
        number_of_turns = 0

        self.__position_movement_wrapper.stop_movement()
        self.body_movement_wrapper.set_head_down(0)

        while number_of_turns < max_turns:
            goal_state = self.__sensing_wrapper.get_red_cups_center_position(self.__person_amount)
            if isinstance(goal_state, GoalTableNotFound):
                self.__position_movement_wrapper.move_to(0, 0, degrees_per_step * direction_multiplier)
                time.sleep(.5)
                number_of_turns = number_of_turns + 1
            else:
                return True
        return False

    def __assign_table(self):
        self.__speech_wrapper.animated_say(self.__sentences["assignTable"])
        self.__wait_for_new_customers = True

    def __return_to_waiting_zone(self):
        print("returning home")
        self.__position_movement_wrapper.go_to_home()

    def __say_table_occupied(self):
        self.body_movement_wrapper.enable_autonomous_life(True)
        self.__position_movement_wrapper.move_to(0, 0, 180)
        self.__speech_wrapper.animated_say(self.__sentences["noTableAvailable"])
        time.sleep(.5)
        self.__speech_wrapper.animated_say(self.__sentences["comeBackAnotherDay"])

    def __load_locales(self):
        with open(os.path.join(os.getcwd(), const.path_to_locale_file), 'r') as f:
            data = json.load(f)
        self.__sentences = data["sentences"]
        self.__vocabularies = data["vocabularies"]

    def __create_map(self, radius):
        # Wake up robot
        # Wake up robot
        self.__robot.ALMotion.wakeUp()  # Explore the environement, in a radius of 2 m.
        error_code = self.__sensing_wrapper.explore(radius)
        if error_code != 0:
            print "Exploration failed."
            return
        # Saves the exploration on disk
        path = self.__sensing_wrapper.save_exploration_to_robot()
        print "Exploration saved at path: \"" + path + "\""
        # Start localization to navigate in map
        self.__sensing_wrapper.start_localization()
        # Come back to initial position
        self.__position_movement_wrapper.navigate_to_coordinate_on_map([
            0., 0., 0.])
        # Stop localization
        self.__sensing_wrapper.stop_localization()
        # Retrieve and display the map built by the robot
        result_map = self.__sensing_wrapper.get_metrical_map()
        map_width = result_map[1]
        map_height = result_map[2]
        img = np.array(result_map[4]).reshape(map_width, map_height)
        img = (100 - img) * 2.55  # from 0..100 to 255..0
        img = np.array(img, np.uint8)

        # save image to project root

        scipy.misc.imsave('mapMitRadius{}.jpg'.format(radius), img)
