class GoalTableFound:

    def __init__(self, goal_location):
        self.goal_location = goal_location


class MultipleTableGoalsFound:

    def __init__(self, previous_goal_location=None):
        self.previous_goal_location = previous_goal_location


class GoalTableNotFound:

    def __init__(self, previous_goal_location=None):
        self.previous_goal_location = previous_goal_location
