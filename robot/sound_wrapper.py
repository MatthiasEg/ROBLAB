import const
import time

from threading import Thread

class SoundWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.audio_player_service = self.__robot.session.service("ALAudioPlayer")
        
    def play_sound(self, file_path):
        file_id = self.__robot.ALAudioPlayer.loadFile(file_path)
        self.__robot.ALAudioPlayer.play(file_id)

    def play_sound_for_seconds(self, file_path, seconds):
        t1 = Thread(target = self.play_sound, args = [file_path])
        t1.start()
        time.sleep(seconds)
        self.stop_all()
        t1.join()

    def stop_all(self):
        self.__robot.ALAudioPlayer.stopAll()
