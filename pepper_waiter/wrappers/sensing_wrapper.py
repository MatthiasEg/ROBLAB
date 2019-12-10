from pandas import Series

import const
from pepper_waiter.utilities.camera import Camera
from pepper_waiter.utilities.file_transfer import FileTransfer
from pepper_waiter.utilities.object_detection.object_detection import ObjectDetector
from pepper_waiter.table_goal_position_state import GoalTableNotFound, GoalTableFound, MultipleTableGoalsFound


class SensingWrapper:
    __MAX_IMAGE_WIDTH = 640.0

    def __init__(self):
        self.__robot = const.robot
        self.__camera = Camera(self.__robot)
        self.__camera.configure_camera(self.__camera.cameras["top"], self.__camera.resolutions["640x480"],
                                       self.__camera.formats["jpg"])
        self.__file_transfer = FileTransfer(const.robot)
        self.__detection = ObjectDetector()
        self.__frontSonarMemoryPath = "Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value"
        self.__backSonarMemoryPath = "Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value"
        self.start_sonar_sensors()

        self.__previous_table_goal = None

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

    def get_object_positions(self, object_name):
        image_path = "object_detection.jpg"
        self.__take_picture(image_path)

        return self.__detection.get_object_positions(image_path, object_name, 0.4)

    def get_starting_red_cup_position(self):
        image_path = "start_cup_detection.jpg"
        self.__take_picture(image_path)

        keypoints = self.__detection.get_red_cup_keypoints(image_path)
        center_goals = GoalTableNotFound()
        if len(keypoints) == 1:
            return GoalTableFound((keypoints[0]["x"], keypoints[0]["y"]))
        return center_goals

    def get_red_cups_center_position(self, cup_goal):
        image_path = "cup_detection.jpg"
        self.__take_picture(image_path)

        keypoints = self.__detection.get_red_cup_keypoints(image_path)
        center_goals = GoalTableNotFound(self.__previous_table_goal)
        if cup_goal == 1:
            cup_goal = 2
        if len(keypoints) > 0:
            center_goals = self.__get_cup_group_center_position(cup_goal, keypoints)

        return center_goals

    def __get_cup_group_center_position(self, cup_goal, keypoints):
        cup_goal = int(cup_goal)
        keypoints.sort(key=lambda x: x["x"])
        sizes = map(lambda r: r["size"], keypoints)

        keypoint_sizes = Series(sizes)
        keypoint_sizes.sort_values(ascending=True)
        if len(keypoint_sizes) < cup_goal:
            return GoalTableNotFound(self.__previous_table_goal)
        elif len(keypoint_sizes) is cup_goal:
            center = self.__calculate_centers(keypoint_sizes, keypoints)
            if center is not None:
                return GoalTableFound((center["x"], center["y"]))
            return GoalTableNotFound(self.__previous_table_goal)
        elif len(keypoint_sizes) <= const.max_cups_on_image:
            current_index = 0
            center_goals = []
            while current_index <= (len(keypoint_sizes) - cup_goal):
                goal_series, goal_keypoints = self.__build_goal_params(cup_goal, keypoint_sizes, keypoints,
                                                                       current_index)
                center_goal = self.__calculate_centers(goal_series, goal_keypoints)
                if center_goal is not None:
                    center_goals.append(center_goal)
                current_index = current_index + 1

            return self.__filter_goal_positions(center_goals)
        return GoalTableNotFound(self.__previous_table_goal)

    @staticmethod
    def __build_goal_params(cup_goal, keypoint_sizes, keypoints, current_index):
        goal_keypoints = []
        goal_sizes = []
        for x in range(cup_goal):
            goal_sizes.append(keypoint_sizes[current_index + x])
            goal_keypoints.append(keypoints[current_index + x])
        goal_series = Series(goal_sizes)

        return goal_series, goal_keypoints

    def __calculate_centers(self, keypoint_sizes, keypoints):
        if keypoint_sizes.std() < 2.5:
            x_values = map(lambda r: r["x"], keypoints)
            x_min = float(min(x_values))
            x_max = float(max(x_values))
            size_mean = keypoint_sizes.mean()
            if ((x_max * size_mean) - (x_min * size_mean)) <= 100 * size_mean:
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

    @staticmethod
    def __calculate_axis_center(centers):
        center_min = min(centers)
        center_max = max(centers)
        distance_between_x = center_max - center_min
        return center_max - (distance_between_x / 2)

    def __filter_goal_positions(self, center_goals):
        indexes_to_remove = set()
        for i in range(len(center_goals)):
            if i < len(center_goals) - 1:
                if (center_goals[i + 1]["x"] - center_goals[i]["x"]) <= 100:
                    indexes_to_remove.add(i)
                    indexes_to_remove.add(i + 1)

        real_goal_positions = center_goals[:]
        for num, goal in enumerate(center_goals):
            if num in indexes_to_remove:
                real_goal_positions.remove(goal)

        if len(real_goal_positions) == 1:
            self.__previous_table_goal = real_goal_positions[0]
            goal_coordinates = (real_goal_positions[0]["x"], real_goal_positions[0]["y"])
            return GoalTableFound(goal_coordinates)
        elif len(real_goal_positions) >= 1:
            if self.__previous_table_goal is not None:
                filtered_goal = self.__get_coordinates_closest_to_previous(real_goal_positions)
                if filtered_goal is not None:
                    return GoalTableFound((filtered_goal["x"], filtered_goal["y"]))
            return MultipleTableGoalsFound(self.__previous_table_goal)
        return GoalTableNotFound(self.__previous_table_goal)

    def __get_coordinates_closest_to_previous(self, goal_positions):
        min_threshold = self.__previous_table_goal["x"] - 100
        max_threshold = self.__previous_table_goal["x"] + 100
        for _, goal in enumerate(goal_positions):
            if min_threshold <= goal["x"] <= max_threshold:
                return goal
        return None

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

    def __take_picture(self, file_name):
        remote_folder_path = "/home/nao/recordings/cameras/"
        self.__camera.camera(remote_folder_path, file_name)
        local = file_name
        remote = remote_folder_path + file_name

        self.__file_transfer.get(remote, local)

    def __del__(self):
        try:
            self.__file_transfer.close()
        except Exception, ex:
            print(ex)

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

    def get_robot_position_in_map(self):
        return self.__robot.ALNavigation.getRobotPositionInMap()


