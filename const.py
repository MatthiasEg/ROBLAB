from tools.PepperConfiguration import PepperConfiguration
from tools.Robot import Robot

config = PepperConfiguration("Pale")
robot = Robot(config)

min_persons = 1
max_persons = 4
person_amount_vocab = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'aight', 'nine', 'ten']
speech_recognition_language = 'English'
