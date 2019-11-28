from tools.PepperConfiguration import PepperConfiguration
from tools.Robot import Robot

config = PepperConfiguration("Pale")
robot = Robot(config)

min_persons = 2
max_persons = 4
person_amount_vocab = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'aight', 'nine', 'ten']
speech_recognition_language = 'English'
path_to_pictures = 'pictures/'
img_people_before_table_search = 'people_before_table_search'
img_people_after_table_search = 'people_after_table_search'