#!/usr/bin/env python

# system imports
import os
import h5py     # h5py allows to save trained models in HDF5 file format : more information here : https://www.h5py.org/
import sys, traceback, time, psutil

# threads imports
from threading import Thread, Lock

# image processing imports
import numpy as np
from skimage import io, color, exposure, transform, filters, feature, img_as_ubyte, measure, segmentation
from skimage.future import graph
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
DEBUG = False

R_drawposition = 0
G_drawposition = 0
B_drawposition = 255

if __name__ == "__main__":
    try:
        init_image = io.imread(IMAGE_PATH)
        img = init_image

        if (DEBUG):
            np.set_printoptions(threshold=sys.maxsize)
            print(img)
            print("\n\n\tArray shape : {}".format(img.shape))

        # Histogram normalization in y
        hsv = color.rgb2hsv(img)
        hsv[:,:,2] = exposure.equalize_hist(hsv[:,:,2])     # equalize_hist(image, nbins=256, mask=None) : return image array as HSV : (Hue (degrees), saturation (%), value (%))
        img = color.hsv2rgb(hsv)

        """
            color threshold
        """
        labels1 = segmentation.slic(img, compactness=30, n_segments=400)
        g = graph.rag_mean_color(img, labels1)
        labels2 = graph.cut_threshold(labels1, g, 29)
        img = color.label2rgb(labels2, img, kind='avg')
        io.imsave("1_after_color_threshold.ppm", img)

        img = color.rgb2gray(img)
        io.imsave("2_after_greyscale.ppm", img)

        img1 = feature.canny(img, sigma=1)
        img1 = img_as_ubyte(img1)
        io.imsave("3_after_canny_edge_sigma1.ppm", img1)

        img3 = feature.canny(img, sigma=3)
        img3 = img_as_ubyte(img3)
        io.imsave("3_after_canny_edge_sigma3.ppm", img3)

        """
        start = (1000, 300)
        end = (1300, 400)
        rr, cc = rectangle(start, end=end, extent=None, shape=None)

        if (DEBUG):
            print(rr)
            print(cc)

        draw_image = init_image

        draw_image[cc, rr, 0] = R_drawposition
        draw_image[cc, rr, 1] = G_drawposition
        draw_image[cc, rr, 2] = B_drawposition

        io.imsave("4_after_drawing_rectangle.ppm", draw_image)
        """

        """
        radius = [40, 50]
        hspaces = transform.hough_circle(img1, radius)
        accum, cx, cy, rad = transform.hough_circle_peaks(hspaces, [radius,], min_xdistance=20, min_ydistance=20, threshold=None, num_peaks=None, total_num_peaks=None, normalize=False)

        print ("CX : {}    , CY : {}".format(cx, cy))
        print ("Accum = {}".format(accum))
        print ("rad = {}".format(rad))

        start = (cx-30, cy-30)
        end = (cx+30, cy+30)
        rr, cc = rectangle(start, end=end, extent=None, shape=None)
        """


    except Exception as e:
        print(traceback.format_exc())
        #print("Error : an exception has been noticed.\nError message : '"+str(e)+"'")
    pass
