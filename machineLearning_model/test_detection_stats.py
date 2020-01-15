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
PATH_TO_MODEL = "/home/vincent/Documents/INSA/5A/Projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/demo_release/roadSignDetection/machinelearning_model/roadsign_300_300_pipeline.config"
# Path to frozen detection graph. This is the actual model that is used for the object detection : '.pb' file
PATH_TO_CKPT = "/home/vincent/Documents/INSA/5A/Projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/demo_release/roadSignDetection/machinelearning_model/roadsign_300_300_frozen_inference_graph.pb"
# List of the strings that is used to add correct label for each box : '.pbtxt' file
PATH_TO_LABELMAP = "/home/vincent/Documents/INSA/5A/Projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/demo_release/roadSignDetection/machinelearning_model/roadsign_300_300_labelmap.pbtxt"
# Number of classes to detect
NUM_CLASSES = 2

"""
    define path for input folder
"""
FOLDERNAME = "/home/vincent/Documents/INSA/5A/Projet_SIEC/Road-Analysis-Project/machineLearning_model/training_roadsign/images/test/" 
IMAGE_FOLDER = glob.glob(FOLDERNAME+"*.jpg")

if __name__ == '__main__':
    
    print("Running object detection statistic test : \nInitializing model...")
    start = time.time()
    testModel = location_machinelearning.LocationModel(debug = True)
    testModelGraph = testModel.loadModel(model_path=PATH_TO_MODEL, ckpt_path=PATH_TO_CKPT, label_path=PATH_TO_LABELMAP, num_classes=NUM_CLASSES)
    print("Initialized hardware and machine learning model. Time taken : {} seconds".format(time.time()-start))
    
    print("------------------------------------STARTING DETECTION------------------------------------")
    with tf.Session(graph=testModelGraph) as sess: 
        for filename in IMAGE_FOLDER:
            # process detection
            image = cv2.imread(filename)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            location_boxes, location_score, location_classes = testModel.detectObjectsFromNumpyArray(sess, image.copy())
            raw_input("Press Enter to continue...")
    pass
