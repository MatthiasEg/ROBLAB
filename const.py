from tools.PepperConfiguration import PepperConfiguration
from tools.Robot import Robot

config = PepperConfiguration("Pale")
robot = Robot(config)

min_persons = 1
max_persons = 4

speech_recognition_language = 'English'
speech_recognition_precision = 0.7

people_counting_number_of_retries = 2
people_counting_time = 5

path_to_locale_file = 'locale/en.json'
path_to_pictures = 'pictures/'
img_people_recognized = 'people_recognized'