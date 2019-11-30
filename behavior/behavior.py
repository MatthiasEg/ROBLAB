import json
import os
import time

# import face_recognition

import const
# import PIL  # import used for scipy.misc.imsave
from person_amount_estimator import PersonAmountEstimator
from robot.body_movement_wrapper import Actuators
from robot.body_movement_wrapper import BodyMovementWrapper
from robot.position_movement_wrapper import PositionMovementWrapper
from robot.sensing_wrapper import SensingWrapper
from robot.speech_wrapper import SpeechWrapper


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
        self.__setup_customer_reception()
        self.__ask_person_amount_correct()
        self.__person_amount_estimator.clear_results()
        # self.__get_number_of_faces_from_picture()
        # self.__recognize_persons()

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
        face_detected_subscriber.signal.connect(self.__human_detected)
        self.sensing_wrapper.subscribe("detect_face")

        while not self.__first_person_detected:
            time.sleep(0.1)

        time.sleep(2)
        self.__person_amount_estimator.stop_estimation()
        self.__person_amount = self.__person_amount_estimator.get_estimated_person_amount()

        self.body_movement_wrapper.enable_autonomous_life(False)

    def __human_detected(self, value):
        if value == []:  # empty value when the face disappears
            self.__got_face = False
        elif not self.__got_face:
            self.__got_face = True
            if self.__first_to_enter_callback:
                self.__first_to_enter_callback = False

                self.__person_amount_estimator.change_picture_file_name(const.img_people_before_table_search)
                self.__person_amount_estimator.start_estimation()

                self.sensing_wrapper.unsubscribe("detect_face")
                self.__wait_for_new_customers = False
                self.speech_wrapper.say(self.__sentences["greeting"])
                self.speech_wrapper.say(self.__sentences["estimateAmountOfPeople"])
                self.speech_wrapper.say(self.__sentences["stayInFrontOfMe"])
                self.__first_person_detected = True

    def __recognize_persons(self):
        amount = 4
        if amount == 1:
            self.speech_wrapper.say(self.__sentences["seeingOnePerson"])
        else:
            self.speech_wrapper.say(self.__sentences["seeingMultiplePersons"].format(amount))

        self.__person_amount = amount
        self.__ask_person_amount_correct()

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
        if self.__person_amount is None:
            self.__ask_person_amount()
        else:
            if self.__recognized_words_certainty > 0.55:
                if self.__person_amount < const.min_persons or self.__person_amount > const.max_persons:
                    self.speech_wrapper.say(self.__sentences["noTablesForAmount"])
                    return
                self.__search_table()
            else:
                self.__ask_person_amount_correct()

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

        if self.__person_amount_correct:
            print(self.__person_amount)
            if self.__person_amount < const.min_persons or self.__person_amount > const.max_persons:
                self.speech_wrapper.say(self.__sentences["noTablesForAmount"])
                return
            self.__search_table()
        else:
            self.__ask_person_amount()

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

        # TODO search table...

        # when table found
        self.__return_to_waiting_zone()

    def __ask_to_follow(self):
        self.speech_wrapper.say(self.__sentences["askToFollow"])
        self.body_movement_wrapper.moveArmsUp(Actuators.RArm, 120)
        time.sleep(1)
        self.body_movement_wrapper.moveArmsDown(Actuators.RArm, 160)

    def __go_to_table(self):
        # TODO implement logic to return to the table that was found

        self.__assign_table()

    def __assign_table(self):
        self.speech_wrapper.say(self.__sentences["assignTable"])
        time.sleep(2)
        self.__wait_for_new_customers = True
        self.__return_to_waiting_zone()

    def __return_to_waiting_zone(self):
        self.position_movement_wrapper.go_to_home()
        if self.__wait_for_new_customers:
          self.setup_customer_reception()
        else:
            self.__ask_to_follow()
            self.__go_to_table()
