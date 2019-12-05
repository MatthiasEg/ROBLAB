from tools.PepperConfiguration import PepperConfiguration
from tools.Robot import Robot

config = PepperConfiguration("Amber")
robot = Robot(config)

min_persons = 2
max_persons = 4

speech_recognition_language = 'German'
speech_recognition_precision = 0.7

people_counting_number_of_retries = 3
people_counting_time = 5

path_to_locale_file = 'locale/de-ch.json'
path_to_pictures = 'pictures/'
img_people_recognized = 'people_recognized'