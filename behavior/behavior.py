import json
import os
import time

import const
from pepper_waiter.utilities.navigation.navigator import Navigator
from pepper_waiter.utilities.person_amount_estimator import PersonAmountEstimator
from pepper_waiter.wrappers.body_movement_wrapper import BodyMovementWrapper
from pepper_waiter.wrappers.position_movement_wrapper import PositionMovementWrapper
from pepper_waiter.wrappers.sensing_wrapper import SensingWrapper
from pepper_waiter.wrappers.speech_wrapper import SpeechWrapper
from pepper_waiter.utilities.table_search_state import TableFound, TableOccupied, TableNotFound, TableStateError
from pepper_waiter.wrappers.tablet_wrapper import TabletWrapper
from pepper_waiter.wrappers.sound_wrapper import SoundWrapper


class Behavior(object):

    def __init__(self):
        self.__robot = const.robot
        self.__initialize_wrappers()
        self.__load_locales()
        self.__init_behavior_state()
        self.__navigator = Navigator(self.body_movement_wrapper,
                                     self.__position_movement_wrapper,
                                     self.__sensing_wrapper,
                                     self.__speech_wrapper,
                                     self.__sentences)

    def __initialize_wrappers(self):
        self.body_movement_wrapper = BodyMovementWrapper()
        self.__position_movement_wrapper = PositionMovementWrapper()
        self.__sensing_wrapper = SensingWrapper()
        self.__speech_wrapper = SpeechWrapper()
        self.__tablet_wrapper = TabletWrapper()
        self.sound_wrapper = SoundWrapper()

    def __load_locales(self):
        with open(os.path.join(os.getcwd(), const.path_to_locale_file), 'r') as f:
            data = json.load(f)
        self.__sentences = data["sentences"]
        self.__vocabularies = data["vocabularies"]

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

    def start_behavior(self):
        # self.sound_wrapper.stop_all()
        while True:
            try:
                print("starting")
                self.body_movement_wrapper.initial_position()
                self.__setup_customer_reception()
                self.__check_person_amount()

                self.__speech_wrapper.say(self.__sentences["searchTable"])
                self.__position_movement_wrapper.move_to(0, 0, 180)
                self.sound_wrapper.start_playing_sound(const.path_to_waiting_music)

                self.__try_find_table()

                self.__navigator.navigate_to_waiting_area()
                self.__init_behavior_state()
            except Exception, ex:
                print("behaviour loop exception %s" % ex)
                self.__speech_wrapper.animated_say(self.__sentences["error"])
                self.__navigator.navigate_to_waiting_area()
                self.__init_behavior_state()

    def __setup_customer_reception(self):
        if not self.__sensing_wrapper.is_face_detection_enabled():
            raise Exception('No Face detection possible with this system!')

        self.__sensing_wrapper.set_maximum_detection_range_in_meters(5)
        self.__sensing_wrapper.enable_face_recognition()
        self.__sensing_wrapper.enable_face_tracking()
        # self.__sensing_wrapper.enable_fast_mode()

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
        self.body_movement_wrapper.enable_autonomous_life(True)
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
                self.body_movement_wrapper.enable_autonomous_life(False)
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

    def __try_find_table(self):
        search_state = self.__navigator.search_table(self.__person_amount)
        if isinstance(search_state, TableFound):
            self.sound_wrapper.stop_all()
            self.__ask_to_follow()
            self.sound_wrapper.start_playing_sound(const.path_to_waiting_music)

            try:
                self.__navigator.navigate_to_table(self.__person_amount)
                if self.__navigator.navigation_successful is True:
                    time.sleep(2)

                    self.body_movement_wrapper.set_head_up(30)
                    self.body_movement_wrapper.set_head_left(0)
                    self.__position_movement_wrapper.move_to(0, 0, 180)
                    self.sound_wrapper.stop_all()

                    self.__assign_table()
                else:
                    self.__speech_wrapper.animated_say(self.__sentences["navigationUnsuccessful"])
            except ValueError, err:
                self.__speech_wrapper.animated_say(self.__sentences["error"])
                print("Error while navigating: %s" % err)
        else:
            if isinstance(search_state, TableOccupied):
                self.__say_table_occupied()
            elif isinstance(search_state, TableNotFound):
                self.__speech_wrapper.animated_say(self.__sentences["noTablesForAmount"])
            elif isinstance(search_state, TableStateError):
                self.__speech_wrapper.animated_say(self.__sentences["error"])
            else:
                self.__speech_wrapper.animated_say("Ficken! Das war nicht gut ich tubel.")

    def __ask_to_follow(self):
        self.__speech_wrapper.animated_say(self.__sentences["askToFollow"])

    def __assign_table(self):
        self.body_movement_wrapper.enable_autonomous_life(True)
        time.sleep(.5)
        self.__speech_wrapper.animated_say(self.__sentences["assignTable"])
        self.__wait_for_new_customers = True
        self.body_movement_wrapper.enable_autonomous_life(False)
        time.sleep(2)

    def __say_table_occupied(self):
        self.body_movement_wrapper.enable_autonomous_life(True)
        self.__position_movement_wrapper.move_to(0, 0, 180)
        self.__speech_wrapper.animated_say(self.__sentences["noTableAvailable"])
        time.sleep(.5)
        self.__speech_wrapper.animated_say(self.__sentences["comeBackAnotherDay"])
