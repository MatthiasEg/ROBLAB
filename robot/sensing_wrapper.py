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

    def is_face_detection_enabled(self):
        return self.__robot.ALPeoplePerception.isFaceDetectionEnabled()

    def is_face_recognition_enabled(self):
        return self.__robot.ALPeoplePerception.isRe()

    def reset_population(self):
        return self.__robot.ALPeoplePerception.resetPopulation()

    def set_maximum_detection_range_in_meters(self, range):
        return self.__robot.ALPeoplePerception.setMaximumDetectionRange(range)

    def subscribe(self, name):
        return self.__robot.ALFaceDetection.subscribe2(name)

    def unsubscribe(self, name):
        return self.__robot.ALFaceDetection.unsubscribe(name)

    def get_robot_position_in_map(self):
        return self.__robot.ALNavigation.getRobotPositionInMap()

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

    def enable_face_tracking(self):
        self.__robot.ALFaceDetection.setTrackingEnabled(True)

    def disable_face_tracking(self):
        self.__robot.ALFaceDetection.setTrackingEnabled(False)

    def enable_face_recognition(self):
        self.__robot.ALFaceDetection.setRecognitionEnabled(True)

    def get_memory_subscriber(self, event):
        return self.__robot.ALFaceDetection.getMemorySubscriber(event)

    def enable_fast_mode(self):
        return self.__robot.ALPeoplePerception.setFastModeEnabled(True)

    def start_Face_Tracking(self, faceSize):
        targetName = "Face"
        faceWidth = faceSize
        self.__robot.ALTracker.registerTarget(targetName, faceWidth)
        self.__robot.ALTracker.track(targetName)

    def stop_Face_Tracking(self):
        self.__robot.ALTracker.stopTracker()
        self.__robot.ALTracker.unregisterAllTargets()
        self.__robot.ALMotion.rest()
