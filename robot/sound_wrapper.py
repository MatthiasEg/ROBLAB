import const
import time

from threading import Thread

class SoundWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.audio_player_service = self.__robot.session.service("ALAudioPlayer")
        self.t1 = None

    def play_sound(self, file_path):
        file_id = self.__robot.ALAudioPlayer.loadFile(file_path)
        self.__robot.ALAudioPlayer.play(file_id)

    def start_playing_sound(self, file_path):
        self.t1 = Thread(target = self.play_sound, args = [file_path])
        self.t1.start()

    def stop_all(self):
        self.__robot.ALAudioPlayer.stopAll()
        self.t1.join()
