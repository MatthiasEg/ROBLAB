import const
from behavior.behavior import Behavior


def main():
    try:
        behavior = Behavior()
        behavior.start_behavior()
    except Exception, e:
        behavior.body_movement_wrapper.enable_autonomous_life(False)
        behavior.sound_wrapper.stop_all()
        print(e.message)
        return


if __name__ == '__main__':
    main()
