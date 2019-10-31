from robot.object_detection.Camera import Camera
from robot.object_detection.FileTransfer import FileTransfer
from robot.object_detection.object_detection import ObjectDetection


class SensingWrapper:

    def __init__(self, robot):
        self.__robot = robot
        self.__detection = ObjectDetection()

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
