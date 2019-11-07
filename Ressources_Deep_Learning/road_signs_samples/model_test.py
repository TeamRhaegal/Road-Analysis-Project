#!/usr/bin/env python

"""

    UNDER CONSTRUCTION :
        VERSION : 1.0.3
        DATE : 2019/11/07

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
import sys, traceback, time

# threads imports
from threading import Thread, Lock

# image processing imports
import numpy as np
from skimage import io, color, exposure, transform
from sklearn.model_selection import train_test_split

#import cv2, picamera
#import picamera

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
from Tkinter import *

"""
    PROGRAM PARAMETERS :
        - NUM_CLASSES : number of different road sign types in the dataset
        - IMG_SIZE_X : input image size (x axis : length)  -> works with raspberry raspicam
        - IMG_SIZE_Y : input image size (y axis : heigh)   -> works with raspberry raspicam
        - SCREEN_SIZE_X : length of the screen (in pixels) where the result window is showed
        - SCREEN_SIZE_Y : heigh of the screen (in pixels) where the result window is showed
        - IMG_SIZE_SQUARE : size of the croped image containing the detected road sign (from the "big" input image)
        - RASPICAM_ENABLE : do you want to use raspicam camera to capture an image and detect road sign in it ? if "false", example image file will be taken
        - DEBUG : Use "debug = true" if you want the program to save captured image at each process (big image, cropped, with histogram equalization...)
        - IMAGE_PATH : path of an example image
"""

NUM_CLASSES = 43
SCREEN_SIZE_X = 1920
SCREEN_SIZE_Y = 1080
IMG_SIZE_X = 1920
IMG_SIZE_Y = 1080
IMG_SIZE_SQUARE = 48
RASPICAM_ENABLE = False
VISUALISATION = True
DEBUG = True
IMAGE_PATH = "test4.ppm"

# result from detected road sign global variable
RESULT = None

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
    Function window_run :
    threaded function (ensure you run it as a separated thread)
    Used to :
        - create a window on the screen
        - configure its size and position

"""
def window_run(threadname, lock):
    # create window
    window = Tk()
    window.title("result : estimated road sign")

    #window.geometry("((0.4)*SCREEN_SIZE_X)x((0.7)*SCREEN_SIZE_Y)+((0.6)*SCREEN_SIZE_X)+((0.2)*SCREEN_SIZE_Y)") #Width x Height
    window.geometry("700x900+1280+360") #Width x Height
    #window.resizable(0,0) # image has constant size
    # create canvas for image display
    canvas = Canvas(window, width = 600, height = 600)
    canvas.pack(side='top', fill='both', expand='yes')

    update_window_content(window, canvas)
    # program is stuck here
    window.mainloop()

"""
    Function show_resultOnWindow :
    Used to :
        - show an image of road sign classified from the train model, and recognised in an input photo

"""
def update_window_content(window, canvas):
    global RESULT
    # get RESULT value
    lock.acquire()
    result = RESULT
    lock.release()
    # show result image on window
    canvas.delete("all")
    if(result != None):
        img = PhotoImage(file=roadsign_types[result][1])
        canvas.create_image(20,20, image=img)
    window.after(1000, update_window_content(window, canvas))



"""
    Function init_camera:
        - init camera parameters
"""
def init_camera():
    # init raspberry camera if the correct mode is chosen
    if (RASPICAM_ENABLE):
        # init raspicam camera
        camera = picamera.PiCamera()
        camera.resolution = (IMG_SIZE_X, IMG_SIZE_Y)

        # print image captured on screen if activated
        if(VISUALISATION):
            camera.start_preview()

        return camera
    else:
        return -1

"""
    function capture_image:
        - capture and return one image from the choosen mode (raspberry camera or example file)
"""
def capture_image():
    # capture image
    if(RASPICAM_ENABLE):
        # capture a first image
        camera.capture("raspicam_captured.ppm")
        # name input image, process it and store it
        img = io.imread("raspicam_captured.ppm")
    else:
        # capture input image from folder and process it
        img = io.imread(IMAGE_PATH)

    return img

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

    # roll color axis (RGB) to axis 0 : NEW IMAGE : (RGB, X, Y) instead of (X, Y, RGB)
    img = np.rollaxis(img,-1)

    return img

"""
    MAIN FUNCTION

"""
if __name__ == "__main__":

    try:
        # create threads
        lock = Lock()

        window_thread = Thread( target=window_run, args=("window thread", lock) )
        window_thread.start()

        # load trained neural network model
        model = load_model('model.h5')

        # init camera instance if RASPICAM_ENABLE = 1
        camera = init_camera()

        while(True):
            # capture one image on raspberry or example image
            input_image = capture_image()

            if(DEBUG):
                io.imsave("0_initial_image.ppm", input_image)

            # pre process image in order to be used by the model
            test_image = preprocess_img(input_image)
            # add one "id" axis at the beginning of the image. Not useful with only one image but required in the trained model
            test_image = np.expand_dims(test_image, axis=0)
            # get RESULT value
            lock.acquire()
            # use the trained model to classify a roadsign in the image
            RESULT = model.predict_classes(test_image)[0]
            result = RESULT
            lock.release()
            # print image of recognised road sign
            print ("----------------------\nthis is the result : {}\n------------------------\n".format(result))
            time.sleep(2)
            pass
        window_thread.join()


    except Exception as e:
        print(traceback.format_exc())
        #print("Error : an exception has been noticed.\nError message : '"+str(e)+"'")
    pass
