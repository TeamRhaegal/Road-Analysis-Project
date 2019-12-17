# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    code that allows to : 
        - capture image from raspicam
        - run SSD mobilenet machine learning model to find and classify road signs (stop, prohibited way and search signs)
        - run another SSD mobilenet model in search mode to find and classify different objects (small, medium, big
"""

# import libraries 
import time

print("Importing libraries for roadsign detector")
begin = time.time()
# system imports 
import sys, os
from threading import Thread
# Project's shared ressources import
import sharedRessources
# image processing imports
from skimage import io
import cv2, imutils
# arrays processing imports
import numpy as np
import tensorflow as tf
# hardware and machine learning imports
sys.path.append('/home/pi/Documents/projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/Demo_sprint4/roadSignDetection/roadsign_python_source/')
from roadsign_python_source import location_machinelearning
from roadsign_python_source import raspicam
    
print("imported libraries : ellapsed time : {} s".format(time.time() - begin))
      
# define if we want to draw rectangles around ROIs and save corresonding images (for DEBUG purposes)
ROADSIGN_DRAW = False
SEARCH_DRAW = True

"""
    Define different paths for Roadsigns location model...
"""
# path to configuration model file : '.config' file
PATH_TO_ROADSIGN_MODEL = "/home/pi/Documents/projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/Demo_sprint4/roadSignDetection/machinelearning_model/roadsign_300_300_pipeline.config"
# Path to frozen detection graph. This is the actual model that is used for the object detection : '.pb' file
PATH_TO_ROADSIGN_CKPT = "/home/pi/Documents/projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/Demo_sprint4/roadSignDetection/machinelearning_model/roadsign_300_300_frozen_inference_graph.pb"
# List of the strings that is used to add correct label for each box : '.pbtxt' file
PATH_TO_ROADSIGN_LABELS = "/home/pi/Documents/projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/Demo_sprint4/roadSignDetection/machinelearning_model/roadsign_300_300_labelmap.pbtxt"
# Number of classes to detect
ROADSIGN_NUM_CLASSES = 3

"""
    Define different paths for objects (search mode) location model...
"""
# path to configuration model file : '.config' file
PATH_TO_SEARCH_MODEL = "/home/pi/Documents/projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/Demo_sprint4/roadSignDetection/machinelearning_model/search_300_300_pipeline.config"
# Path to frozen detection graph. This is the actual model that is used for the object detection : '.pb' file
PATH_TO_SEARCH_CKPT = "/home/pi/Documents/projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/Demo_sprint4/roadSignDetection/machinelearning_model/search_300_300_frozen_inference_graph.pb"
# List of the strings that is used to add correct label for each box : '.pbtxt' file
PATH_TO_SEARCH_LABELS = "/home/pi/Documents/projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/Demo_sprint4/roadSignDetection/machinelearning_model/search_300_300_labelmap.pbtxt"
# Number of classes to detect
SEARCH_NUM_CLASSES = 3

"""
    OBJECT INSTANCES AND CONSTANTS
        - roadsign_types : meaning of each 3 classes of road signs, and a path to an image of each road sign (if needed)
        - search_object_types : meaning of each 3 classes for search mode, and a path to an image of each class (if needed)
    This part is not useful anymore and is just information about existing classes
"""
roadsign_types =    [   ["stop",                        ""],
                        ["search",                      ""],
                        ["prohibited",                  ""],
                    ]

search_object_types  =  [   ["small",                       ""],
                            ["medium",                      ""],
                            ["big",                         ""],
                        ]

"""
    Capture an image from the raspicam, then process it, find location of different shapes (road signs in "common mode", objects in "search mode") and classify them. 
    Modify roadsign class and width global variables in order to be used by other threads
"""
class ObjectDetector(Thread):
    
    def __init__(self, runEvent):
        Thread.__init__(self)
        # variable used to check if connection has been established between smartphone (HMI) and car
        self.runEvent = runEvent
        # retrieve default informations from global variables in this file
        self.getGlobalInfos()
        # init hardware and machine learning models
        print("initializing hardware and machine learning models")
        begin = time.time()
        self.camera = self.openCamera(resolution=(300,300), save=False, preview=False)
        self.roadsign_model = self.initLocationModel(self.roadsign_draw)
        self.roadsign_detection_graph = self.loadLocationModel(location_model=self.roadsign_model, model_path=self.path_to_roadsign_model, ckpt_path=self.path_to_roadsign_ckpt, label_path=self.path_to_roadsign_labels, num_classes=self.roadsign_num_classes)
        self.search_model = self.initLocationModel(self.search_draw)
        self.search_detection_graph = self.loadLocationModel(location_model=self.search_model, model_path=self.path_to_search_model, ckpt_path=self.path_to_search_ckpt, label_path=self.path_to_search_labels, num_classes=self.search_num_classes)
        print("Initialized hardware and machine learning model. Time taken : {} seconds".format(time.time()-begin))
        pass
    
    def getGlobalInfos(self):
         # configure options from global variables
        self.roadsign_draw = ROADSIGN_DRAW
        self.search_draw = SEARCH_DRAW
        self.path_to_roadsign_model = PATH_TO_ROADSIGN_MODEL
        self.path_to_roadsign_ckpt = PATH_TO_ROADSIGN_CKPT
        self.path_to_roadsign_labels = PATH_TO_ROADSIGN_LABELS
        self.roadsign_num_classes = ROADSIGN_NUM_CLASSES
        
        self.path_to_search_model = PATH_TO_SEARCH_MODEL
        self.path_to_search_ckpt = PATH_TO_SEARCH_CKPT
        self.path_to_search_labels = PATH_TO_SEARCH_LABELS
        self.search_num_classes = SEARCH_NUM_CLASSES
        pass
    
    def openCamera(self, resolution=(300,300), save=False, preview=False):
        try:
            print("Initializing camera with resolution : {}\nOptions : \n\tsave : {}\n\tpreview : {}".format(resolution, save, preview))
            return raspicam.Raspicam(resolution = resolution, save = save, preview = preview)
        except Exception as e:
            print("[ERROR] : Couldn't open camera. Exception : {}".format(str(e)))
        pass
    
    def initLocationModel(self, draw=False):
        try:
            return location_machinelearning.LocationModel(debug = draw)
        except Exception as e:
            print("[ERROR] : couldn't init location model. Exception : {}".format(str(e)))
        pass
        
    def loadLocationModel(self, location_model, model_path="", ckpt_path="", label_path="", num_classes=3):
        try:
            print ("initializing location model : {}".format(location_model))
            return location_model.loadModel(model_path=model_path, ckpt_path=ckpt_path, label_path=label_path, num_classes=num_classes)
        except Exception as e:
            print("[ERROR] : couldn't load location model. Exception : {}".format(str(e)))
        pass
    
    def run(self):
        # no detection counter. Useful to detect if no road sign/object is present in the image, or if there is just a recognition error.
        no_roadsign_detection_count = 0
        no_object_detection_count = 0
        # variable used to check if connection is established between smartphone (HMI) and car
        self.check_connected = False
        """
            MAIN LOOP
        """
        with tf.Session(graph=self.roadsign_detection_graph) as roadsign_sess:
            with tf.Session(graph=self.search_detection_graph) as search_sess:
                # capture one image and process both roadsign and search mode detection to test and init them
                self.initTestDetection(camera=self.camera, roadsign_model=self.roadsign_model, search_model=self.search_model, roadsign_sess=roadsign_sess, search_sess=search_sess)
                # Run detection loop while smartphone is connected to the car
                while (self.runEvent.isSet()):
                    # wait minimum amount of time in order to avoid blocking other threads
                    time.sleep(0.1)
                    self.check_connected = self.getConnectedGlobalVariable()
                    if (self.check_connected):
                        # capture and save image from raspicam
                        self.camera.captureImage()
                        input_image = self.camera.readImageAsNumpyArray(save=False)
                        #input_image = cv2.cvtColor(input_image, cv2.COLOR_RGB2BGR) 
                        # check if we are in search mode or not
                        self.check_searchmode = self.getSearchModeGlobalVariable()
                        #------------------------------------------------------------------------
                        #    Road sign detection if we are in "common" mode (auto, assist)
                        #------------------------------------------------------------------------
                        if (not self.check_searchmode):
                            # process prediction from roadsign model and get scores + corresponding boxes FOR ROADSIGN DETECTION MODEL
                            roadsign_location_boxes, roadsign_location_score, roadsign_location_classes = self.roadsign_model.detectObjectsFromNumpyArray(roadsign_sess, input_image.copy())
                            """
                                Next part of code :
                                    - save each box where the probability score is better than a defined threshold 
                                If DEBUG is True, print, save and show image with all the boxes rendered. 
                            """
                            # assume we start with no detection
                            result = 0
                            detected_stop = False
                            detected_search = False
                            width_stop = []
                            width_search  = []
                            # search for road sign in all the found boxes (in the corresponding model
                            for i in range(roadsign_location_boxes.shape[1]):
                                # detect a road sign if probability score of a box is better than a defined threshold
                                if (roadsign_location_boxes[0][i][0] != 0 and roadsign_location_score[0][i] > 0.75):
                                    # assign "no_roadsign_detection_count" to 0  because a road sign has been detected
                                    no_roadsign_detection_count = 0
                                    # find prediction result from collected data (boxes, score for each box and class for each box)
                                    result = int(roadsign_location_classes[0][i])             
                                    # capture interesting part (box) from the global image
                                    x1 = int(roadsign_location_boxes[0][i][1]*input_image.shape[1])
                                    x2 = int(roadsign_location_boxes[0][i][3]*input_image.shape[1])
                                    y1 = int(roadsign_location_boxes[0][i][0]*input_image.shape[0])
                                    y2 = int(roadsign_location_boxes[0][i][2]*input_image.shape[0])
                                    # compute width of the road sign in pixels
                                    w = x2 - x1
                                    # detected stop sign : add width to list of widths for this sign
                                    if (result == 1):
                                        detected_stop = True
                                        width_stop.append(w)
                                    # detected search sign : add width to list of widths for this sign
                                    elif (result == 2):
                                        detected_search = True
                                        width_search.append(w)
                                    # detected prohibited way sign
                                    elif(result == 3):
                                        print("i have found a PROHIBITED SIGN")
    
                            # save sign width (minimum bounding box around the sign)
                            if (detected_stop):
                                print("i have found a STOP SIGN !")
                                w = min(width_stop)
                                self.setWidthStopGlobalVariable(width=w)       
                            if (detected_search):
                                print("i have found a SEARCH SIGN !")
                                w = min(width_search)
                                self.setWidthSearchGlobalVariable(width=w)  
                            if (not detected_stop and not detected_search):
                                # increase no detection counter
                                no_roadsign_detection_count += 1
                                # if "no_roadsign_detection_count" after multiple try, then set widths to 0
                                if (no_roadsign_detection_count >= 2):
                                    self.setWidthStopGlobalVariable(width=0)
                                    self.setWidthSearchGlobalVariable(width=0)  
         
                        #------------------------------------------------------------------------
                        #    Object detection (small, medium, big) if we are in "search" mode"
                        #------------------------------------------------------------------------
                        elif (self.check_searchmode):
                            # process prediction from search mode model and get scores + corresponding boxes FOR SEARCH MODE MODEL
                            output_image = input_image.copy()
                            search_location_boxes, search_location_score, search_location_classes = self.search_model.detectObjectsFromNumpyArray(search_sess, output_image)
                            """
                                Next part of code :
                                    - save each box where the probability score is better than a defined threshold 
                                If DEBUG is True, print, save and show image with all the boxes rendered. 
                            """
                            # assume we start with no detection
                            result = 0
                            detected_small = False
                            detected_medium = False
                            detected_big = False
                            width_small = []
                            width_medium  = []
                            width_big = []
                            # search for road sign in all the found boxes (in the corresponding model
                            for i in range(search_location_boxes.shape[1]):
                                # detect a road sign if probability score of a box is better than a defined threshold
                                if (search_location_boxes[0][i][0] != 0 and search_location_score[0][i] > 0.4):
                                    # assign "no_roadsign_detection_count" to 0  because a road sign has been detected
                                    no_object_detection_count = 0
                                    # find prediction result from collected data (boxes, score for each box and class for each box)
                                    result = int(search_location_classes[0][i])             
                                    # capture interesting part (box) from the global image
                                    x1 = int(search_location_boxes[0][i][1]*output_image.shape[1])
                                    x2 = int(search_location_boxes[0][i][3]*output_image.shape[1])
                                    y1 = int(search_location_boxes[0][i][0]*output_image.shape[0])
                                    y2 = int(search_location_boxes[0][i][2]*output_image.shape[0])
                                    # compute width of the road sign in pixels
                                    w = x2 - x1
                                    # detected small object : add width to list of widths for this type of object
                                    if (result == 1):
                                        detected_small = True
                                        width_small.append(w)
                                    # detected medium object : add width to list of widths for this type of object
                                    elif (result == 2):
                                        detected_medium = True
                                        width_medium.append(w)
                                    # detected big object : add width to list of widths for this type of object
                                    elif (result == 3):
                                        detected_big = True
                                        width_big.append(w)
                                        
                            # save image with rectangle boxes around detected objects (if objects are detected), as global variable
                            if (detected_small or detected_medium or detected_big):
                                self.setImageSearchObjectGlobalVariable(image=output_image)
                            # save object width (minimum bounding box around the object)
                            if (detected_small):
                                print ("i have found a small sized object !")
                                w = min(width_small)
                                self.setWidthSmallObjectGlobalVariable(width=w)       
                            if (detected_medium):
                                print ("i have found a medium sized object !")
                                w = min(detected_medium)
                                self.setWidthMediumObjectGlobalVariable(width=w)  
                            if (detected_big):
                                print ("i have found a big sized object !")
                                w = min(width_big)
                                self.setWidthBigObjectGlobalVariable(width=w)             
                            if (not detected_small and not detected_medium and not detected_big):
                                # increase no detection counter
                                no_object_detection_count += 1
                                # if "no_object_detection_count" after multiple try, then set widths to 0
                                if (no_object_detection_count >= 5):
                                    self.setWidthSmallObjectGlobalVariable(width=0)
                                    self.setWidthMediumObjectGlobalVariable(width=0)
                                    self.setWidthBigObjectGlobalVariable(width=0)     
        pass
        
        
        # capture a 'dummy' image and process both roadsign and search detection for test. Return nothings
    def initTestDetection(self, camera=None, roadsign_model=None, search_model=None, roadsign_sess=None, search_sess=None):
        try:
            print("testing Camera capture, then roadsign detection and search mode detection with defined models")
            camera.captureImage()
            input_image = camera.readImageAsNumpyArray(save=False)
            print("\tCamera capture and save : \t\t\t\t[  OK  ]")
            roadsign_location_boxes, roadsign_location_score, roadsign_location_classes = roadsign_model.detectObjectsFromNumpyArray(roadsign_sess, input_image.copy())
            print("\tRoadsign detection using defined model : \t\t[  OK  ]")
            search_location_boxes, search_location_score, search_location_classes = search_model.detectObjectsFromNumpyArray(search_sess, input_image.copy())
            print("\tSearch mode detection using defined model : \t\t[  OK  ]")
        except Exception as e:
            print("[ERROR] : Couldn't run detection test. Exception : {}".format(str(e)))
        pass
    
    # Next functions are useful to get or modify datas from shared (global) variables
    def getConnectedGlobalVariable(self):
        sharedRessources.lockConnectedDevice.acquire()
        check_connected = sharedRessources.connectedDevice
        sharedRessources.lockConnectedDevice.release()
        return check_connected
        pass
    
    def getSearchModeGlobalVariable(self):
        sharedRessources.lockSearchModeActivated.acquire()
        check_searchmode = sharedRessources.searchModeActivated
        sharedRessources.lockSearchModeActivated.release()
        return check_searchmode
        pass

    def setWidthStopGlobalVariable(self, width=0):
        sharedRessources.lockWidthStop.acquire()
        sharedRessources.widthStop = width
        sharedRessources.lockWidthStop.release()
        pass
    
    def setWidthSearchGlobalVariable(self, width=0):
        sharedRessources.lockWidthSearch.acquire()
        sharedRessources.widthSearch = width
        sharedRessources.lockWidthSearch.release()
        pass
    
    def setWidthSmallObjectGlobalVariable(self, width=0):
        sharedRessources.lockWidthSmall.acquire()
        sharedRessources.widthSmall = width
        sharedRessources.lockWidthSmall.release()
        pass
    
    def setWidthMediumObjectGlobalVariable(self, width=0): 
        sharedRessources.lockWidthMedium.acquire()
        sharedRessources.widthMedium = width
        sharedRessources.lockWidthMedium.release()
        pass
    
    def setWidthBigObjectGlobalVariable(self, width=0):
        sharedRessources.lockWidthBig.acquire()
        sharedRessources.widthBig = width
        sharedRessources.lockWidthBig.release()
        pass
    
    def setImageSearchObjectGlobalVariable(self, image=np.empty(0)):
        sharedRessources.lockImageSearchObject.acquire()
        sharedRessources.imageSearchObject = image
        sharedRessources.lockImageSearchObject.release()
        pass
    
    
    
    
    
    
    
    
    
    
    
    
    
