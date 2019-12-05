import cv2
import statistics as statistics

import const
from math import ceil
from robot.object_detection.camera import Camera
from robot.object_detection.file_transfer import FileTransfer
from thread import start_new_thread


class PersonAmountEstimator:
    def __init__(self):
        self.__should_estimate = True
        self.__all_estimations = []
        self.__picture_names_of_seen_people_amounts = {}
        self.__picture_file_name = const.img_people_recognized
        self.__current_picture_project_path = ""

    def start_estimation(self):
        print("start estimating")
        start_new_thread(self.__estimate, ())

    def __estimate(self):
        i = 1
        while self.__should_estimate:
            old_picture_name = self.__picture_file_name
            self.__picture_file_name = self.__picture_file_name + "_" + str(i)
            self.__take_and_store_picture()
            estimated_number = self.__get_number_of_faces_from_picture()
            print("Estimated number of people: ", estimated_number)
            self.__all_estimations.append(estimated_number)
            self.__picture_names_of_seen_people_amounts[estimated_number] = self.__picture_file_name
            self.__picture_file_name = old_picture_name
            i = i + 1

    def stop_estimation(self):
        self.__should_estimate = False

    def get_picture_path_of_highest_amount_of_seen_people(self):
        return self.__picture_names_of_seen_people_amounts[max(self.__all_estimations)]

    def get_estimated_person_amount(self):
        print("All estimations: ", self.__all_estimations)
        return self.__calculate_mean_of_seen_people_amounts()

    def __calculate_mean_of_seen_people_amounts(self):
        if len(self.__picture_names_of_seen_people_amounts) is 0:
            return 0
        return int(ceil(statistics.mean(self.__picture_names_of_seen_people_amounts)))

    def __take_and_store_picture(self):
        self.__camera = Camera(const.robot)
        self.__camera.configure_camera(self.__camera.cameras["top"], self.__camera.resolutions["640x480"],
                                       self.__camera.formats["jpg"])
        self.__file_transfer = FileTransfer(const.robot)

        remote_folder_path = "/home/nao/recordings/cameras/"
        file_name = self.__picture_file_name + ".jpg"
        self.__camera.camera(remote_folder_path, file_name)
        local_project_path = const.path_to_pictures + file_name
        self.__current_picture_project_path = local_project_path
        remote = remote_folder_path + file_name
        self.__file_transfer.get(remote, local_project_path)

    def __get_number_of_faces_from_picture(self):
        # Create the haar cascade
        face_cascade = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")
        image = cv2.imread(self.__current_picture_project_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        return len(faces)
