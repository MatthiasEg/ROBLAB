import const


class SoundWrapper:

    def __init__(self):
        self.__robot = const.robot
        self.audio_player_service = self.__robot.session.service("ALAudioPlayer")
        
    def play_sound(self, file_path):
        file_id = self.__robot.ALAudioPlayer.loadFile(file_path)
        self.__robot.ALAudioPlayer.play(file_id)

    def stop_all(self):
        self.__robot.ALAudioPlayer.stopAll()
