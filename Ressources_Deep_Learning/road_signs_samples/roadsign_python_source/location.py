#!/usr/bin/env python
# coding=utf-8

"""
    LOCATION.PY

    Code and pre trained model mainly comes from the article : 
    "Evaluation of deep neural networks for traffic sign detection systems."
    Álvaro Arcos-García, Juan A. Álvarez-García, Luis M. Soria-Morillo. Neurocomputing 316 (2018) 332-344."
    
    Please visit the next github link if you want more informations : https://github.com/aarcosg/traffic-sign-detection
"""

import warnings
warnings.filterwarnings('ignore')
import numpy as np
import os, sys
import tensorflow as tf
from matplotlib import pyplot as plt
from PIL import Image
import glob as glob

import sys
sys.path.append('/home/vincent/Tensorflow/models/research/object_detection') # ~/tensorflow/models/research/object_detection
from object_detection.utils import label_map_util
from utils import visualization_utils as vis_util

"""
    Define default paths to models files.
"""

# Path to frozen detection graph. This is the actual model that is used for the traffic sign detection.
DEFAULT_PATH_TO_MODEL = "F_RCNN_location/mobilenet_v1/ssd_mobilenet_v1_gtsdb3.config"
DEFAULT_PATH_TO_CKPT = "F_RCNN_location/mobilenet_v1/frozen_inference_graph.pb"

# define path to labels files and choose to use one of the type of labels (43 labels : one for each road sign, or 3 labels : one for each category : mandatory, prohibitory, danger).
DEFAULT_PATH_TO_LABELS = "F_RCNN_location/scripts/gtsdb3_label_map.pbtxt"
DEFAULT_NUM_CLASSES = 3

# Size, in inches, of the output images.
DEFAULT_OUTPUT_IMAGE_SIZE = (20, 20)

class LocationModel (object):
    
    def __init__(self, debug=False):
        
        self.debug = debug
        self.model_path = None
        self.ckpt_path = None
        self.label_path = None
        self.detection_graph = None
        self.od_graph_def = None
        self.serialized_graph = None
        self.label_map = None
        self.categories = None
        
        pass
    
    """
        Load F-RCNN model to be used, in order to find the location of road signs. 
    """
    def load_model(self, model_path=DEFAULT_PATH_TO_MODEL, ckpt_path=DEFAULT_PATH_TO_CKPT, label_path=DEFAULT_PATH_TO_LABELS, num_classes=DEFAULT_NUM_CLASSES):
        # save model path
        self.model_path = model_path
        self.ckpt_path = ckpt_path
        self.label_path = label_path
        self.num_classes = num_classes
        
        # load inference graph 
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            self.od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(ckpt_path, 'rb') as fid:
                self.serialized_graph = fid.read()
                self.od_graph_def.ParseFromString(self.serialized_graph)
                tf.import_graph_def(self.od_graph_def, name='')
                
        # load label maps to apply labels on detected road signs (mandatory, prohibitory, danger)
        self.label_map = label_map_util.load_labelmap(self.label_path)
        self.categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=self.num_classes, use_display_name=True)
        self.category_index = label_map_util.create_category_index(self.categories)
        print(self.category_index)
        pass
    
    """
        next function : load image data to numpy array if it is a common image format  (Jpeg, png, bmp ...)
        useful if an example image is used (and not camera. py file where you can store images as numpy arrays)
    """
    def load_image_into_numpy_array(self, image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)
        pass

    """
        detect roadsign position from an image as numpy array (heigth x length x RGB)
    """
    def detect_roadsigns_from_numpy_array(self, image_np, image_size=DEFAULT_OUTPUT_IMAGE_SIZE):
        if (self.detection_graph == None):
            print ("\nError : please run 'load_model' function before trying to detect roadsigns")
            return None
        with self.detection_graph.as_default():      
            with tf.Session(graph=self.detection_graph) as sess:
                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(image_np, axis=0)
                image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
                # Each box represents a part of the image where a particular object was detected.
                self.boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
                # Each score represent how level of confidence for each of the objects.
                # Score is shown on the result image, together with the class label.
                self.scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
                self.classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
                self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
                # Actual detection.
                self.feed_dict = {image_tensor: image_np_expanded}
                (self.boxes, self.scores, self.classes, self.num_detections) = sess.run(
                                    [self.boxes, self.scores, self.classes, self.num_detections],
                                    self.feed_dict)
                # Visualization of the results of a detection.
                if(self.debug):
                    vis_util.visualize_boxes_and_labels_on_image_array(
                                                                                                        image_np,
                                                                                                        np.squeeze(self.boxes),
                                                                                                        np.squeeze(self.classes).astype(np.int32),
                                                                                                        np.squeeze(self.scores),
                                                                                                        self.category_index,
                                                                                                        use_normalized_coordinates=True,
                                                                                                        line_thickness=6)
                    plt.figure(1, figsize=image_size)
                    plt.axis('off')
                    plt.imshow(image_np)
                
                return self.boxes, self.scores
                pass
    
    """
        detect roadsigns from stored image (as ppm file in general)
    """
    def detect_roadsigns_from_image(self, image_path, image_size=DEFAULT_OUTPUT_IMAGE_SIZE):
        if (self.detection_graph == None):
            print ("\nError : please run 'load_model' function before trying to detect roadsigns")
            return None
            pass
        
        image = Image.open(image_path)
        # the array based representation of the image will be used later in order to prepare the
        # result image with boxes and labels on it.
        image_np = load_image_into_numpy_array(image)
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
        # Actual detection.
        self.feed_dict = {image_tensor: image_np_expanded}
        (self.boxes, self.scores, self.classes, self.num_detections) = sess.run(
                                [self.boxes, self.scores, self.classes, self.num_detections],
                                self.feed_dict)
        # Visualization of the results of a detection.
        if(self.debug):
            vis_util.visualize_boxes_and_labels_on_image_array(
                                                                                                image_np,
                                                                                                np.squeeze(self.boxes),
                                                                                                np.squeeze(self.classes).astype(np.int32),
                                                                                                np.squeeze(self.scores),
                                                                                                self.category_index,
                                                                                                use_normalized_coordinates=True,
                                                                                                line_thickness=6)
            plt.figure(2, figsize=image_size)
            plt.axis('off')
            plt.imshow(image_np)
        
        return self.boxes, self.scores

        pass
            
    
