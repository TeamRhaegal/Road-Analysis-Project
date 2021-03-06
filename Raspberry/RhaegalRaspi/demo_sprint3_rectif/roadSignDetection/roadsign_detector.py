#!/usr/bin/env python

"""
    Optimised code that allows to detect road signs from an image and classify them, using only one machine learning model (SSD mobilenet)
"""

import time

print("Importing libraries")
begin = time.time()
# system imports 
import sys, os, time
from threading import Thread, Lock

import sharedRessources
# image processing imports
from skimage import io
import cv2, imutils
# arrays processing imports
import numpy as np
import tensorflow as tf

sys.path.append('roadSignDetection/roadsign_python_source/')
from roadsign_python_source import location_machinelearning
from roadsign_python_source import raspicam
    
print("imported libraries : ellapsed time : {} s".format(time.time() - begin))
      
# define if we want to draw rectangles around ROIs and save corresonding images (for DEBUG purposes)
DRAW = False

"""
    Define different paths for location model...
"""
# path to configuration model file
PATH_TO_MODEL = "roadSignDetection/machinelearning_model/300_300_pipeline.config"
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = "roadSignDetection/machinelearning_model/300_300_frozen_inference_graph.pb"

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = "roadSignDetection/machinelearning_model/300_300_labelmap.pbtxt"

# Number of classes to detect
NUM_CLASSES = 3

"""
    OBJECT INSTANCES AND CONSTANTS
        - roadsign_types : meaning of each 43 classes of road signs, and a path to an image of each road sign
"""
roadsign_types =    [   ["stop",                        ""],
                        ["search",                      ""],
                        ["prohibited",                  ""],
                    ]

"""
    Capture an image from the raspicam, or open an example file if we chose this mode. 
        Then process it, find location of different shapes (road signs) and classify each sign. 
        Modify roadsign class and width global variables in order to be used by other threads
"""
def roadsign_detector(runEvent):
    global PATH_FOR_EXAMPLE_IMAGE, PATH_TO_MODEL, PATH_TO_CKPT, PATH_TO_LABELS, NUM_CLASSES
    
    print("initializing roadsign detector")
    init_time = time.time()
    #Remove Python cache files if they exist
    os.system("rm -rf  roadSignDetection/machinelearning_model/*.pyc && rm -rf roadSignDetection/machinelearning_model/*.pyc")

    #init camera from raspberry (raspicam)
    print("initializing camera")
    camera = raspicam.Raspicam(resolution = (300,300))

    # define location object instance
    location_model = location_machinelearning.LocationModel(debug = DRAW)
    # load model from specified files
    detection_graph = location_model.load_model(model_path=PATH_TO_MODEL, ckpt_path=PATH_TO_CKPT, label_path=PATH_TO_LABELS, num_classes=NUM_CLASSES)
    
    # camera focal value (used to calculate the roadsign distance from the camera
    focal = 1026
    old_distance = None

    # variable that shows 
    detected_stop = False
    detected_search = False

    # width of road signs
    w = 0
    width_stop = []
    width_search = []
    
    # no detection counter. Useful to detect if no road sign is present in the image, or if there is just a recognition error.
    no_detection_count = 0

    print ("initialized roadsign detector. Ellapsed time : {} s".format(time.time()-init_time))
    
    """
        MAIN LOOP
    """
    with tf.Session(graph=detection_graph) as sess:
        while(runEvent.isSet()):
            
            time.sleep(0.1)
            sharedRessources.lockConnectedDevice.acquire()
            check_connected = sharedRessources.connectedDevice
            sharedRessources.lockConnectedDevice.release()
            
            if (check_connected == True):
                
                t = time.time()
                # capture image
                camera.capture_image()
                location_input_image = camera.read_image_as_numpy_array(save=False)
                #location_input_image = cv2.cvtColor(location_input_image, cv2.COLOR_RGB2BGR)
                    
                # process prediction from model and get scores + corresponding boxes
                location_boxes, location_score, location_classes = location_model.detect_roadsigns_from_numpy_array(sess, location_input_image.copy())

                """
                    Next part of code :
                        - save each box were the probability score is better than a defined threshold 
                        - compute width of the corresponding box in order to be used after.
                    If DEBUG is True, print, save and show image with all the boxes rendered. 
                """
                
                # assume we start with no detection
                result = 0
                detected_stop = False
                detected_search = False
                width_stop = []
                width_search  = []
                
                # search for road sign in all the found boxes
                for i in range(location_boxes.shape[1]):
                    # if the code go through the next condition, a road sign is detected. 
                    if (location_boxes[0][i][0] != 0 and location_score[0][i] > 0.75):
                        
                        # assign "no_detection_count" to 0  because a road sign has been detected
                        no_detection_count = 0
                        
                        # find prediction result from collected data (boxes, score for each box and class for each box)
                        result = int(location_classes[0][i])
                                                     
                        # capture interesting part (box) from the global image
                        x1 = int(location_boxes[0][i][1]*location_input_image.shape[1])
                        x2 = int(location_boxes[0][i][3]*location_input_image.shape[1])
                        y1 = int(location_boxes[0][i][0]*location_input_image.shape[0])
                        y2 = int(location_boxes[0][i][2]*location_input_image.shape[0])
                        # compute width of the road sign in pixels
                        w = x2 - x1                   
                        
                        # detected stop sign : add width to list of width for this sign
                        if (result == 1):
                            detected_stop = True
                            width_stop.append(w)
                        
                        # detected search sign : add width to list of width for this sign
                        elif (result == 2):
                            detected_search = True
                            width_search.append(w)
                            
                        elif(result==3):
                            print("i have found a PROHIBITED sign")
                        
                        """
                        # compute road sign distance from the camera
                        if (w != None and w > 0):
                            distance = (0.195 * focal) / w
                            if (old_distance != distance):
                                old_distance = distance
                                print ("distance = {} meters".format(distance))
                                print ("width = {} pixels".format(w))
                         
                         
                        if (DRAW):
                            # draw rectangle boxes around Region of Interest (ROI)
                            cv2.rectangle(location_input_image, (x1,y1), (x2,y2), (255,0,0), 1)
                            location_input_image = cv2.cvtColor(location_input_image, cv2.COLOR_RGB2BGR)
                            cv2.imshow("object_detection", location_input_image)
                            cv2.waitKey(0)
                        """
                        
                # save sign width (minimum bounding box around the sign
                if (detected_stop):
                    print("i have found a STOP !")
                    w = min(width_stop)
                    sharedRessources.lockWidthStop.acquire()
                    sharedRessources.widthStop = w
                    sharedRessources.lockWidthStop.release()
                    
                if (detected_search):
                    print("i have found a SEARCH")
                    w = min(width_search)
                    sharedRessources.lockWidthSearch.acquire()
                    sharedRessources.widthSearch = w
                    sharedRessources.lockWidthSearch.release()
                
                else:
                    # increase no detection counter
                    no_detection_count += 1
                    # if "no_detection_count" 
                    if (no_detection_count >= 2):
                        w = 0
                        sharedRessources.lockWidthStop.acquire()
                        sharedRessources.widthStop = w
                        sharedRessources.lockWidthStop.release()
                        
                        sharedRessources.lockWidthSearch.acquire()
                        sharedRessources.widthSearch = w
                        sharedRessources.lockWidthSearch.release()
