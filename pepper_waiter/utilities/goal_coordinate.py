class GoalCoordinate:

    def __init__(self, x, y):
        if x is None or y is None:
            raise ValueError("x or y cannot be None! [GoalCoordinate]")
        self.x = x
        self.y = y
