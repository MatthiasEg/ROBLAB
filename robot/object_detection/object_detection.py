import numpy as np
import cv2
import os


class ObjectDetection:

    def __init__(self):
        self.__loadYolo()

    def __loadYolo(self):
        filePath = os.path.dirname(os.path.abspath(__file__))
        labelsPath = filePath + "/yolo-coco/coco.names"
        self.__LABELS = open(labelsPath).read().strip().split("\n")

        np.random.seed(42)
        self.__COLORS = np.random.randint(0, 255, size=(len(self.__LABELS), 3), dtype="uint8")

        weightsPath = filePath + "/yolo-coco/yolov3.weights"
        configPath = filePath + "/yolo-coco/yolov3.cfg"

        print("Loading YOLO from disk")
        self.__net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
        ln = self.__net.getLayerNames()
        self.__ln = [ln[i[0] - 1] for i in self.__net.getUnconnectedOutLayers()]
        print("Loading successful")

    def analyze(self, imagePath):
        frame = cv2.imread(imagePath)

        (H, W) = frame.shape[:2]
        centerY = int(H / 2)
        centerX = int(W / 2)
        print("H: %s, W: %s" % (H, W))

        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.__net.setInput(blob)

        # intense task
        print("Analyzing file")
        layerOutputs = self.__net.forward(self.__ln)
        print("Analysis complete")

        boxes = []
        confidences = []
        classIDs = []

        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > 0.8:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (boxCenterX, boxCenterY, width, height) = box.astype("int")

                    x = int(boxCenterX - (width / 2))
                    y = int(boxCenterY - (height / 2))

                    boxes.append([x, y, int(width), int(height), int(boxCenterX), int(boxCenterY)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)
                    idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.4)
                    if len(idxs) > 0:
                        for i in idxs.flatten():
                            # if LABELS[classIDs[i]] == "cup":
                            (x, y) = (boxes[i][0], boxes[i][1])
                            (w, h) = (boxes[i][2], boxes[i][3])
                            (cX, cY) = (boxes[i][4], boxes[i][5])

                            # print("x: %s y: %s w: %s h: %s" % (str(x), str(y), str(w), str(h)))

                            color = [int(c) for c in self.__COLORS[classIDs[i]]]
                            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                            text = "{}: {:.4f}".format(self.__LABELS[classIDs[i]], confidences[i])
                            cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.imshow("Analyzed Frame", frame)
        cv2.waitKey(0) & 0xFF == ord('q')
        cv2.destroyAllWindows()
