from Robot import Robot
from PepperConfiguration import PepperConfiguration

config = PepperConfiguration('Amber')
pepper = Robot(config)

pepper.ALTextToSpeech.setLanguage('English')
pepper.ALAnimatedSpeech.say('hello')
languages = pepper.ALTextToSpeech.getAvailableLanguages()
if 'German' in languages:
    pepper.ALTextToSpeech.setLanguage('German')
    pepper.ALTextToSpeech.say('hallo')
