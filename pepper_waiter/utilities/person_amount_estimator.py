import cv2
import time
import const

from thread import start_new_thread

import statistics as statistics

from pepper_waiter.utilities.camera import Camera
from pepper_waiter.utilities.file_transfer import FileTransfer

# import face_recognition


class PersonAmountEstimator:
    def __init__(self):
        self.__should_estimate = True
        self.__taking_pictures = False
        self.__picture_file_name = const.img_people_recognized
        self.__taken_picture_paths_local = []
        self.__taken_picture_paths_remote = []

    def start_estimation(self):
        print("start estimating")
        start_new_thread(self.__estimate, ())

    def __estimate(self):
        self.__taking_pictures = True
        self.__take_and_store_picture(10)
        # while self.__should_estimate:
        #     print(time.time())
        #     self.__take_and_store_picture()
        #     print(time.time())

        self.__taking_pictures = False

    def stop_estimation(self):
        print("stop estimating")
        self.__should_estimate = False

    def get_estimated_person_amount(self):
        self.__get_remote_pictures()
        return self.__calculate_mean_of_seen_people_amounts()

    def __calculate_mean_of_seen_people_amounts(self):
        seen_faces = []
        for pic in self.__taken_picture_paths_local:
            print(pic)
            seen_faces.append(self.__get_number_of_faces_from_picture(pic))

        return int(round(statistics.mean(seen_faces)))

    def __take_and_store_picture(self, amount):
        self.__camera = Camera(const.robot)
        self.__camera.configure_camera(self.__camera.cameras["top"], self.__camera.resolutions["640x480"],
                                       self.__camera.formats["jpg"])
        self.__file_transfer = FileTransfer(const.robot)

        file_names = self.__camera.take_pictures(amount, "/home/nao/recordings/cameras/", 'people_recognized' + str(time.time()) + '.jpg')
        self.__taken_picture_paths_remote += file_names[0]

    def __get_remote_pictures(self):
        while self.__taking_pictures:
            time.sleep(0.2)
        local_file_names = []
        for remote in self.__taken_picture_paths_remote:
            file_name = self.__picture_file_name + str(time.time()) + ".jpg"
            local_project_path = const.path_to_pictures + file_name
            local_file_names.append(local_project_path)
            self.__file_transfer.get(remote, local_project_path)
        self.__taken_picture_paths_local += local_file_names

    def __get_number_of_faces_from_picture(self, picture_path):
        # image = face_recognition.load_image_file(picture_path)
        # faces = face_recognition.face_locations(image)
        # print(len(faces))

        # return len(faces)
        # Create the haar cascade
        face_cascade = cv2.CascadeClassifier("face_detection_data/haarcascade_frontalface_default.xml")
        image = cv2.imread(picture_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        return len(faces)
