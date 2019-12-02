from robot.object_detection.Camera import Camera
from robot.object_detection.FileTransfer import FileTransfer
from robot.object_detection.object_detection import ObjectDetection
from pandas import Series

import const


class SensingWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.__detection = ObjectDetection()
        self.__frontSonarMemoryPath = "Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value"
        self.__backSonarMemoryPath = "Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value"

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

    def start_face_tracking(self, faceSize):
        targetName = "Face"
        faceWidth = faceSize
        self.__robot.ALTracker.registerTarget(targetName, faceWidth)
        self.__robot.ALTracker.track(targetName)

    def stop_face_tracking(self):
        self.__robot.ALTracker.stopTracker()
        self.__robot.ALTracker.unregisterAllTargets()
        self.__robot.ALMotion.rest()

    def detect_object(self, object_name):
        remote_folder_path = "/home/nao/recordings/cameras/"
        file_name = "object_detection.jpg"

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

    MAX_CUPS_ON_IMAGE = 9.0
    MAX_IMAGE_WIDTH = 640.0

    def get_cup_goal_centers(self, cup_goal):
        keypoints = self.__detection.get_red_cup_keypoints()
        center_goals = None
        if len(keypoints) > 0:
            center_goals = self.__get_cup_group_center(cup_goal, keypoints)

        return center_goals

    def __get_cup_group_center(self, cup_goal, keypoints):
        cup_goal = int(cup_goal)
        keypoints.sort(key=lambda x: x["x"])
        sizes = map(lambda r: r["size"], keypoints)

        keypoint_sizes = Series(sizes)
        keypoint_sizes.sort_values(ascending=True)
        if len(keypoint_sizes) < cup_goal:
            return None
        elif len(keypoint_sizes) is cup_goal:
            center = self.__get_centers(keypoint_sizes, keypoints)
            if center is not None:
                return center["x"], center["y"]
            return None
        elif len(keypoint_sizes) <= self.MAX_CUPS_ON_IMAGE:
            current_index = 0
            center_goals = []
            while current_index <= (len(keypoint_sizes) - cup_goal):
                goal_series, goal_keypoints = self.__get_stuff(cup_goal, keypoint_sizes, keypoints, current_index)
                center_goal = self.__get_centers(goal_series, goal_keypoints)
                if center_goal is not None:
                    center_goals.append(center_goal)
                current_index = current_index + 1

            return self.__fucking(center_goals)
        return None

    def __fucking(self, center_goals):
        indexes_to_remove = set()
        for i in range(len(center_goals)):
            if i < len(center_goals) - 1:
                if (center_goals[i + 1]["x"] - center_goals[i]["x"]) <= 100:
                    indexes_to_remove.add(i)
                    indexes_to_remove.add(i + 1)

        bla = center_goals[:]
        for num, name in enumerate(center_goals):
            if num in indexes_to_remove:
                bla.remove(name)

        if len(bla) is 1:
            return bla[0]["x"], bla[0]["y"]
        return None

    def __get_stuff(self, cup_goal, keypoint_sizes, keypoints, current_index):
        goal_keypoints = []
        goal_sizes = []
        for x in range(cup_goal):
            goal_sizes.append(keypoint_sizes[current_index + x])
            goal_keypoints.append(keypoints[current_index + x])
        goal_series = Series(goal_sizes)

        return goal_series, goal_keypoints

    def __get_centers(self, keypoint_sizes, keypoints):
        if keypoint_sizes.std() < 2.5:
            x_values = map(lambda r: r["x"], keypoints)
            x_min = float(min(x_values))
            x_max = float(max(x_values))
            # if ((x_max / self.MAX_IMAGE_WIDTH) - (x_min / self.MAX_IMAGE_WIDTH)) <= 0.5:
            size_mean = keypoint_sizes.mean()
            if ((x_max * size_mean) - (x_min * size_mean)) <= 1500:
                y_values = map(lambda r: r["y"], keypoints)
                center_y = self.__calculate_axis_center(y_values)
                center_x = self.__calculate_axis_center(x_values)

                result = dict()
                result["x"] = center_x
                result["y"] = center_y
                result["size"] = size_mean
                return result
        else:
            return None

    def __calculate_axis_center(self, centers):
        center_min = min(centers)
        center_max = max(centers)
        distance_between_x = center_max - center_min
        return center_max - (distance_between_x / 2)

    def start_sonar_sensors(self):
        # subscriber name, refresh period( in milliseconds), precision of the extractor
        self.__robot.ALSonar.subscribe("Pepper", 1000, .1)

    def stop_sonar_sensors(self):
        self.__robot.ALSonar.unsubscribe("Pepper")

    def get_sonar_distance(self, sonar):
        al_memory_path = ""
        if sonar is "Front":
            al_memory_path = self.__frontSonarMemoryPath
        elif sonar is "Back":
            al_memory_path = self.__backSonarMemoryPath
        else:
            raise Exception("Invalid sonar sensor parameter!")

        return self.__robot.ALMemory.getData(al_memory_path)



