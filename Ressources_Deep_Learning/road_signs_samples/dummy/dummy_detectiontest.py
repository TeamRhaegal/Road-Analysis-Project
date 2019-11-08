#!/usr/bin/env python

# system imports
import os
import h5py     # h5py allows to save trained models in HDF5 file format : more information here : https://www.h5py.org/
import sys, traceback, time, psutil

# threads imports
from threading import Thread, Lock

# image processing imports
import numpy as np
from skimage import io, color, exposure, transform, filters, feature, img_as_ubyte, measure
from skimage.draw import rectangle

from sklearn.model_selection import train_test_split

# image drawing imports
from PIL import Image
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


"""
    constants and global variables
"""
IMAGE_PATH = "test_image.ppm"



if __name__ == "__main__":
    try:
        init_image = io.imread(IMAGE_PATH)
        img = init_image

        """
        # gaussian smoothing
        img = filters.gaussian(img, sigma=1, output=None, mode='nearest', cval=0, multichannel=None, preserve_range=True, truncate=4.0)
        io.imsave("1_after_gaussian.ppm", img)
        """

        img = color.rgb2gray(img)
        io.imsave("2_after_greyscale.ppm", img)

        img1 = feature.canny(img, sigma=1)
        img1 = img_as_ubyte(img1)
        io.imsave("3_after_canny_edge_sigma1.ppm", img1)

        img3 = feature.canny(img, sigma=3)
        img3 = img_as_ubyte(img3)
        io.imsave("3_after_canny_edge_sigma3.ppm", img3)

        radius = [40, 50]
        hspaces = transform.hough_circle(img1, radius)
        accum, cx, cy, rad = transform.hough_circle_peaks(hspaces, [radius,], min_xdistance=20, min_ydistance=20, threshold=None, num_peaks=None, total_num_peaks=None, normalize=False)

        print ("CX : {}    , CY : {}".format(cx, cy))
        print ("Accum = {}".format(accum))
        print ("rad = {}".format(rad))

        start = (cx-30, cy-30)
        end = (cx+30, cy+30)
        rr, cc = rectangle(start, end=end, extent=None, shape=None)

    except Exception as e:
        print(traceback.format_exc())
        #print("Error : an exception has been noticed.\nError message : '"+str(e)+"'")
    pass
