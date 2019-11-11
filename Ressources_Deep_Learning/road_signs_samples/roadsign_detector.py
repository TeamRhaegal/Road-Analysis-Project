#!/usr/bin/env python

"""

    UNDER CONSTRUCTION :
        VERSION : 1.2
        DATE : 2019/11/11

    PROGRAM OBJECTIVE : Use pre-trained deep learning models to detect and classify traffic signs in an image captured by the raspicam camera. For reasons of format in the datasets used, the images are in "PPM" format (3D matrix : weight x lenght x [RGB]):
        - load and configure 2 deep learning models (neural networks)
                - a "Fast-RCNN" used to locate a road sign in an image
                - a classic CNN used to classify a road sign within different categories (stop, speed limit, prohibited way ...)
        - define specification of the raspberry pi camera (raspicam) : color, save format (ppm), resolution ...
        - capture an image with the raspicam
        - use the location model to detect ROIs (Regions of Interest) around road signs
        - crop the input image to detcted ROIs, then "pre process" it according to the classification model used :
                - normalize its histogram (technique used to adapt contrast)
                - crop image in the center (if not already done)
                - resize the image (extra/interpolation) to the required size for the model input
        - process the croped image to the classification neural network and get the type of road sign found
        - if "DEBUG" option is activated, show a preview of what the camera "sees" and what kind of panel has been recognised
"""

# system imports
import os, sys, traceback, time, psutil
import h5py     # h5py allows to save trained models in HDF5 file format : more information here : https://www.h5py.org/
from io import BytesIO
import tqdm

# threads imports
from threading import Thread, Lock

# image processing imports
import numpy as np
from skimage import io, color, exposure, transform
from sklearn.model_selection import train_test_split
from PIL import Image
import cv2
#import picamera

# model load imports
from keras.models import load_model
import pickle

# general model imports
from keras.layers import Input
from keras.models import Model

# training and test imports
import pandas as pd
from keras.optimizers import SGD
from keras.utils import np_utils
from keras.callbacks import LearningRateScheduler, ModelCheckpoint
from keras import backend as K
K.set_image_data_format('channels_first')

#if K=='tensorflow':
#    keras.backend.set_image_dim_ordering('tf')

# imports for location model
import keras_frcnn.fcnet as nn
from keras_frcnn import config, data_generators
#from keras_frcnn import losses as losses
from keras_frcnn.simple_parser import get_data
import keras_frcnn.roi_helpers as roi_helpers

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
        - LOCATION_MODEL_PICKLE_PATH :
"""

NUM_CLASSES = 43
SCREEN_SIZE_X = 1920
SCREEN_SIZE_Y = 1080
IMG_SIZE_X = 1380
IMG_SIZE_Y = 800
IMG_SIZE_SQUARE = 48
RASPICAM_ENABLE = False
CAMERA_PREVIEW = False
DEBUG = True
IMAGE_PATH = "00082.ppm"
LOCATION_MODEL_PICKLE_PATH = "fcnet_config.pickle"
CLASSIFICATION_MODEL_PATH = "classification_model.h5"

DEMO_LOCATION = True
DEMO_CLASSIFICATION = False

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
    Function init_camera:
        - init camera parameters (camera instance, resolution...)
"""
def init_camera():
    # init raspberry camera if the correct mode is chosen
    if (RASPICAM_ENABLE):
        # init raspicam camera
        camera = picamera.PiCamera()
        camera.resolution = (IMG_SIZE_X, IMG_SIZE_Y)
        # print image captured on screen if activated
        if(CAMERA_PREVIEW):
            camera.start_preview()
        return camera
    else:
        print("\nRASPICAM_ENABLE constant is set at 'False' so we don't use raspicam input but example one\nCheck IMAGE_PATH constant for example image")
        return -1
    pass

"""
    function 'capture_image':
        - capture and return one image from the choosen mode (raspberry camera or example file)
"""
def capture_image(camera):
    # capture image
    if(RASPICAM_ENABLE):
        # capture a first image and convert it to ppm format
        camera.capture("raspicam_capture.rgb")
        im = io.imread("raspicam_capture.rgb")
        io.imsave("raspicam_capture.ppm", im)
        stream = io.imread("raspicam_capture.ppm")
    else:
        # capture input image from folder and process it
        stream = io.imread(IMAGE_PATH)
    return stream
    pass

"""
    Function 'preprocess_img' : used to :
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
    # add one "id" axis at the beginning of the image. Not useful with only one image but required in the trained model
    img = np.expand_dims(img, axis=0)

    return img
    pass


"""
    Function 'show_image':
    show an image put as variable, using skimage (io.imread)
"""
def show_image(image, from_file=False):
    if (from_file):
        img = Image.open(image)
    else:
        img = Image.fromarray(image)
    img.show()
    pass

"""
    Function show_result :
    used to show a representation of detected road sign as a result
"""
def show_result(result):
    img = Image.open(roadsign_types[result][1])
    img.show()
    pass

"""
    Function 'kill_window_process' :
        - Kill all display process (windows)
"""
def kill_window_process():
    for proc in psutil.process_iter():
        if proc.name() == "display":
            proc.kill()

"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

"""
    The next functions are used to format image from the LOCATION Neural Network model in order to retrieve some coordinates, resize images ...
    - "format_img" : formats an image for model prediction
    - "format_img_size" : format the image size depending on pickle configuration
    - "format_img_channels" : formats the image channels depending on pickle configuration
    - "get_real_coordinates" : Method to transform the coordinates of the bounding box to its original size
"""
def format_img(img, C):
    """ formats an image for model prediction based on config """
    img, ratio, fx, fy = format_img_size(img, C)
    img = format_img_channels(img, C)
    return img, ratio, fx, fy

def format_img_size(img, C):
    """ formats the image size based on config """
    img_min_side = float(C.im_size)
    (height, width, _) = img.shape

    if width <= height:
        ratio = img_min_side/width
        new_height = int(ratio * height)
        new_width = int(img_min_side)
    else:
        ratio = img_min_side/height
        new_width = int(ratio * width)
        new_height = int(img_min_side)
    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    fx = width / float(new_width)
    fy = height / float(new_height)
    return img, ratio, fx, fy

def format_img_channels(img, C):
    """ formats the image channels based on config """
    img = img[:, :, (2, 1, 0)]
    img = img.astype(np.float32)
    img[:, :, 0] -= C.img_channel_mean[0]
    img[:, :, 1] -= C.img_channel_mean[1]
    img[:, :, 2] -= C.img_channel_mean[2]
    img /= C.img_scaling_factor
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    return img

def get_real_coordinates(ratio, x1, y1, x2, y2):
    """ Method to transform the coordinates of the bounding box to its original size """
    real_x1 = int(round(x1 // ratio))
    real_y1 = int(round(y1 // ratio))
    real_x2 = int(round(x2 // ratio))
    real_y2 = int(round(y2 // ratio))

    return (real_x1, real_y1, real_x2 ,real_y2)

"""
    Function 'config_location_model' :
    Load and configure Fast-RCNN neural network model from a pickle configuration file (trained model)
    This model is used to detect a roadsign in an image (find xA,yA,xB,yB rectangle arround road signs)
    INPUTS :
        - "pickle_file_path" : configuration file path
    OUTPUTS :
        - C : content of the configuration file
        - model_rpn : Region proposal network model (find semantic regions in the image) in order to find ROIs (regions of interest)
        - model_classifier : Model that find road signs (or objects) with a defined probability in every ROI (regions of interest)
        - model_classifier_only : Model that doesn't classify road signs
"""
def config_location_model(pickle_file_path):
    # configure location model paths
    config_output_filename = LOCATION_MODEL_PICKLE_PATH

    # open configuration file
    with open(config_output_filename, 'rb') as f_in:
        C = pickle.load(f_in)
        import keras_frcnn.fcnet as nn

    class_mapping = C.class_mapping
    if 'bg' not in class_mapping:
        class_mapping['bg'] = len(class_mapping)

    class_mapping = {v: k for k, v in class_mapping.items()}
    print(class_mapping)
    class_to_color = {class_mapping[v]: np.random.randint(0, 255, 3) for v in class_mapping}
    C.num_rois = 32
    print("\nnumber of ROIs : {}".format(C.num_rois))

    input_shape_img = (None, None, 3)
    input_shape_features = (None, None, C.num_features)
    img_input = Input(shape=input_shape_img)
    roi_input = Input(shape=(C.num_rois, 4))
    feature_map_input = Input(shape=input_shape_features)

    # define the base network (zfnet)
    shared_layers = nn.nn_base(img_input, trainable=True)

    # define the RPN, built on the base layers
    num_anchors = len(C.anchor_box_scales) * len(C.anchor_box_ratios)
    rpn_layers = nn.rpn(shared_layers, num_anchors)

    classifier = nn.classifier(feature_map_input, roi_input, C.num_rois, nb_classes=len(class_mapping), trainable=True)

    model_rpn = Model(img_input, rpn_layers)
    model_classifier_only = Model([feature_map_input, roi_input], classifier)

    model_classifier = Model([feature_map_input, roi_input], classifier)

    print('Loading weights from {}'.format(C.model_path))       # model_path specified in config file
    model_rpn.load_weights(C.model_path, by_name=True)
    model_classifier.load_weights(C.model_path, by_name=True)

    model_rpn.compile(optimizer='sgd', loss='mse')
    model_classifier.compile(optimizer='sgd', loss='mse')

    return C, class_mapping, class_to_color, model_rpn, model_classifier, model_classifier_only
    pass

def find_roadsign_in_image(img, C, class_mapping, class_to_color, model_rpn, model_classifier, model_classifier_only):
    # try to localise road sign
    classification_threshold = 0.5		# threshold above which we classify as positive

    X, ratio, fx, fy = format_img(img, C)

    assert K.image_dim_ordering() == 'tf'
    X = np.transpose(X, (0, 2, 3, 1))

    # get the feature maps and output from the RPN
    [Y1, Y2, F] = model_rpn.predict(X)
    # R = bboxes (300 ,4)
    R = roi_helpers.rpn_to_roi(Y1, Y2, C, K.image_dim_ordering(), overlap_thresh=0.7)

    # convert from (x1,y1,x2,y2) to (x,y,w,h)
    R[:, 2] -= R[:, 0]
    R[:, 3] -= R[:, 1]

    # apply the spatial pyramid pooling to the proposed regions
    bboxes = {}
    probs = {}

    for jk in range(R.shape[0]//C.num_rois + 1):    	# R.shape[0] = 300
        ROIs = np.expand_dims(R[C.num_rois*jk:C.num_rois*(jk+1), :], axis=0)
        if ROIs.shape[1] == 0:
            break

        if jk == R.shape[0]//C.num_rois:
            # pad R
            curr_shape = ROIs.shape
            target_shape = (curr_shape[0],C.num_rois,curr_shape[2])
            ROIs_padded = np.zeros(target_shape).astype(ROIs.dtype)
            ROIs_padded[:, :curr_shape[1], :] = ROIs
            ROIs_padded[0, curr_shape[1]:, :] = ROIs[0, 0, :]
            ROIs = ROIs_padded

        # [pred_cls, pred_regr] = model_classifier_only.predict([F, ROIs])
        [pred_cls, pred_regr] = model_classifier.predict([F, ROIs])

        for ii in range(pred_cls.shape[1]):

            if np.max(pred_cls[0, ii, :]) < classification_threshold or np.argmax(pred_cls[0, ii, :]) == (pred_cls.shape[2] - 1):
                pass

            cls_name = class_mapping[np.argmax(pred_cls[0, ii, :])]

            if cls_name not in bboxes:
                bboxes[cls_name] = []
                probs[cls_name] = []

            (x, y, w, h) = ROIs[0, ii, :]

            cls_num = np.argmax(pred_cls[0, ii, :])	 # index of predicted class
            try:
                (tx, ty, tw, th) = pred_regr[0, ii, 4*cls_num:4*(cls_num+1)]
                tx /= C.classifier_regr_std[0]
                ty /= C.classifier_regr_std[1]
                tw /= C.classifier_regr_std[2]
                th /= C.classifier_regr_std[3]
                x, y, w, h = roi_helpers.apply_regr(x, y, w, h, tx, ty, tw, th)
            except:
                pass
            bboxes[cls_name].append([C.rpn_stride*x, C.rpn_stride*y, C.rpn_stride*(x+w), C.rpn_stride*(y+h)])
            probs[cls_name].append(np.max(pred_cls[0, ii, :]))

    bboxes.pop('bg')    # added to avoid plotting background bbox
    probs.pop('bg')     # added to avoid plotting background bbox

    pred_bboxs = []

    for key in bboxes:
        bbox = np.array(bboxes[key])

        new_boxes, new_probs = roi_helpers.non_max_suppression_fast(bbox, np.array(probs[key]), overlap_thresh=0.5)
        for jk in range(new_boxes.shape[0]):
            (x1, y1, x2, y2) = new_boxes[jk, :]

            (real_x1, real_y1, real_x2, real_y2) = get_real_coordinates(ratio, x1, y1, x2, y2)

            cv2.rectangle(img,(real_x1, real_y1), (real_x2, real_y2), (int(class_to_color[key][0]), int(class_to_color[key][1]), int(class_to_color[key][2])),2)

            textLabel = '{}: {}'.format(key, int(100*new_probs[jk]))
            pred_bboxs.append({'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2, 'class': key, 'prob': new_probs[jk]})

            (retval,baseLine) = cv2.getTextSize(textLabel,cv2.FONT_HERSHEY_COMPLEX,1,1)
            textOrg = (real_x1, real_y1-0)

            cv2.rectangle(img, (textOrg[0] - 5,textOrg[1]+baseLine - 5), (textOrg[0]+retval[0] + 5, textOrg[1]-retval[1] - 5), (255, 255, 255), -1)
            cv2.putText(img, textLabel, textOrg, cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 1)

    print("pred_bboxs:", pred_bboxs)
    #print("gt boxes:", img_data['bboxes'])
    cv2.imwrite('results_imgs/result.ppm', img)
    return img, pred_bboxs
    pass

"""
    MAIN FUNCTION : here is where all the code is processed
    WARNING : because of format differences between location model and classification model, please :
        - use : 'K.set_image_data_format('channels_last')' just before using location model functions
        - use : 'K.set_image_data_format('channels_first')' just before using classification model functions
    (it is easier to do that, because we would have to re train the model from 0 if we wanted to solve that problem)
"""
if __name__ == "__main__":

    if (DEMO_LOCATION):
        # configure location deep learning model
        K.set_image_data_format('channels_last')
        C, class_mapping, class_to_color, location_model_rpn, location_model_classifier, location_model_classifier_only  = config_location_model(LOCATION_MODEL_PICKLE_PATH)

    if (DEMO_CLASSIFICATION):
        # configure classification deep learning model
        K.set_image_data_format('channels_first')
        classify_model = load_model('classification_model.h5')

    # init camera specifications (or do nothing if RASPICAM_ENABLE is set to False)
    camera = init_camera()

    if(DEMO_LOCATION):
        input_image = "demo_imgs/location_demo/img_0003.ppm"
    elif(DEMO_CLASSIFICATION):
        input_image = "demo_imgs/classification_demo/img_0004.ppm"

    # close opened windows
    kill_window_process()

    input_image = io.imread(input_image)
    # capture an image from the camera (or use example image if RASPICAM_ENABLE is set to False)
    #input_image = capture_image(camera)
    if (DEBUG):
        show_image(input_image, from_file=False)

    if (DEMO_LOCATION):
        K.set_image_data_format('channels_last')
        result_localisation_image, pred_bboxs = find_roadsign_in_image(input_image, C, class_mapping, class_to_color, location_model_rpn, location_model_classifier, location_model_classifier_only)
        if (DEBUG):
            show_image(result_localisation_image)


    if (DEMO_CLASSIFICATION):
        input_image = preprocess_img(input_image)
        K.set_image_data_format('channels_first')
        result = classify_model.predict_classes(input_image)[0]
        if (DEBUG):
            show_result(result)

    time.sleep(5)

    pass
