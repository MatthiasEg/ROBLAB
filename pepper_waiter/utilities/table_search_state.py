from pepper_waiter.utilities.goal_coordinate import GoalCoordinate


class TableFound:

    def __init__(self, coordinate):
        if isinstance(coordinate, GoalCoordinate):
            self.coordinate = coordinate
        else:
            raise ValueError("Coordinate not valid! [GoalCoordinatesFound]")


class TableOccupied:

    def __init__(self):
        pass


class TableNotFound:

    def __init__(self):
        pass


class TableStateError:

    def __init__(self):
        pass
