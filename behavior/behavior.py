import os
import time

import numpy
import scipy.misc
import const
import cv2
import sys
import json
import face_recognition
# import PIL  # import used for scipy.misc.imsave
from person_amount_estimator import PersonAmountEstimator
from robot.body_movement_wrapper import BodyMovementWrapper
from robot.object_detection.Camera import Camera
from robot.object_detection.FileTransfer import FileTransfer
from robot.position_movement_wrapper import PositionMovementWrapper
from robot.sensing_wrapper import SensingWrapper
from robot.speech_wrapper import SpeechWrapper
from robot.body_movement_wrapper import Actuators


class Behavior(object):

    def __init__(self):
        self.__robot = const.robot
        self.__initialize_wrappers()
        self.__load_locales()
        self.__got_face = False
        self.__first_person_detected = False
        self.__first_to_enter_callback = True
        self.__first_to_enter_callback_two = True
        self.__person_amount = 0
        self.__person_amount_correct = False
        self.__waiting_for_an_answer = False
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
        # self.body_movement_wrapper.move_head_up(10)
        # self.speech_wrapper.say("hello")
        # self.speech_wrapper.say("learning home")
        # self.position_movement_wrapper.learn_home()
        self.setup_customer_reception()
        # self.__get_number_of_faces_from_picture()
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
        self.sensing_wrapper.enable_fast_mode()

        self.body_movement_wrapper.enable_autonomous_life(True)

        face_detected_subscriber = self.sensing_wrapper.get_memory_subscriber("FaceDetected")
        face_detected_subscriber.signal.connect(self.__on_human_tracked)
        self.sensing_wrapper.subscribe("detect_face")

        while not self.__first_person_detected:
            time.sleep(1)

        # self.speech_wrapper.say("Hello I'm currently estimating the amount of people.")
        # self.speech_wrapper.say("Hmm hmm Hmm let me estimate")
        # self.speech_wrapper.say("Wait a second my friend")

        self.__person_amount_estimator.stop_estimation()
        self.__person_amount = self.__person_amount_estimator.get_estimated_person_amount()

        # self.__person_amount = self.__get_number_of_faces_and_store_picture(const.img_people_before_table_search)
        self.__ask_person_amount_correct()
        self.body_movement_wrapper.enable_autonomous_life(False)

        self.__person_amount = self.__get_number_of_faces_and_store_picture(const.img_people_before_table_search)
        self.__ask_person_amount_correct()

        while True:
            time.sleep(1)

    def __get_number_of_faces_and_store_picture(self, file_name_without_jpg):
        self.__camera = Camera(const.robot)
        self.__camera.configure_camera(self.__camera.cameras["top"], self.__camera.resolutions["640x480"],
                                       self.__camera.formats["jpg"])
        self.__file_transfer = FileTransfer(const.robot)

        remote_folder_path = "/home/nao/recordings/cameras/"
        file_name = file_name_without_jpg + ".jpg"
        self.__camera.take_picture(remote_folder_path, file_name)
        local_project_path = const.path_to_pictures + file_name
        remote = remote_folder_path + file_name
        self.__file_transfer.get(remote, local_project_path)
        number_of_faces = self.__get_number_of_faces_from_picture(local_project_path)
        return number_of_faces

    def __get_number_of_faces_from_picture(self, picture_path):
        # Create the haar cascade
        faceCascade = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")

        image = cv2.imread(picture_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        return len(faces)

    def __on_human_tracked(self, value):
        if value == []:  # empty value when the face disappears
            self.__got_face = False
        elif not self.__got_face:
            self.__got_face = True
            if self.__first_to_enter_callback:
                self.__first_to_enter_callback = False
                self.sensing_wrapper.unsubscribe("huso")
                self.speech_wrapper.say_random(self.__sentences["greeting"])
                self.speech_wrapper.say_random(self.__sentences["estimateAmountOfPeople"])
                self.speech_wrapper.say(self.__sentences["stayInFrontOfMe"])
                self.__first_person_detected = True

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

    def __recognize_persons(self):
        amount = 4
        if amount == 1:
            self.speech_wrapper.say(self.__sentences["seeingOnePerson"])
        elif amount > 1 and amount < (const.max_persons + 1):
            self.speech_wrapper.say(self.__sentences["seeingMultiplePersons"].format(amount))
        else:
            self.speech_wrapper.say(self.__sentences["seeingMultiplePersons"].format(amount))

        self.__person_amount = amount
        self.__ask_person_amount_correct()

    def __ask_person_amount(self):
        self.__person_amount = None
        self.speech_wrapper.say(self.__sentences["askAmountToSearch"])
        self.speech_wrapper.say(self.__sentences["availableTables"].format(const.min_persons, const.max_persons))
        self.speech_wrapper.start_to_listen(
            self.__vocabularies["personAmount"], const.speech_recognition_language, self.__on_person_amount_answered)
        self.__waiting_for_an_answer = True
        while self.__waiting_for_an_answer:
            time.sleep(1)
        self.speech_wrapper.stop_listening()
        if self.__person_amount is None:
            self.__ask_person_amount()
        else:
            self.__ask_person_amount_correct()

    def __on_person_amount_answered(self, message):
        print('Ask Person amount triggered')

        m = message[0]
        if m != '':
            word_found = next((x for x in self.__vocabularies["personAmount"] if x in m), None)
            if word_found is not None:
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
            ['Yes', 'No'], const.speech_recognition_language, self.__on_person_amount_correct_answered)
        self.__waiting_for_an_answer = True
        while self.__waiting_for_an_answer:
            time.sleep(1)
        self.speech_wrapper.stop_listening()

        if self.__person_amount_correct:
            print(self.__person_amount)
            if self.__person_amount < const.min_persons or self.__person_amount > const.max_persons:
                self.speech_wrapper.say_random(self.__sentences["noTablesForAmount"])
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
        self.speech_wrapper.say_random(self.__sentences["searchTable"])

        # TODO search table...

        # when table found
        self.__return_to_waiting_zone()

    def __return_to_waiting_zone(self):
        if self.__find_person():
            self.speech_wrapper.say('I remember you')
        else:
            self.speech_wrapper.say('Who are you?')
        # self.position_movement_wrapper.go_to_home()
        # TODO change this or create attribute
        # if self.assigned:
        #     # self.setup_customer_reception()
        #     pass
        # else:
        self.__ask_to_follow()
        self.__return_to_table()

    def __find_person(self):
        self.body_movement_wrapper.enable_autonomous_life(True)

        while self.__get_number_of_faces_and_store_picture(const.img_people_after_table_search) == 0:
            time.sleep(2)

        self.body_movement_wrapper.enable_autonomous_life(False)

        people_before_table_search = face_recognition.load_image_file(
            os.path.join(os.getcwd(), const.path_to_pictures, const.img_people_before_table_search + '.jpg'))
        people_after_table_search = face_recognition.load_image_file(
            os.path.join(os.getcwd(), const.path_to_pictures, const.img_people_after_table_search + '.jpg'))
        known_faces = []

        for encoding in face_recognition.face_encodings(people_before_table_search):
            known_faces.append(encoding)

        for face in face_recognition.face_encodings(people_after_table_search):
            if True in face_recognition.compare_faces(known_faces, face):
                return True

        return False

    def __ask_to_follow(self):
        self.speech_wrapper.say(self.__sentences["askToFollow"])
        self.body_movement_wrapper.moveArmsUp(Actuators.RArm, 120)
        time.sleep(1)
        self.body_movement_wrapper.moveArmsDown(Actuators.RArm, 160)

    def __return_to_table(self):
        # TODO implement logic to return to the table that was found

        self.__assign_table()

    def __assign_table(self):
        self.speech_wrapper.say(self.__sentences["assignTable"])
        time.sleep(2)
        self.__return_to_waiting_zone()

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
