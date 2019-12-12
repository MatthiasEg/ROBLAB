import time

import const
from pepper_waiter.utilities.goal_coordinate import GoalCoordinate
from pepper_waiter.utilities.navigation.coordinate_calculator import CoordinateCalculator
from pepper_waiter.utilities.table_goal_position_state import GoalCoordinatesFoundState
from pepper_waiter.utilities.table_search_state import TableStateError, TableOccupied, TableFound, TableNotFound


class Navigator:

    def __init__(self, body_movement, position_movement, sensing, speech, sentences):
        self.__coordinate_calculator = CoordinateCalculator()
        self.__body_movement_wrapper = body_movement
        self.__position_movement_wrapper = position_movement
        self.__sensing_wrapper = sensing
        self.__speech_wrapper = speech
        self.__sentences = sentences
        self.__amount_of_persons = 0
        self.__navigation_interrupted = False
        self.navigation_successful = False

    def search_table(self, amount_of_persons):
        self.__amount_of_persons = amount_of_persons
        self.__prepare_to_move()

        try:
            while not self.__navigation_interrupted:
                goal_state = self.__coordinate_calculator.get_table_coordinate_state(self.__amount_of_persons)
                if isinstance(goal_state, GoalCoordinatesFoundState):
                    table_occupied = self.__is_table_occupied(goal_state.coordinate)
                    if table_occupied:
                        if self.__amount_of_persons < const.max_persons:
                            self.__amount_of_persons += 1
                        else:
                            self.__amount_of_persons = 0
                            self.__navigation_interrupted = True
                            return TableOccupied()
                    else:
                        return TableFound()
                else:
                    self.__speech_wrapper.say(self.__sentences["moreTimeToSearch"])
                    table_coord_func = self.__coordinate_calculator.get_table_coordinate_state
                    if self.__retry_to_locate_table(goal_state.previous_coordinate,
                                                    table_coord_func,
                                                    self.__amount_of_persons) is not True:
                        if self.__amount_of_persons < const.max_persons:
                            self.__amount_of_persons += 1
                        else:
                            self.__navigation_interrupted = True
                            self.__amount_of_persons = 0
                            return TableNotFound()
        except Exception, e:
            self.__position_movement_wrapper.stop_movement()
            self.__navigation_interrupted = True
            self.__amount_of_persons = 0
            print(e)
            return TableStateError()

    def __is_table_occupied(self, goal_coordinate):
        detected_person_coordinates = self.__coordinate_calculator.get_object_positions("person")
        if len(detected_person_coordinates) > 0:
            person_x_positions = map(lambda r: r["centerX"], detected_person_coordinates)
            goal_x = goal_coordinate.x
            range_min = goal_x - 100 if goal_x - 100 >= 0 else 0
            range_max = goal_x + 100 if goal_x + 100 <= 640 else 640
            for x_coord in person_x_positions:
                if range_min <= x_coord <= range_max:
                    return True
        return False

    def navigate_to_table(self):
        if self.__amount_of_persons is 0:
            raise ValueError("Amount of persons cannot be 0")
        table_coord_func = self.__coordinate_calculator.get_table_coordinate_state
        self.__do_navigation(table_coord_func, self.__amount_of_persons)

    def navigate_to_waiting_area(self):
        waiting_area_coord_func = self.__coordinate_calculator.get_waiting_area_coordinates
        self.__do_navigation(waiting_area_coord_func)

    def __do_navigation(self, goal_state_func, *args):
        self.__navigation_interrupted = False
        self.navigation_successful = False
        self.__prepare_to_move()
        try:
            not_found_tries = 0
            while not self.__navigation_interrupted:
                distance_meters = self.__sensing_wrapper.get_sonar_distance("Front")
                if float(distance_meters) >= 1.8:
                    not_found_tries = self.__move_by_goal_state(not_found_tries, goal_state_func, *args)
                else:
                    if float(distance_meters) >= 0.8:
                        self.__position_movement_wrapper.move(0.5, 0, 0)
                    else:
                        self.__position_movement_wrapper.stop_movement()
                        self.navigation_successful = True
                        self.__navigation_interrupted = True
                        print("movement finished")
        except Exception, ex:
            self.__position_movement_wrapper.stop_movement()
            self.__navigation_interrupted = True
            print(ex)

    def __move_by_goal_state(self, not_found_tries, goal_state_func, *args):
        goal_state = goal_state_func(*args)
        if isinstance(goal_state, GoalCoordinatesFoundState):
            goal_location = goal_state.coordinate
            self.__move_towards_goal_location(goal_location)
            return 0
        else:
            if not_found_tries < 6:
                print("not found tries: %s" % not_found_tries)
                return not_found_tries + 1
            else:
                self.__position_movement_wrapper.stop_movement()
                self.__body_movement_wrapper.initial_position()
                if self.__retry_to_locate_table(goal_state.previous_coordinate, goal_state_func, *args) is not True:
                    self.__navigation_interrupted = True
                return 0

    def __move_towards_goal_location(self, goal_coordinate):
        pixels_to_move_x = (640 / 2) - goal_coordinate.x
        degrees_to_move_x = int(round(pixels_to_move_x / 15.0))
        print("table goal position: %s, move_x: %s" % (goal_coordinate.x, degrees_to_move_x))
        self.__position_movement_wrapper.move(0.5, 0, degrees_to_move_x)

    def __retry_to_locate_table(self, previous_coordinate, goal_state_func, *args):
        if previous_coordinate is not None:
            if not isinstance(previous_coordinate, GoalCoordinate):
                raise ValueError("Coordinate not valid! [__retry_to_locate_table]")

        self.__position_movement_wrapper.stop_movement()
        self.__prepare_to_move()

        direction_multiplier = -1  # left
        if previous_coordinate is not None:
            print("previous goal x: %s" % previous_coordinate.x)
            if previous_coordinate.x >= (640 / 2):
                direction_multiplier = 1  # right

        degrees_per_step = 30
        max_turns = int(round(360 / degrees_per_step))
        number_of_turns = 0

        while number_of_turns < max_turns:
            goal_state = goal_state_func(*args)
            if not isinstance(goal_state, GoalCoordinatesFoundState):
                self.__position_movement_wrapper.move_to(0, 0, degrees_per_step * direction_multiplier)
                time.sleep(.5)
                number_of_turns = number_of_turns + 1
            else:
                return True
        return False

    def __prepare_to_move(self):
        self.__body_movement_wrapper.enable_autonomous_life(False)
        self.__body_movement_wrapper.set_head_left(0)
        self.__body_movement_wrapper.set_head_up(0)
        self.__body_movement_wrapper.set_hip_pitch(-5)
        self.__body_movement_wrapper.set_hip_roll(0)
        time.sleep(3)
