"""
Author: jaishivawasthi49@gmail.com
Date: 20-November-2024
"""

import cv2
import argparse
import numpy as np


class OBJECT_DETECTION:
    """Object Detection Class"""

    def __init__(self, image_path: str):
        """Initialize the image"""
        self.classes = []
        self.class_ids = []
        self.confidences = []
        self.COLORS = []
        self.boxes = []
        self.conf_threshold = 0.5
        self.nms_threshold = 0.4
        self.scale = 0.00392
        self.path_setter()
        self.image = cv2.imread(image_path)

    def path_setter(
        self,
        yolo_config_path: str = None,
        yolo_weights_path: str = None,
        yolo_classes_path: str = None,
    ):
        """Assign the path of config, weights and classes files"""
        self.yolo_config_path = yolo_config_path or "./yolov3.cfg"
        self.yolo_weights_path = yolo_weights_path or "./yolov3.weights"
        self.yolo_classes_path = yolo_classes_path or "./yolov3.txt"
        return True

    def load_classes(self):
        """Load Classes"""
        with open(self.yolo_classes_path, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.set_color_for_classes()

    def set_color_for_classes(self, classes: list = None):
        """Set Color for Classes"""
        classes_length = len(classes or self.classes)
        self.COLORS = np.random.uniform(0, 255, size=(classes_length, 3))

    def load_yolo_model(self):
        """Load Yolo Model"""
        net_object = cv2.dnn.readNet(self.yolo_weights_path, self.yolo_config_path)
        return net_object

    def resize_image(
        self,
        target_x: int = 416,
        target_y: int = 416,
        scale: float = 0.00392,
        crop: str = False,
    ):
        """Resizze the image"""
        blob = cv2.dnn.blobFromImage(
            self.image,
            scale or self.scale,
            (target_x, target_y),
            (0, 0, 0),
            True,
            crop=crop,
        )
        return blob

    def generate_indices(self):
        """generate indices"""
        net_object = self.load_yolo_model()
        blob = self.resize_image()
        net_object.setInput(blob)
        outs = net_object.forward(self.get_output_layers(net_object))
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * self.image.shape[1])
                    center_y = int(detection[1] * self.image.shape[0])
                    w = int(detection[2] * self.image.shape[1])
                    h = int(detection[3] * self.image.shape[0])
                    x = center_x - w / 2
                    y = center_y - h / 2
                    self.class_ids.append(class_id)
                    self.confidences.append(float(confidence))
                    self.boxes.append([x, y, w, h])
        indices = cv2.dnn.NMSBoxes(
            self.boxes, self.confidences, self.conf_threshold, self.nms_threshold
        )
        return indices

    def draw_bounding_boxes(self, indices: list):
        """Draw bounding boxes and create json file"""
        detection_result = []
        indices = self.generate_indices()
        for i in indices:
            try:
                box = self.boxes[i]
            except:
                i = i[0]
                box = self.boxes[i]
            x, y, w, h = box[0], box[1], box[2], box[3]
            detection_result.append(
                {
                    "object": self.classes[self.class_ids[i]],
                    "confidence": self.confidences[i],
                    "box_dimention": [round(x), round(y), round(x + w), round(y + h)],
                }
            )
            self.mark_predictions_in_image(
                self.class_ids[i],
                self.confidences[i],
                round(x),
                round(y),
                round(x + w),
                round(y + h),
            )
        return detection_result

    def mark_predictions_in_image(
        self,
        class_id: int,
        confidence: float,
        x: int,
        y: int,
        x_distance: int,
        y_distance: int,
    ):
        """Mark the predictions in the image"""
        label = str(self.classes[class_id])
        color = self.COLORS[class_id]
        cv2.rectangle(self.image, (x, y), (x_distance, y_distance), color, 2)
        cv2.putText(
            self.image, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
        )
        return True

    def get_output_layers(self, net_object):
        """Get all ouptut layers"""
        layer_names = net_object.getLayerNames()
        try:
            output_layers = [
                layer_names[i - 1] for i in net_object.getUnconnectedOutLayers()
            ]
        except:
            output_layers = [
                layer_names[i[0] - 1] for i in net_object.getUnconnectedOutLayers()
            ]
        return output_layers

    def wrapper_function(self):
        """Wrapper function"""
        self.load_classes()
        indices = self.generate_indices()
        detection_result = self.draw_bounding_boxes(indices=indices)
        # print(cv2.imshow("Image", self.image))
        cv2.imwrite("./object-detection.jpg", self.image)
        return detection_result


if __name__ == "__main__":
    obj = OBJECT_DETECTION("./uploaded_images/image1.jpg")
    print(obj.wrapper_function())
