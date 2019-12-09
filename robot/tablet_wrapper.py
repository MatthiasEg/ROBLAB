import const
import time

class TabletWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.tabletService = self.__robot.session.service("ALTabletService")

    def showImage(self, path_or_url, duration=3):
        print(path_or_url)
        try:
            # self.tabletService.image_show_local("http://192.168.1.102/dinner_for_one/html/img/demo.jpg")
            self.tabletService.showImage("http://192.168.1.102/opt/aldebaran/var/www/apps/dinner_for_one/html/img/demo.jpg")
            time.sleep(10)
            self.tabletService.hideImage()
        except Exception, e:
            print "Error was: ", e