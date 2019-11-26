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

sys.path.append('roadsign_python_source/')
from roadsign_python_source import location_machinelearning

RASPICAM_ENABLE = True
if (RASPICAM_ENABLE):
    from roadsign_python_source import raspicam
    
print("imported libraries : ellapsed time : {} s".format(time.time() - begin))
      
# define if we want to draw rectangles around ROIs and save corresonding images (for DEBUG purposes)
DRAW = False

"""
    Define different paths for example images, location model...
"""
# images paths
PATH_FOR_EXAMPLE_IMAGE = "images/stoptest.ppm"

# path to configuration model file
PATH_TO_MODEL = "machinelearning_model/300_300_pipeline.config"
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = "machinelearning_model/300_300_frozen_inference_graph.pb"

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = "machinelearning_model/300_300_labelmap.pbtxt"

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
    os.system("rm -rf  roadsign_python_source/*.pyc && rm -rf roadsign_python_source/keras_frcnn/*.pyc")

    # init camera or example image depending on the mode chosen
    if (RASPICAM_ENABLE):
        #init camera from raspberry (raspicam)
        print("initializing camera")
        camera = raspicam.Raspicam(resolution = (1640,922))
    else:
        # load example image 
        print("loading example image (not camera)")
        location_input_image = cv2.imread(PATH_FOR_EXAMPLE_IMAGE)    
        
        if(DRAW):
            cv2.imshow("image", location_input_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    
    # define location object instance
    location_model = location_machinelearning.LocationModel()
    # load model from specified files
    detection_graph = location_model.load_model(model_path=PATH_TO_MODEL, ckpt_path=PATH_TO_CKPT, label_path=PATH_TO_LABELS, num_classes=NUM_CLASSES)
    
    # camera focal value (used to calculate the roadsign distance from the camera
    focal = 1026
    old_distance = None
    
    # local variable to send "stop message" only 1 time"
    send_message = 0

    print ("initialized roadsign detector. Ellapsed time : {} s".format(time.time()-init_time))
    
    """
        MAIN LOOP
    """
    with tf.Session(graph=detection_graph) as sess:
        while(runEvent.isSet()):
            
            sharedRessources.lockConnectedDevice.acquire()
            check_connected = sharedRessources.connectedDevice
            sharedRessources.lockConnectedDevice.release()
            
            if (check_connected == True):
                
                # capture image
                if (RASPICAM_ENABLE):
                    camera.capture_image()
                    location_input_image = camera.read_image_as_numpy_array(save=False)
                    location_input_image = cv2.cvtColor(location_input_image, cv2.COLOR_BGR2RGB)
                    
                # process prediction from model and get scores + corresponding boxes
                location_boxes, location_score, location_classes = location_model.detect_roadsigns_from_numpy_array(location_input_image.copy())

                """
                    Next part of code :
                        - save each box were the probability score is better than a defined threshold 
                        - compute width of the corresponding box in order to be used after.
                    If DEBUG is True, print, save and show image with all the boxes rendered. 
                """
                for i in range(location_boxes.shape[1]):
                    if (location_boxes[0][i][0] != 0 and location_score[0][i] > 0.1):
                        result = int(location_classes[0][i])
                        print ("found roadsign : {}".format(roadsign_types[result-1][0]))
                        # capture interesting part (box) from the global image
                        x1 = int(location_boxes[0][i][1]*location_input_image.shape[1])
                        x2 = int(location_boxes[0][i][3]*location_input_image.shape[1])
                        y1 = int(location_boxes[0][i][0]*location_input_image.shape[0])
                        y2 = int(location_boxes[0][i][2]*location_input_image.shape[0])
                        w = x2 - x1
                        
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
                            
                        if (result == 1 and send_message == 0):
                            send_message = 1
                            sharedRessources.lockMessagesToSend.acquire()
                            sharedRessources.listMessagesToSend.append("sign$stop")
                            sharedRessources.lockMessagesToSend.release()

                        # save result in global variable
                        sharedRessources.signLock.acquire()
                        sharedRessources.sign.append(roadsign_types[result-1][0])                                                                                                                                                                                                                                                                                                                                                        
                        sharedRessources.signLock.release()
                        
                        sharedRessources.signWidthLock.acquire()
                        sharedRessources.signWidth = w
                        sharedRessources.signWidthLock.release()
                                    
            else : 
                send_message = 0
                
            time.sleep(0.1)
        
