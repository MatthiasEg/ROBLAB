from behavior.behavior import Behavior


def main():
    behavior = Behavior()

    try:
        behavior.start_behavior()
    except Exception, e:
        behavior.body_movement_wrapper.enable_autonomous_life(False)
        print(e)
        return


if __name__ == '__main__':
    main()
