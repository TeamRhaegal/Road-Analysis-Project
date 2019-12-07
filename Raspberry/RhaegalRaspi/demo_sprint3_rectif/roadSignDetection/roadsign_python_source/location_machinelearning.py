#!/usr/bin/env python
# coding=utf-8

"""
    LOCATION_MACHINELEARNING.PY

    the program is a library that allows you to make predictions from a given machine learning model, and to retrieve data such as areas of interest or classes. 
    It is a problem of classification AND location of panels in an image.

    the code is then used with models of type R-NN, FR-CNN, or SSD ssd_mobinet 
    
    WARNING ! IF YOU WANT TO USE THIS LIBRARY, YOU NEED TO AT LEAST MODIFY PATH TO TENSORFLOW OBJECT DETECTION FOLDER TO THE EFFECTIVE FOLDER IN 
    YOUR COMPUTER !
"""

import numpy as np
import sys, time
import tensorflow as tf
import cv2

sys.path.insert(1, "/home/pi/Documents/Tensorflow/models/research/object_detection")

from utils import label_map_util
from utils import visualization_utils as vis_util

# path to configuration model file
DEFAULT_PATH_TO_MODEL = ""
# Path to frozen detection graph. This is the actual model that is used for the object detection.
DEFAULT_PATH_TO_CKPT = ""

# List of the strings that is used to add correct label for each box.
DEFAULT_PATH_TO_LABELS = ""

# Number of classes to detect
DEFAULT_NUM_CLASSES = 3

"""
    Class used to predict location of road sign in an image and its class
"""
class LocationModel (object):
    
    def __init__(self, debug=False):
        
        self.debug = debug
        self.model_path = None
        self.ckpt_path = None
        self.label_path = None
        pass
    
    """
        Load machine learning model into memory. Includes inference graph, CKPT file and labels map
    """
    def load_model(self, model_path=DEFAULT_PATH_TO_MODEL, ckpt_path=DEFAULT_PATH_TO_CKPT, label_path=DEFAULT_PATH_TO_LABELS, num_classes=DEFAULT_NUM_CLASSES):
        
        # save model path
        self.model_path = model_path
        self.ckpt_path = ckpt_path
        self.label_path = label_path
        self.num_classes = num_classes
        
        # Load the (frozen) Tensorflow model into memory.
        with tf.gfile.GFile(ckpt_path, 'rb') as fid:
            self.od_graph_def = tf.GraphDef()
            self.od_graph_def.ParseFromString(fid.read())
        with tf.Graph().as_default() as graph:
            tf.import_graph_def(self.od_graph_def, name='')
        self.detection_graph = graph
                
        # Loading label map
        # Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine
        self.label_map = label_map_util.load_labelmap(label_path)
        self.categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=num_classes, use_display_name=True)
        self.category_index = label_map_util.create_category_index(self.categories)
        
        return self.detection_graph
            
    """
        next function : load image data to numpy array if it is a common image format  (Jpeg, png, bmp ...)
        useful if an example image is used (and not camera. py file where you can store images as numpy arrays)
    """
    def load_image_into_numpy_array(image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape(
            (im_height, im_width, 3)).astype(np.uint8)

    """
        detect roadsign position from an image as numpy array (heigth x length x RGB)
    """
    def detect_roadsigns_from_numpy_array(self, sess, image_np):
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        self.image_np_expanded = np.expand_dims(image_np, axis=0)

        # Extract image tensor
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Extract detection boxes
        self.boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Extract detection scores
        self.scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        # Extract detection classes
        self.classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        # Extract number of detections
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

        # Actual detection.
        (self.boxes, self.scores, self.classes, self.num_detections) = sess.run([self.boxes, self.scores, self.classes, self.num_detections], feed_dict={self.image_tensor: self.image_np_expanded})

        if (self.debug):
            # Visualization of the results of a detection.
            vis_util.visualize_boxes_and_labels_on_image_array(
                image_np,
                np.squeeze(self.boxes),
                np.squeeze(self.classes).astype(np.int32),
                np.squeeze(self.scores),
                self.category_index,
                use_normalized_coordinates=True,
                line_thickness=8)

            # Display output
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            cv2.imshow('object detection', image_np)
            cv2.waitKey(1)
        
        return self.boxes, self.scores, self.classes
        pass
