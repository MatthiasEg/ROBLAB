from robot.body_movement_wrapper import BodyMovementWrapper
from robot.position_movement_wrapper import PositionMovementWrapper
from robot.sensing_wrapper import SensingWrapper
from robot.speech_wrapper import SpeechWrapper
from tools.PepperConfiguration import PepperConfiguration
from tools.Robot import Robot


def main()
    config = PepperConfiguration("Porter")
    robot = Robot(config)
    body_movement_wrapper = BodyMovementWrapper(robot)
    position_movement_wrapper = PositionMovementWrapper(robot)
    sensing_wrapper = SensingWrapper(robot)
    speech_wrapper = SpeechWrapper(robot)
    body_movement_wrapper.close_left_hand()


if __name__ == '__main__':
    main()
