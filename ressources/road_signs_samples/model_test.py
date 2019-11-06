#!/usr/bin/env python

"""

    UNDER CONSTRUCTION :
        VERSION : 1.0.1
        DATE : 2019/11/06

"""


"""
    Program objective :
        - define specification of the raspberry pi camera (raspicam) : color, save format (ppm), resolution ...
        - capture an image with the raspicam
        - do an algorithm to detect the position of a road sign (if there is one) in the image
        - crop the image to the defined position, then "pre process" it according to the model used :
                - normalize its histogram (technique used to adapt contrast)
                - crop image in the center (if not already done)
                - resize the image (extra/interpolation) to the required size for the model input
        - process the croped image to the neural network and get the type of road sign found
        - if "DEBUG" option is activated, show a preview of what the camera "sees" and what kind of panel has been recognised
"""

# system imports
import os
import h5py     # h5py allows to save trained models in HDF5 file format : more information here : https://www.h5py.org/

# image processing imports
import numpy as np
from skimage import io, color, exposure, transform
from sklearn.model_selection import train_test_split

#import cv2, picamera

# model training and processing imports
from keras.models import load_model

# training and test imports
import pandas as pd
from keras.optimizers import SGD
from keras.utils import np_utils
from keras.callbacks import LearningRateScheduler, ModelCheckpoint
from keras import backend as K
K.set_image_data_format('channels_first')

# graphic interface
from tkinter import *

"""
    PROGRAM PARAMETERS :
        - NUM_CLASSES : number of different road sign types in the dataset
        - IMG_SIZE_X : input image size (x axis : length)  -> works with raspberry raspicam
        - IMG_SIZE_Y : input image size (y axis : heigh)   -> works with raspberry raspicam
        - IMG_SIZE_SQUARE : size of the croped image containing the detected road sign (from the "big" input image)
        - RASPICAM_ENABLE : do you want to use raspicam camera to capture an image and detect road sign in it ? if "false", example image file will be taken
        - DEBUG : Use "debug = true" if you want the program to save captured image at each process (big image, cropped, with histogram equalization...)
        - IMAGE_PATH :
"""

NUM_CLASSES = 43
IMG_SIZE_X = 1920
IMG_SIZE_Y = 1080
IMG_SIZE_SQUARE = 48
RASPICAM_ENABLE = False
VISUALISATION = False
DEBUG = True
IMAGE_PATH = "/home/vincent/Documents/images_samples/FullIJCNN2013/00086.ppm"

"""
    OBJECT INSTANCES AND CONSTANTS
        - roadsign_types : meaning of each 43 classes of road signs, and a path to an image of each road sign


"""

roadsign_types = [  ["speed limit 20",                              "roadsigns_representation/00000/speed_limit_20.ppm"],
                    ["speed limit 30",                              "roadsigns_representation/00001/speed_limit_30.ppm"],
                    ["speed limit 50",                              "roadsigns_representation/00002/speed_limit_50.ppm"],
                    ["speed limit 60",                              "roadsigns_representation/00003/speed_limit_60.ppm"],
                    ["speed limit 70",                              "roadsigns_representation/00004/speed_limit_70.ppm"],
                    ["speed limit 80",                              "roadsigns_representation/00005/speed_limit_80.ppm"],
                    ["end of speed limit 80",                       "roadsigns_representation/00006/end_speed_limit_80.ppm"],
                    ["speed limit 100",                             "roadsigns_representation/00007/speed_limit_100.ppm"],
                    ["speed limit 120",                             "roadsigns_representation/00008/speed_limit_120.ppm"],
                    ["forbidden to overtake car",                   "roadsigns_representation/00009/forbidden_overtake.ppm"],
                    ["forbidden for truck to overtake",             "roadsigns_representation/00010/forbidden_overtake_truck.ppm"],
                    ["priority for the next cross",                 "roadsigns_representation/00011/priority_road_sign.ppm"],
                    ["priority road",                               "roadsigns_representation/00012/priority_sign.ppm"],
                    ["give way",                                    "roadsigns_representation/00013/let_priority_sign.ppm"],
                    ["stop",                                        "roadsigns_representation/00014/stop.ppm"],
                    ["forbidden for motored vehicles",              "roadsigns_representation/00015/forbidden_motored_vehicle.ppm"],
                    ["forbidden for trucks",                        "roadsigns_representation/00016/forbidden_truck.ppm"],
                    ["prohibited way",                              "roadsigns_representation/00017/prohibited_way.ppm"],
                    ["warning",                                     "roadsigns_representation/00018/warning.ppm"],
                    ["dangerous turn left",                         "roadsigns_representation/00019/dangerous_turn_left.ppm"],
                    ["dangerous turn right",                        "roadsigns_representation/00020/dangerous_turn_right.ppm"],
                    ["multiple turn left",                          "roadsigns_representation/00021/multiple_turn_left.ppm"],
                    ["bump ahead",                                  "roadsigns_representation/00022/bump.ppm"],
                    ["warning slippy road",                         "roadsigns_representation/00023/warning_slip.ppm"],
                    ["tighter way right",                           "roadsigns_representation/00024/tighter_way_right.ppm"],
                    ["road works ahead",                            "roadsigns_representation/00025/roadworks.ppm"],
                    ["traffic light ahead",                         "roadsigns_representation/00026/traffic_light.ppm"],
                    ["warning pedestrian",                          "roadsigns_representation/00027/warning_pedestrian.ppm"],
                    ["warning childs",                              "roadsigns_representation/00028/warning_pedestrian_child.ppm"],
                    ["warning bycicles",                            "roadsigns_representation/00029/warning_bycicle.ppm"],
                    ["presence of snow",                            "roadsigns_representation/00030/warning_snow.ppm"],
                    ["warning wild animals",                        "roadsigns_representation/00031/warning_wild_animal.ppm"],
                    ["enf of last speed limit",                     "roadsigns_representation/00032/end_last_speed_limit.ppm"],
                    ["indication : turn right",                     "roadsigns_representation/00033/indication_right_turn.ppm"],
                    ["indication : turn left",                      "roadsigns_representation/00034/indication_left_turn.ppm"],
                    ["indication : straight line",                  "roadsigns_representation/00035/indication_straight_line.ppm"],
                    ["indication : straight + right",               "roadsigns_representation/00036/indication_straight_right.ppm"],
                    ["indication : straight + left",                "roadsigns_representation/00037/indication_straight_left.ppm"],
                    ["go right side",                               "roadsigns_representation/00038/go_right_mandatory.ppm"],
                    ["go left side",                                "roadsigns_representation/00039/go_left_mandatory.ppm"],
                    ["roundabout ahead",                            "roadsigns_representation/00040/roundabout.ppm"],
                    ["end of forbidden overtake for cars",          "roadsigns_representation/00041/end_forbidden_overtake.ppm"],
                    ["end of forbidden overtake for trucks",        "roadsigns_representation/00042/end_forbidden_overtake_truck.ppm"]
                ]

"""
    Function init_viewWindow :
    Used to :
        - create a window on the screen
        - configure its size and position

    the window will then be used to print image of detected road signs in real time
"""

def init_viewWindow():
    # create window
    window = Tk()
    window.geometry("700x900+1280+360") #Width x Height



    return window


"""
    Function used to :
        - equalize the histogram (contrast) of the image : (convert to HSV format, then normalize the Y axis (light values), and finally convert back to RGB)
        - crop image to its center (most part of the image)
        - rescale image to IMG_SIZE x IMG_SIZE size.

    input : image (RGB numpy array)
    output : processed image (RGB numpy array)
"""
def preprocess_img(img):
    # Histogram normalization in y
    hsv = color.rgb2hsv(img)
    hsv[:,:,2] = exposure.equalize_hist(hsv[:,:,2])     # equalize_hist(image, nbins=256, mask=None) : return image array as HSV : (Hue (degrees), saturation (%), value (%))
    img = color.hsv2rgb(hsv)

    if(DEBUG):
        io.imsave("1_image_after_equalizehist.ppm", img)

    # central scrop
    min_side = min(img.shape[:-1])
    centre = img.shape[0]//2, img.shape[1]//2
    img = img[centre[0]-min_side//2:centre[0]+min_side//2,
              centre[1]-min_side//2:centre[1]+min_side//2,
              :]

    if(DEBUG):
        io.imsave("2_image_after_centralscrop.ppm", img)

    # rescale to standard size
    img = transform.resize(img, (IMG_SIZE_SQUARE, IMG_SIZE_SQUARE))

    if(DEBUG):
        io.imsave("3_image_after_resize.ppm", img)

    # roll color axis to axis 0
    img = np.rollaxis(img,-1)

    if(DEBUG):
        io.imsave("4_image_after_rollaxis.ppm", img)

    return img





"""
    MAIN FUNCTION

"""
if __name__ == "__main__":

    try:
        # create window on screen
        result_window = init_viewWindow()
        # load trained neural network model
        model = load_model('model.h5')

        if(RASPICAM_ENABLE):
            # init raspicam camera
            camera = picamera.PiCamera()
            camera.resolution = (IMG_SIZE_X, IMG_SIZE_Y)

            # print image captured on screen if activated
            if(VISUALISATION):
                camera.start_preview()

            # capture a first image
            camera.capture("raspicam_captured.ppm")
            # name input image, process it and store it
            input_image = io.imread("raspicam_captured.ppm")

        else:
            # capture input image from folder and process it
            input_image = io.imread(IMAGE_PATH)

        if(DEBUG):
            io.imsave("0_initial_image.ppm", input_image)

        test_image = preprocess_img(input_image)
        """
        left = 48
        top = 48
        width = 0
        heigh = 0

        while (heigh < 1032):
            while(width < 1920):
                test_image = preprocess_img(input_image[width:width+left, heigh:heigh+top])
                test_image = np.expand_dims(test_image, axis=0)
                result = model.predict_classes(test_image)
                print("\nClass detected : {}, coordinates : {}, {}".format(result, width+left, heigh+top))
                width = width + left
            width = 0
            heigh = heigh + top
        """
    except Exception as e:
        print("Error : an exception has been noticed.\nError message : '"+str(e)+"'")
    pass
