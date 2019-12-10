import os

import cv2
import numpy as np


class ObjectDetector:

    def __init__(self):
        self.__load_yolo()

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

    def get_object_positions(self, image_path, object_to_find_label, min_confidence=0.3):
        if not os.path.isfile(image_path):
            raise ValueError("Object detection: Couldn't find image!")

        min_confidence = float(min_confidence)
        frame = cv2.imread(image_path)
        (H, W) = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.__net.setInput(blob)
        layer_outputs = self.__net.forward(self.__ln)

        boxes = []
        confidences = []
        classIDs = []
        detected_objects = []

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
                                    detected_objects.append(
                                        self.__build_object_position_info(i, frame, boxes, classIDs, confidences))
                            else:
                                detected_objects.append(
                                    self.__build_object_position_info(i, frame, boxes, classIDs, confidences))

        return detected_objects

    def __build_object_position_info(self, i, frame, boxes, classIDs, confidences):
        (x, y) = (boxes[i][0], boxes[i][1])
        (w, h) = (boxes[i][2], boxes[i][3])
        (cX, cY) = (boxes[i][4], boxes[i][5])

        color = [int(c) for c in self.__COLORS[classIDs[i]]]
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

    def get_red_cup_keypoints(self, image_path):
        if not os.path.isfile(image_path):
            raise ValueError("Object detection: Couldn't find image!")

        cv_image = cv2.imread(image_path)

        blob_params = self.__build_blob_detector_params()
        # limits for red cups used
        hsv_red_lower = (166, 155, 100)
        hsv_red_upper = (180, 255, 255)

        return self.__get_key_points(cv_image, hsv_red_lower, hsv_red_upper, blob_params)

    @staticmethod
    def __build_blob_detector_params():
        params = cv2.SimpleBlobDetector_Params()
        params.minThreshold = 100
        params.maxThreshold = 5000
        params.filterByConvexity = True
        params.minConvexity = 0.87
        return params

    def __get_key_points(self, cv_image, hsv_red_lower, hsv_red_upper, blob_params):
        (rows, cols, channels) = cv_image.shape
        cup_key_points = []
        if cols > 60 and rows > 60:
            # --- Detect blobs
            key_points = self.__blob_detect(cv_image, hsv_red_lower, hsv_red_upper, blob_params)
            for i, key_point in enumerate(key_points):
                cup_keypoint = dict()
                cup_keypoint["x"] = key_point.pt[0]
                cup_keypoint["y"] = key_point.pt[1]
                cup_keypoint["size"] = key_point.size
                cup_key_points.append(cup_keypoint)
        return cup_key_points

    def __blob_detect(self, image,
                      hsv_min,
                      hsv_max,
                      blob_params):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, hsv_min, hsv_max)
        mask = cv2.dilate(mask, None, iterations=2)
        mask = cv2.erode(mask, None, iterations=2)

        detector = cv2.SimpleBlobDetector_create(blob_params)
        reversemask = 255 - mask
        keypoints = detector.detect(reversemask)

        self.__draw_key_points(image, keypoints)
        return keypoints

    @staticmethod
    def __draw_key_points(image,  # -- Input image
                          keypoints,  # -- CV keypoints
                          line_color=(0, 0, 255),  # -- line's color (b,g,r)
                          ):

        im_with_keypoints = cv2.drawKeypoints(image, keypoints, np.array([]), line_color,
                                              cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imshow("Red Cups", im_with_keypoints)
        cv2.waitKey(1)

    def __del__(self):
        cv2.destroyAllWindows()
