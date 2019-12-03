import json
import os
import time

import const
# import PIL  # import used for scipy.misc.imsave
from person_amount_estimator import PersonAmountEstimator
from robot.body_movement_wrapper import Actuators
from robot.body_movement_wrapper import BodyMovementWrapper
from robot.position_movement_wrapper import PositionMovementWrapper
from robot.sensing_wrapper import SensingWrapper
from robot.speech_wrapper import SpeechWrapper


# import face_recognition


class Behavior(object):

    def __init__(self):
        self.__robot = const.robot
        self.__initialize_wrappers()
        self.__load_locales()
        self.__wait_for_new_customers = True
        self.__got_face = False
        self.__first_person_detected = False
        self.__first_to_enter_callback = True
        self.__first_to_enter_callback_two = True
        self.__person_amount = 0
        self.__person_amount_correct = False
        self.__waiting_for_an_answer = False
        self.__recognized_words_certainty = 0
        self.__person_amount_estimator = PersonAmountEstimator()

    def __initialize_wrappers(self):
        self.body_movement_wrapper = BodyMovementWrapper()
        self.position_movement_wrapper = PositionMovementWrapper()
        self.sensing_wrapper = SensingWrapper()
        self.speech_wrapper = SpeechWrapper()

    def __load_locales(self):
        with open(os.path.join(os.getcwd(), const.path_to_locale_file), 'r') as f:
            data = json.load(f)
        self.__sentences = data["sentences"]
        self.__vocabularies = data["vocabularies"]

    def start_behavior(self):
        self.position_movement_wrapper.learn_home()
        self.__setup_customer_reception()

        while not self.__person_amount_correct or self.__person_amount < const.min_persons or self.__person_amount > const.max_persons:

            if self.__person_amount < const.min_persons or self.__person_amount > const.max_persons:
                self.speech_wrapper.say(self.__sentences["noTablesForAmount"])

            if self.__ask_person_amount() is not None
                if self.__recognized_words_certainty > 0.55:
                    break

        self.__search_table()

        # if self.__search_table():
        #     self.__ask_to_follow()
        #     self.__go_to_table()
        #     self.__assign_table()
        #     self.__return_to_waiting_zone()
        #     self.__setup_customer_reception()
        # else:
        #     self.__say_no_table_available()
        #     self.__setup_customer_reception()


    def __setup_customer_reception(self):
        if not self.sensing_wrapper.is_face_detection_enabled():
            raise Exception('No Face detection possible with this system!')

        self.sensing_wrapper.reset_population()

        self.sensing_wrapper.set_maximum_detection_range_in_meters(3)
        self.sensing_wrapper.enable_face_recognition()
        self.sensing_wrapper.enable_face_tracking()
        self.sensing_wrapper.enable_fast_mode()

        self.body_movement_wrapper.enable_autonomous_life(True)

        face_detected_subscriber = self.sensing_wrapper.get_memory_subscriber("FaceDetected")
        face_detected_subscriber.signal.connect(self.__on_human_detected)
        self.sensing_wrapper.start_face_detection("detect_face")

        while not self.__first_person_detected:
            time.sleep(0.1)

        time.sleep(2)

        for i in range(const.people_counting_number_of_retries):
            if not self.__ask_person_amount_correct():
                self.speech_wrapper.say(self.__sentences["estimateAmountOfPeopleAgain"])
                self.__person_amount = self.__count_people(const.people_counting_time)
            else:
                break                

        self.body_movement_wrapper.enable_autonomous_life(False)


    def __count_people(self, time):
        self.__person_amount_estimator.clear_results()
        self.__person_amount_estimator.change_picture_file_name(const.people_recognized)
        self.__person_amount_estimator.start_estimation()
        self.speech_wrapper.say(self.__sentences["estimateAmountOfPeople"])
        self.speech_wrapper.say(self.__sentences["stayInFrontOfMe"])
        time.sleep(time)
        self.__person_amount_estimator.stop_estimation()
        return self.__person_amount_estimator.get_estimated_person_amount()


    def __on_human_detected(self, value):
        if value == []:  # empty value when the face disappears
            self.__got_face = False
        elif not self.__got_face:
            self.__got_face = True
            if self.__first_to_enter_callback:
                self.__first_to_enter_callback = False

                self.sensing_wrapper.stop_face_detection("detect_face")
                self.__wait_for_new_customers = False
                self.speech_wrapper.say(self.__sentences["greeting"])
                self.__person_amount = self.__count_people(const.people_counting_time)
                self.__first_person_detected = True

    def __ask_person_amount(self):
        self.__person_amount = None
        self.speech_wrapper.say(self.__sentences["askAmountToSearch"])
        self.speech_wrapper.say(self.__sentences["availableTables"].format(const.min_persons, const.max_persons))

        self.speech_wrapper.start_to_listen(
            self.__vocabularies["personAmount"],
            const.speech_recognition_language,
            const.speech_recognition_precision,
            self.__on_person_amount_answered)

        self.__waiting_for_an_answer = True
        while self.__waiting_for_an_answer:
            time.sleep(1)

        self.speech_wrapper.stop_listening()

        return self.__person_amount

        # if self.__person_amount is None:
        #     self.__ask_person_amount()
        # else:
        #     if self.__recognized_words_certainty > 0.55:
        #         if self.__person_amount < const.min_persons or self.__person_amount > const.max_persons:
        #             self.speech_wrapper.say(self.__sentences["noTablesForAmount"])
        #             return
        #         self.__search_table()
        #     else:
        #         self.__ask_person_amount_correct()

    def __on_person_amount_answered(self, message):
        print('Ask Person amount triggered')

        m = message[0]
        if m != '':
            word_found = next((x for x in self.__vocabularies["personAmount"] if x in m), None)
            if word_found is not None:
                self.__recognized_words_certainty = message[1]
                self.__person_amount = self.__vocabularies["personAmount"].index(word_found) + 1
                self.__waiting_for_an_answer = False

        print(message)

    def __ask_person_amount_correct(self):
        if self.__person_amount == 1:
            self.speech_wrapper.say(self.__sentences["askToSearchTableForOnePerson"])
        elif self.__person_amount == 0:
            self.__ask_person_amount()
        else:
            self.speech_wrapper.say(self.__sentences["askToSearchTableForMultiplePersons"].format(self.__person_amount))

        self.speech_wrapper.start_to_listen(
            self.__vocabularies["yes"] + self.__vocabularies["no"],
            const.speech_recognition_language,
            const.speech_recognition_precision,
            self.__on_person_amount_correct_answered)

        self.__waiting_for_an_answer = True
        while self.__waiting_for_an_answer:
            time.sleep(1)

        self.speech_wrapper.stop_listening()

        return self.__person_amount_correct

        # if self.__person_amount_correct:
        #     print(self.__person_amount)
        #     if self.__person_amount < const.min_persons or self.__person_amount > const.max_persons:
        #         self.speech_wrapper.say(self.__sentences["noTablesForAmount"])
        #         return
        #     self.__search_table()
        # else:
        #     self.__ask_person_amount()

    def __on_person_amount_correct_answered(self, message):
        print('Ask Person triggered')
        if message[0] != '':
            msg = message[0].replace('<...>', '').strip()
            if msg in self.__vocabularies["no"]:
                self.__person_amount_correct = False
                self.__waiting_for_an_answer = False
            elif msg in self.__vocabularies["yes"]:
                self.__person_amount_correct = True
                self.__waiting_for_an_answer = False
        print(message)

    def __search_table(self):
        self.speech_wrapper.say(self.__sentences["searchTable"])
        self.position_movement_wrapper.move_to(0, 0, 180)
        self.body_movement_wrapper.enable_autonomous_life(False)
        self.body_movement_wrapper.set_head_down(0)
        self.body_movement_wrapper.set_head_right(0)
        time.sleep(1)

        try:
            while True:
                goal_center = self.sensing_wrapper.get_red_cups_center_position(self.__person_amount)
                if goal_center is not None:
                    detected_persons = self.sensing_wrapper.get_object_positions("person")
                    table_occupied = self.__is_table_occupied(detected_persons, goal_center)
                    if table_occupied:
                        self.body_movement_wrapper.enable_autonomous_life(True)
                        self.position_movement_wrapper.move_to(0, 0, 180)
                        self.speech_wrapper.say(self.__sentences["noTableAvailable"])
                        time.sleep(1)
                        self.speech_wrapper.say(self.__sentences["comeBackAnotherDay"])
                        break
                    else:
                        self.__ask_to_follow()
                        self.__go_to_table(goal_center)
                        self.body_movement_wrapper.enable_autonomous_life(True)
                        self.position_movement_wrapper.move_to(0, 0, 180)
                        self.__assign_table()
                        break
                else:
                    self.__search_for_correct_table()
        except Exception, e:
            print(e)
            self.position_movement_wrapper.stop_movement()

    def __say_no_table_available(self):
        self.body_movement_wrapper.enable_autonomous_life(True)
        self.position_movement_wrapper.move_to(0, 0, 180)
        self.speech_wrapper.say(self.__sentences["noTableAvailable"])
        time.sleep(1)
        self.speech_wrapper.say(self.__sentences["comeBackAnotherDay"])

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
        self.speech_wrapper.say(self.__sentences["askToFollow"])
        self.body_movement_wrapper.moveArmsUp(Actuators.RArm, 120)
        time.sleep(1)
        self.body_movement_wrapper.moveArmsDown(Actuators.RArm, 160)

    def __go_to_table(self, goal_center):
        self.__move_towards_goal_location(goal_center)
        while True:
            time_movement_start = round(time.time() * 1000)
            distance_meters = self.sensing_wrapper.get_sonar_distance("Front")
            if float(distance_meters) >= 1.5:
                if float(distance_meters) >= 1.0:
                    goal_center = self.sensing_wrapper.get_red_cups_center_position(self.__person_amount)
                    if goal_center is not None:
                        now = round(time.time() * 1000)
                        diff = now - time_movement_start
                        if diff <= 2000:
                            self.__move_towards_goal_location(goal_center)
                        else:
                            self.position_movement_wrapper.move(0.5, 0, 0)
                    else:
                        self.position_movement_wrapper.move(0.5, 0, 0)
                else:
                    self.position_movement_wrapper.stop_movement()
                    break
            else:
                if float(distance_meters) <= .8:
                    self.position_movement_wrapper.stop_movement()
                    self.position_movement_wrapper.move_to(0, 0, 180)
                    break
                else:
                    self.position_movement_wrapper.move(0.5, 0, 0)

    def __move_towards_goal_location(self, goal_center):
        pixels_to_move_x = (640 / 2) - goal_center[0]
        degrees_to_move_x = int(round(pixels_to_move_x / 15.0))
        print("table goal position: %s, move_x: %s" % (goal_center, degrees_to_move_x))
        self.position_movement_wrapper.move(0.5, 0, degrees_to_move_x)

    def __search_for_correct_table(self):
        print("Couldn't find your object. Searching around")
        number_of_turns = 0
        max_turns = 9

        while True:
            goal_centers = self.sensing_wrapper.get_red_cups_center_position(self.__person_amount)
            if goal_centers is None:
                if number_of_turns is 0:
                    self.position_movement_wrapper.stop_movement()
                    self.body_movement_wrapper.set_head_down(0)
                    self.position_movement_wrapper.move_to(0, 0, 90)

                if number_of_turns < max_turns:
                    self.position_movement_wrapper.move_to(0, 0, -20)
                    time.sleep(.5)
                    number_of_turns = number_of_turns + 1
                else:
                    self.position_movement_wrapper.move_to(0, 0, 90)
                    self.position_movement_wrapper.move(.5, 0, 0)
                    time.sleep(2)
                    self.position_movement_wrapper.stop_movement()
                    number_of_turns = 0
            else:
                break

    def __assign_table(self):
        self.speech_wrapper.say(self.__sentences["assignTable"])
        time.sleep(2)
        self.__wait_for_new_customers = True

    def __return_to_waiting_zone(self):
        self.position_movement_wrapper.go_to_home()
