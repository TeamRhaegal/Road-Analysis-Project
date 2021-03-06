#!/usr/bin/env python
# coding=utf-8

hello = """
    ------------------------------------------------------------------------------
        MODEL STATISTICS TESTER : 
            - uses defined model to test multiple images from a folder
            - process detection, then show result for each input image 
    ------------------------------------------------------------------------------\n\n
    """
print(hello)

# import libraries
import os, sys, time
print("importing libraries")
start = time.time()
sys.dont_write_bytecode=True
# image processing imports
from skimage import io
import cv2, imutils, glob
# arrays processing imports
import numpy as np
import tensorflow as tf
# hardware and machine learning imports
import location_machinelearning
print("imported libraries : time taken : {}".format(time.time()-start))

"""
    Define different paths for input model...
"""
# path to configuration model file : '.config' file
PATH_TO_MODEL = "/home/pi/Documents/projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/demo_release/roadSignDetection/machinelearning_model/search_300_300_pipeline.config"
# Path to frozen detection graph. This is the actual model that is used for the object detection : '.pb' file
PATH_TO_CKPT = "/home/pi/Documents/projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/demo_release/roadSignDetection/machinelearning_model/search_300_300_frozen_inference_graph.pb"
# List of the strings that is used to add correct label for each box : '.pbtxt' file
PATH_TO_LABELMAP = "/home/pi/Documents/projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/demo_release/roadSignDetection/machinelearning_model/search_300_300_labelmap.pbtxt"
# Number of classes to detect
NUM_CLASSES = 3

"""
    define path for input folder
"""
FOLDERNAME = "/home/pi/Documents/projet_SIEC/Road-Analysis-Project/machineLearning_model/new_images_search/" 
IMAGE_FOLDER = glob.glob(FOLDERNAME+"*.jpg")
print ("image folder : {}".format(IMAGE_FOLDER))
if __name__ == '__main__':
    
    print("Running object detection statistic test : \nInitializing model...")
    start = time.time()
    testModel = location_machinelearning.LocationModel(debug = True)
    testModelGraph = testModel.loadModel(model_path=PATH_TO_MODEL, ckpt_path=PATH_TO_CKPT, label_path=PATH_TO_LABELMAP, num_classes=NUM_CLASSES)
    print("Initialized hardware and machine learning model. Time taken : {} seconds".format(time.time()-start))
    
    # test program functionning
    image = cv2.imread(IMAGE_FOLDER[0])
   # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    cv2.imshow('object detection', image)
    cv2.waitKey(0)
    
    counter = 1
    
    print("------------------------------------STARTING DETECTION------------------------------------")
    with tf.Session(graph=testModelGraph) as sess: 
        for filename in IMAGE_FOLDER:
            # process detection
            print ("processing new image : {}".format(counter))
            image = cv2.imread(filename)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            location_boxes, location_score, location_classes = testModel.detectObjectsFromNumpyArray(sess, image)
            cv2.waitKey(1)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(FOLDERNAME+"image_with_boarder.jpg", image)
            counter += 1
            #raw_input("Press Enter to continue...")
    pass
