import numpy as np
import cv2
import os

import const
from robot.object_detection.Camera import Camera
from robot.object_detection.FileTransfer import FileTransfer


class ObjectDetection:

    def __init__(self):
        self.__load_yolo()
        self.__camera = Camera(const.robot)
        self.__camera.configure_camera(self.__camera.cameras["top"], self.__camera.resolutions["640x480"],
                                       self.__camera.formats["jpg"])
        self.__file_transfer = FileTransfer(const.robot)

    def __load_yolo(self):
        file_path = os.path.dirname(os.path.abspath(__file__))
        labels_path = file_path + "/yolo-coco/coco.names"
        self.__LABELS = open(labels_path).read().strip().split("\n")

        np.random.seed(42)
        self.__COLORS = np.random.randint(0, 255, size=(len(self.__LABELS), 3), dtype="uint8")

        # weights download: https://pjreddie.com/media/files/yolov3.weights
        weights_path = file_path + "/yolo-coco/yolov3.weights"
        config_path = file_path + "/yolo-coco/yolov3.cfg"

        print("Loading YOLO from disk...")
        self.__net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
        ln = self.__net.getLayerNames()
        self.__ln = [ln[i[0] - 1] for i in self.__net.getUnconnectedOutLayers()]
        print("YOLO loaded successfully!")

    def analyze(self, image_path, object_to_find_label, min_confidence=0.3):
        if not os.path.isfile(image_path):
            raise ValueError("Object detection: Wrong image path!")

        min_confidence = float(min_confidence)
        frame = cv2.imread(image_path)
        (H, W) = frame.shape[:2]
        center_y = int(H / 2)
        center_x = int(W / 2)

        cv2.rectangle(frame, (center_x - 30, center_y - 30), (center_x + 60, center_y + 60), [int(c) for c in self.__COLORS[0]], 2)

        center_box = dict()
        center_box["name"] = "center_box"
        center_box["centerX"] = center_x
        center_box["centerY"] = center_y

        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.__net.setInput(blob)
        layer_outputs = self.__net.forward(self.__ln)

        boxes = []
        confidences = []
        classIDs = []
        detected_objects = []
        detected_objects.append(center_box)

        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > min_confidence:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (boxCenterX, boxCenterY, width, height) = box.astype("int")

                    x = int(boxCenterX - (width / 2))
                    y = int(boxCenterY - (height / 2))

                    boxes.append([x, y, int(width), int(height), int(boxCenterX), int(boxCenterY)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)
                    idxs = cv2.dnn.NMSBoxes(boxes, confidences, min_confidence, 0.3)
                    if len(idxs) > 0:
                        for i in idxs.flatten():
                            if object_to_find_label is not None:
                                if self.__LABELS[classIDs[i]] == object_to_find_label:
                                    detected_objects.append(self.__draw_boxes(i, frame, boxes, classIDs, confidences))
                            else:
                                detected_objects.append(self.__draw_boxes(i, frame, boxes, classIDs, confidences))


        # cv2.imshow("Analyzed Frame", frame)
        # cv2.waitKey(0) & 0xFF == ord('q')
        # cv2.destroyAllWindows()

        return detected_objects

    def __draw_boxes(self, i, frame, boxes, classIDs, confidences):
        (x, y) = (boxes[i][0], boxes[i][1])
        (w, h) = (boxes[i][2], boxes[i][3])
        (cX, cY) = (boxes[i][4], boxes[i][5])

        # color = [int(c) for c in self.__COLORS[classIDs[i]]]
        color = [int(c) for c in self.__COLORS[i]]
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        text = "{}: {:.4f}".format(self.__LABELS[classIDs[i]], confidences[i])
        cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        detected_object_info = dict()
        detected_object_info["name"] = self.__LABELS[classIDs[i]]
        detected_object_info["x"] = x
        detected_object_info["y"] = y
        detected_object_info["w"] = w
        detected_object_info["h"] = h
        detected_object_info["centerX"] = cX
        detected_object_info["centerY"] = cY

        return detected_object_info

    def get_red_cup_keypoints(self):
        hsv_red_lower = (166, 155, 100)
        hsv_red_upper = (180, 255, 255)

        file_name = "temp_picture.jpg"
        self.__take_picture(file_name)

        cv_image = cv2.imread(file_name)
        blob_params = self.__build_blob_detector_params()

        return self.__get_keypoints(cv_image, hsv_red_lower, hsv_red_upper, blob_params)

    @staticmethod
    def __build_blob_detector_params():
        params = cv2.SimpleBlobDetector_Params()
        # Change thresholds
        params.minThreshold = 100
        params.maxThreshold = 5000

        params.filterByConvexity = True
        params.minConvexity = 0.87

        return params

    def __get_keypoints(self, cv_image, hsv_red_lower, hsv_red_upper, blob_params):
        (rows, cols, channels) = cv_image.shape
        cup_points = []
        if cols > 60 and rows > 60:
            # --- Detect blobs
            keypoints = self.__blob_detect(cv_image, hsv_red_lower, hsv_red_upper, blob_params)
            for i, key_point in enumerate(keypoints):
                # --- Find x and y position in camera adimensional frame
                # x, y = self.__get_blob_relative_position(cv_image, key_point)
                cup_point = dict()
                cup_point["x"] = key_point.pt[0]
                cup_point["y"] = key_point.pt[1]
                cup_point["size"] = key_point.size
                cup_points.append(cup_point)
        return cup_points

    def __blob_detect(self, image,  # -- The frame (cv standard)
                      hsv_min,  # -- minimum threshold of the hsv filter [h_min, s_min, v_min]
                      hsv_max,  # -- maximum threshold of the hsv filter [h_max, s_max, v_max]
                      blob_params):
        # - Convert image from BGR to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # - Apply HSV threshold
        mask = cv2.inRange(hsv, hsv_min, hsv_max)
        mask = cv2.dilate(mask, None, iterations=2)
        mask = cv2.erode(mask, None, iterations=2)

         # - Apply blob detection
        detector = cv2.SimpleBlobDetector_create(blob_params)
        # Reverse the mask: blobs are black on white
        reversemask = 255 - mask
        keypoints = detector.detect(reversemask)

        self.draw_keypoints(image, keypoints)

        return keypoints

    @staticmethod
    def draw_keypoints(image,  # -- Input image
                       keypoints,  # -- CV keypoints
                       line_color=(0, 0, 255),  # -- line's color (b,g,r)
                       ):

        # -- Draw detected blobs as red circles.
        # -- cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
        im_with_keypoints = cv2.drawKeypoints(image, keypoints, np.array([]), line_color,
                                              cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imshow("Keypoints", im_with_keypoints)
        cv2.waitKey(1)

    def __take_picture(self, file_name):
        remote_folder_path = "/home/nao/recordings/cameras/"
        self.__camera.take_picture(remote_folder_path, file_name)
        local = file_name
        remote = remote_folder_path + file_name

        self.__file_transfer.get(remote, local)

    def __del__(self):
        self.__file_transfer.close()
        cv2.destroyAllWindows()
