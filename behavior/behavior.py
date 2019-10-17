import const
import main
from robot.body_movement_wrapper import BodyMovementWrapper
from robot.position_movement_wrapper import PositionMovementWrapper
from robot.sensing_wrapper import SensingWrapper
from robot.speech_wrapper import SpeechWrapper


class Behavior:

    def __init__(self):
        self.robot = const.robot

    def start_behavior(self):
        body_movement_wrapper = BodyMovementWrapper(self._robot)
        position_movement_wrapper = PositionMovementWrapper(self._robot)
        sensing_wrapper = SensingWrapper(self._robot)
        speech_wrapper = SpeechWrapper(self._robot)
        speech_wrapper.say("Hello")
