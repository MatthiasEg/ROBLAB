from pepper_waiter.utilities.robot.PepperConfiguration import PepperConfiguration
from pepper_waiter.utilities.robot.Robot import Robot

config = PepperConfiguration("Pale")
robot = Robot(config)

min_persons = 1
max_persons = 4

speech_recognition_language = 'English'
speech_recognition_precision = 0.7

people_counting_number_of_retries = 1
people_counting_time = 3

path_to_waiting_music = '/home/nao/recordings/mp3/Wartemusik2.mp3'
path_to_locale_file = 'pepper_waiter/locale/en.json'
path_to_pictures = 'pictures/'
img_people_recognized = 'people_recognized'

max_cups_on_image = 9