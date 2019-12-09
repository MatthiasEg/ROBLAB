import const
from behavior.behavior import Behavior


def main():
    try:
        Behavior().start_behavior()
    except Exception, e:
        robot = const.robot
        Behavior().body_movement_wrapper.enable_autonomous_life(False)
        print(e.message)
        return


if __name__ == '__main__':
    main()
