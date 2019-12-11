from pandas import Series

import const
from pepper_waiter.utilities.camera import Camera
from pepper_waiter.utilities.file_transfer import FileTransfer
from pepper_waiter.utilities.goal_coordinate import GoalCoordinate
from pepper_waiter.utilities.object_detection.object_detection import ObjectDetector
from pepper_waiter.utilities.table_goal_position_state import GoalCoordinatesNotFoundState, GoalCoordinatesFoundState, \
    MultipleGoalCoordinatesFoundState


class CoordinateCalculator:

    def __init__(self):
        self.__robot = const.robot
        self.__camera = Camera(self.__robot)
        self.__camera.configure_camera(self.__camera.cameras["top"], self.__camera.resolutions["640x480"],
                                       self.__camera.formats["jpg"])
        self.__file_transfer = FileTransfer(const.robot)
        self.__detection = ObjectDetector()
        self.__previous_goal_coordinate = None

    def get_object_positions(self, object_name):
        image_path = "object_detection.jpg"
        self.__take_picture(image_path)

        return self.__detection.get_object_positions(image_path, object_name, 0.4)

    def get_waiting_area_coordinates(self):
        image_path = "start_cup_detection.jpg"
        self.__take_picture(image_path)

        cup_key_points = self.__detection.get_red_cup_keypoints(image_path)
        goal_state = GoalCoordinatesNotFoundState()
        if len(cup_key_points) == 1:
            return GoalCoordinatesFoundState(GoalCoordinate(cup_key_points[0]["x"], cup_key_points[0]["y"]))
        return goal_state

    def get_table_coordinate_state(self, cup_goal):
        image_path = "cup_detection.jpg"
        self.__take_picture(image_path)

        cup_key_points = self.__detection.get_red_cup_keypoints(image_path)
        goal_state = GoalCoordinatesNotFoundState(self.__previous_goal_coordinate)

        cup_goal = int(cup_goal)
        if cup_goal == 1:
            cup_goal = 2
        if len(cup_key_points) > 0:
            goal_state = self.__get_cup_group_center_coordinates(cup_goal, cup_key_points)

        return goal_state

    def __get_cup_group_center_coordinates(self, cup_goal, cup_key_points):
        cup_key_points.sort(key=lambda x: x["x"])
        key_point_size_values = map(lambda r: r["size"], cup_key_points)

        key_point_sizes = Series(key_point_size_values)
        key_point_sizes.sort_values(ascending=True)

        if len(key_point_sizes) < cup_goal:
            return GoalCoordinatesNotFoundState(self.__previous_goal_coordinate)

        elif len(key_point_sizes) is cup_goal:
            return self.__get_state_for_key_point_size_match(key_point_sizes, cup_key_points)

        elif len(key_point_sizes) <= const.max_cups_on_image:
            return self.__get_state_for_larger_key_point_size(cup_goal, key_point_sizes, cup_key_points)

        return GoalCoordinatesNotFoundState(self.__previous_goal_coordinate)

    def __get_state_for_key_point_size_match(self, key_point_sizes, cup_key_points):
        center_coordinate = self.__calculate_center_coordinate(key_point_sizes, cup_key_points)
        if center_coordinate is not None:
            return GoalCoordinatesFoundState(GoalCoordinate(center_coordinate["x"], center_coordinate["y"]))
        return GoalCoordinatesNotFoundState(self.__previous_goal_coordinate)

    def __get_state_for_larger_key_point_size(self, cup_goal, key_point_sizes, cup_key_points):
        current_index = 0
        center_coordinates = []
        while current_index <= (len(key_point_sizes) - cup_goal):
            goal_key_point_sizes, goal_key_points = self.__build_goal_params(cup_goal,
                                                                             key_point_sizes,
                                                                             cup_key_points,
                                                                             current_index)
            center_coordinate = self.__calculate_center_coordinate(goal_key_point_sizes, goal_key_points)
            if center_coordinate is not None:
                center_coordinates.append(center_coordinate)
            current_index = current_index + 1

        return self.__filter_goal_coordinate(center_coordinates)

    @staticmethod
    def __build_goal_params(cup_goal, key_point_sizes, cup_key_points, current_index):
        goal_key_points = []
        goal_key_point_sizes = []

        for x in range(cup_goal):
            goal_key_point_sizes.append(key_point_sizes[current_index + x])
            goal_key_points.append(cup_key_points[current_index + x])
        goal_series = Series(goal_key_point_sizes)

        return goal_series, goal_key_points

    def __calculate_center_coordinate(self, goal_key_point_sizes, goal_key_points):
        if goal_key_point_sizes.std() < 2.5:
            x_values = map(lambda r: r["x"], goal_key_points)
            x_min = float(min(x_values))
            x_max = float(max(x_values))
            size_mean = goal_key_point_sizes.mean()
            if ((x_max * size_mean) - (x_min * size_mean)) <= 100 * size_mean:
                y_values = map(lambda r: r["y"], goal_key_points)
                center_y = self.__calculate_axis_center(y_values)
                center_x = self.__calculate_axis_center(x_values)

                goal_coordinates = dict()
                goal_coordinates["x"] = center_x
                goal_coordinates["y"] = center_y
                return goal_coordinates
        else:
            return None

    @staticmethod
    def __calculate_axis_center(centers):
        center_min = min(centers)
        center_max = max(centers)
        distance_between_x = center_max - center_min
        return center_max - (distance_between_x / 2)

    def __filter_goal_coordinate(self, goal_coordinates):
        indexes_to_remove = self.__get_indexes_to_remove(goal_coordinates)
        filtered_goal_coordinates = self.__get_filtered_coordinates(goal_coordinates, indexes_to_remove)

        if len(filtered_goal_coordinates) == 1:
            goal_coordinate = GoalCoordinate(filtered_goal_coordinates[0]["x"], filtered_goal_coordinates[0]["y"])
            self.__set_previous_goal_coordinate(goal_coordinate)
            return GoalCoordinatesFoundState(goal_coordinate)

        elif len(filtered_goal_coordinates) >= 1:
            if self.__previous_goal_coordinate is not None:
                filtered_goal = self.__get_coordinates_closest_to_previous(filtered_goal_coordinates)
                if filtered_goal is not None:
                    return GoalCoordinatesFoundState(GoalCoordinate(filtered_goal["x"], filtered_goal["y"]))
            return MultipleGoalCoordinatesFoundState(self.__previous_goal_coordinate)

        return GoalCoordinatesNotFoundState(self.__previous_goal_coordinate)

    @staticmethod
    def __get_indexes_to_remove(center_goals):
        indexes_to_remove = set()
        for i in range(len(center_goals)):
            if i < len(center_goals) - 1:
                if (center_goals[i + 1]["x"] - center_goals[i]["x"]) <= 100:
                    indexes_to_remove.add(i)
                    indexes_to_remove.add(i + 1)
        return indexes_to_remove

    @staticmethod
    def __get_filtered_coordinates(goal_coordinates, indexes_to_remove):
        filtered_goal_coordinates = goal_coordinates[:]
        for num, goal in enumerate(goal_coordinates):
            if num in indexes_to_remove:
                filtered_goal_coordinates.remove(goal)

        return filtered_goal_coordinates

    def __set_previous_goal_coordinate(self, coordinate):
        if not isinstance(coordinate, GoalCoordinate):
            raise ValueError("Coordinate not valid! [__set_previous_goal_coordinate]")
        self.__previous_goal_coordinate = coordinate

    def __get_coordinates_closest_to_previous(self, goal_coordinates):
        min_threshold = self.__previous_goal_coordinate.x - 50
        max_threshold = self.__previous_goal_coordinate.x + 50
        for _, goal in enumerate(goal_coordinates):
            if min_threshold <= goal["x"] <= max_threshold:
                return goal
        return None

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
            print("%s: [CoordinateCalculator __del__]" % ex)
