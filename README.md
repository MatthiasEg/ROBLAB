# Dinner for one
Implementation of a behavior for the Pepper robot by SoftBank Robotics built on top of the naoqi SDK.

## Behavior description
This behavior lets Pepper search for a table with a specific number of cups on it and then assign a group of people to it.
Pepper will wait for new persons in a waiting zone and automatically recognize when new faces show up.
Pepper will then count the amount of people and ask for confirmation. After that, it will search for a free table and return to the waiting area to ask the guests to follow it to the found spot. 

## Project description
This project consists of three main directories:
* behavior (main scripts for behavior logic)
* robot (wrappers and object detection)
* tools (naoqi wrappers and robot configuration files)

To execute the behavior, execute main.py

Behavior can be customized by values in const.py

## How to start
- Download YOLO Model from https://pjreddie.com/media/files/yolov3.weights
- Put it in the folder robot/object_detection/yolo-coco
- Configure values in const.py
- Run main.py

## Team
* Matthias Egli
* Patrick Lädrach
* Mario Zelger