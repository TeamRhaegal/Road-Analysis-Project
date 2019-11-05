#!/usr/bin/env python

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

# number of different signs in the dataset
NUM_CLASSES = 43
# image size we want (lenght X height) : The larger the image (high resolution), the longer the calculations will be.
IMG_SIZE_X = 1920
IMG_SIZE_Y = 1080

IMG_SIZE_SQUARE = 48

# do you want to use raspicam camera to capture an image and detect road sign in it ?
# if "false", example image file will be taken
RASPICAM_ENABLE = False
# do you want the raspberry to print the images captured on screen ?
RASPICAM_PREVIEW = False

# Specify image path if you want to try the road sign recognition without raspicam camera.
IMAGE_PATH = "/home/vincent/Documents/images_samples/FullIJCNN2013/00086.ppm"

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

    # central scrop
    min_side = min(img.shape[:-1])
    centre = img.shape[0]//2, img.shape[1]//2
    img = img[centre[0]-min_side//2:centre[0]+min_side//2,
              centre[1]-min_side//2:centre[1]+min_side//2,
              :]

    # rescale to standard size
    img = transform.resize(img, (IMG_SIZE_SQUARE, IMG_SIZE_SQUARE))

    # roll color axis to axis 0
    img = np.rollaxis(img,-1)

    return img


if __name__ == "__main__":

    try:
        # load trained neural network model
        model = load_model('model.h5')

        if(RASPICAM_ENABLE):
            # init raspicam camera
            camera = picamera.PiCamera()
            camera.resolution = (IMG_SIZE_X, IMG_SIZE_Y)

            # print image captured on screen if activated
            if(RASPICAM_PREVIEW):
                camera.start_preview()

            # capture a first image
            camera.capture("raspicam_captured.ppm")
            # name input image, process it and store it
            input_image = io.imread("raspicam_captured.ppm")

        else:
            # capture input image from folder and process it
            input_image = io.imread(IMAGE_PATH)

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

    except Exception as e:
        print("Error : an exception has been noticed.\nError message : '"+str(e)+"'")
    pass
