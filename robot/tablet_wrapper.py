import const
import time

class TabletWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.tabletService = self.__robot.session.service("ALTabletService")

    def showImage(self, path_or_url, duration=3):
        print(path_or_url)
        try:
            self.tabletService.showImage("http://192.168.1.101/img/people_recognized_1.jpg")
            time.sleep(duration)
            self.tabletService.hideImage()
        except Exception, e:
            print "Error was: ", e