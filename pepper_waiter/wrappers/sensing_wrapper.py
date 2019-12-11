import const
from pepper_waiter.utilities.navigation.coordinate_calculator import CoordinateCalculator


class SensingWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.__frontSonarMemoryPath = "Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value"
        self.__backSonarMemoryPath = "Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value"
        self.start_sonar_sensors()

    def is_face_detection_enabled(self):
        return self.__robot.ALPeoplePerception.isFaceDetectionEnabled()

    def is_face_recognition_enabled(self):
        return self.__robot.ALPeoplePerception.isRe()

    def reset_population(self):
        return self.__robot.ALPeoplePerception.resetPopulation()

    def set_maximum_detection_range_in_meters(self, range):
        return self.__robot.ALPeoplePerception.setMaximumDetectionRange(range)

    def start_face_detection(self, name):
        return self.__robot.ALFaceDetection.subscribe2(name)

    def stop_face_detection(self, name):
        return self.__robot.ALFaceDetection.unsubscribe(name)

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

    def start_sonar_sensors(self):
        # subscriber name, refresh period( in milliseconds), precision of the extractor
        self.__robot.ALSonar.subscribe("Pepper", 1000, .1)

    def stop_sonar_sensors(self):
        self.__robot.ALSonar.unsubscribe("Pepper")

    def get_sonar_distance(self, sonar):
        if sonar is "Front":
            al_memory_path = self.__frontSonarMemoryPath
        elif sonar is "Back":
            al_memory_path = self.__backSonarMemoryPath
        else:
            raise Exception("Invalid sonar sensor parameter!")

        return self.__robot.ALMemory.getData(al_memory_path)

