from robot.object_detection.Camera import Camera
from robot.object_detection.FileTransfer import FileTransfer
from robot.object_detection.object_detection import ObjectDetection


import const


class SensingWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.__detection = ObjectDetection()

    def explore(self, radius):
        return self.__robot.ALNavigation.explore(radius)

    def save_exploration_to_robot(self):
        return self.__robot.ALNavigation.saveExploration()

    def start_localization(self):
        return self.__robot.ALNavigation.startLocalization()

    def stop_localization(self):
        return self.__robot.ALNavigation.stopLocalization()

    def get_metrical_map(self):
        return self.__robot.ALNavigation.getMetricalMap()
        self.__robot = robot

    def detectObjects(self):
        remote_folder_path = "/home/nao/recordings/cameras/"
        file_name = "picture.jpg"

        camera = Camera(self.__robot)
        camera.configure_camera(camera.cameras["top"], camera.resolutions["640x480"], camera.formats["jpg"])

        camera.take_picture(remote_folder_path, file_name)

        # copy file to local path
        local = file_name
        remote = remote_folder_path + file_name
        file_transfer = FileTransfer(self.__robot)
        file_transfer.get(remote, local)
        file_transfer.close()

        self.__detection.analyze(file_name)
