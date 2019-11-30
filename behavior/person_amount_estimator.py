import cv2
import statistics as statistics

import const
from robot.object_detection.Camera import Camera
from robot.object_detection.FileTransfer import FileTransfer
from thread import start_new_thread


class PersonAmountEstimator:
    def __init__(self):
        self.should_estimate = True
        self.all_estimations = []

    def start_estimation(self):
        print("start estimating")
        start_new_thread(self.__estimate, ())

    def __estimate(self):
        while self.should_estimate:
            estimated_number = self.__get_number_of_faces_and_store_picture(const.img_people_before_table_search)
            print("Estimated number of people: ", estimated_number)
            self.all_estimations.append(estimated_number)

    def stop_estimation(self):
        self.should_estimate = False

    def get_estimated_person_amount(self):
        print("All estimations: ", self.all_estimations)
        if len(self.all_estimations) is 0:
            return 0
        return round(statistics.mean(self.all_estimations), 0)

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
        face_cascade = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")

        image = cv2.imread(picture_path)
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
