from robot.object_detection.Camera import Camera
from robot.object_detection.FileTransfer import FileTransfer
from robot.object_detection.object_detection import ObjectDetection


import const


class SensingWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.__detection = ObjectDetection()
        self.__frontSonarMemoryPath = "Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value"
        self.__backSonarMemoryPath = "Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value"

    def explore(self, radius):
        return self.__robot.ALNavigation.explore(radius)

    def save_exploration_to_robot(self):
        return self.__robot.ALNavigation.saveExploration()

    def load_exploration_from_robot(self, path):
        return self.__robot.ALNavigation.loadExploration(path)

    def start_localization(self):
        return self.__robot.ALNavigation.startLocalization()

    def stop_localization(self):
        return self.__robot.ALNavigation.stopLocalization()

    def get_metrical_map(self):
        return self.__robot.ALNavigation.getMetricalMap()

    def detect_object(self, object_name):
        remote_folder_path = "/home/nao/recordings/cameras/"
        file_name = "picture.jpg"

        camera = Camera(self.__robot)
        camera.configure_camera(camera.cameras["top"], camera.resolutions["640x480"], camera.formats["jpg"])

        camera.take_picture(remote_folder_path, file_name)

        # copy file to local path
        local = file_name
        remote = remote_folder_path + file_name
        file_transfer = FileTransfer(self.__robot)
        file_transfer.get(remote, local)
        file_transfer.close()

        return self.__detection.analyze(file_name, object_name, 0.4)

    def start_sonar_sensors(self):
        # subscriber name, refresh period( in milliseconds), precision of the extractor
        self.__robot.ALSonar.subscribe(self.__robot.configuration.name, 1000, .1)

    def stop_sonar_sensors(self):
        self.__robot.ALSonar.unsubscribe(self.__robot.configuration.name)

    def get_sonar_distance(self, sonar):
        al_memory_path = ""
        if sonar is "Front":
            al_memory_path = self.__frontSonarMemoryPath
        elif sonar is "Back":
            al_memory_path = self.__backSonarMemoryPath
        else:
            raise Exception("Invalid sonar sensor parameter!")

        return self.__robot.ALMemory.getData(al_memory_path)

