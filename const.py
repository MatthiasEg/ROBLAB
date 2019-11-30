from tools.PepperConfiguration import PepperConfiguration
from tools.Robot import Robot

config = PepperConfiguration("Pale")
robot = Robot(config)

min_persons = 2
max_persons = 4

speech_recognition_language = 'English'
speech_recognition_precision = 0.4
path_to_locale_file = 'locale/en.json'
path_to_pictures = 'pictures/'
img_people_before_table_search = 'people_before_table_search'
img_people_after_table_search = 'people_after_table_search'