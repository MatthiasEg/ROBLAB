from pepper_waiter.utilities.goal_coordinate import GoalCoordinate


class GoalCoordinatesFoundState:

    def __init__(self, coordinate):
        if isinstance(coordinate, GoalCoordinate):
            self.coordinate = coordinate
        else:
            raise ValueError("Coordinate not valid! [GoalCoordinatesFound]")


class MultipleGoalCoordinatesFoundState:

    def __init__(self, previous_coordinate=None):
        if previous_coordinate is not None:
            if not isinstance(previous_coordinate, GoalCoordinate):
                raise ValueError("Coordinate not valid! [MultipleGoalCoordinatesFound]")
        self.previous_coordinate = previous_coordinate


class GoalCoordinatesNotFoundState:

    def __init__(self, previous_coordinate=None):
        if previous_coordinate is not None:
            if not isinstance(previous_coordinate, GoalCoordinate):
                raise ValueError("Coordinate not valid! [GoalCoordinatesNotFound]")
        self.previous_coordinate = previous_coordinate
