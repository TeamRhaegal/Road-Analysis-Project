#!/usr/bin/env python

"""
    CLASSIFICATION.PY

This code allows you to configure and use the road sign classification model.
This model takes as input an image of size "48 x 48" pixels, and writes as output an integer number describing the corresponding class of the road sign (from 0 to 42 because we have 43 classes of panels) : speed limit, stop, prohibited way, etc.

"""

# model load imports
from keras.models import load_model

# image processing imports
from skimage import io, color, exposure, transform
import numpy as np

from keras import backend as K
K.set_image_data_format('channels_first')


"""
    CONSTANTS DEFINITION 
"""
NUM_CLASSES = 43
IMG_SIZE = 48
DEFAULT_MODEL_PATH = "classification_model.h5"


class ClassificationModel(object):
    
    def __init__(self, debug=False):
        self.debug = debug
        pass
    
    """
        load_model : load model in order to be used, to predict the output result
        
        input : model path
        output : model content as variable
    """
    def load_model(self, model_path=DEFAULT_MODEL_PATH):
        self.model = load_model(model_path)
        pass
    
    """
        preprocess_img : transform an input image to make it the best quality possible as input of the classification model
        used to :
        - equalize the histogram (contrast) of the image : (convert to HSV format, then normalize the Y axis (light values), and finally convert back to RGB)
        - crop image to its center (most part of the image)
        - rescale image to IMG_SIZE x IMG_SIZE size.

        input : image (RGB numpy array)
        output : processed image (RGB numpy array)
    """
    def preprocess_img(self, img):
        # save non processed image as local variable
        self.nonprocessed_image = img
        # Histogram normalization in y
        hsv = color.rgb2hsv(img)
        hsv[:,:,2] = exposure.equalize_hist(hsv[:,:,2])     # equalize_hist(image, nbins=256, mask=None) : return image array as HSV : (Hue (degrees), saturation (%), value (%))
        img = color.hsv2rgb(hsv)

        if(self.debug):
            io.imsave("1_image_after_equalizehist.ppm", img)

        # central scrop
        min_side = min(img.shape[:-1])
        centre = img.shape[0]//2, img.shape[1]//2
        img = img[centre[0]-min_side//2:centre[0]+min_side//2,
                centre[1]-min_side//2:centre[1]+min_side//2,
                :]

        if(self.debug):
            io.imsave("2_image_after_centralscrop.ppm", img)

        # rescale to standard size
        img = transform.resize(img, (IMG_SIZE, IMG_SIZE))

        if(self.debug):
            io.imsave("3_image_after_resize.ppm", img)

        # roll color axis (RGB) to axis 0 : NEW IMAGE : (RGB, X, Y) instead of (X, Y, RGB)
        img = np.rollaxis(img,-1)        
        # add one "id" axis at the beginning of the image. Not useful with only one image but required in the trained model
        img = np.expand_dims(img, axis=0)
        # save processed image in local variable
        self.processed_img = img
        return img
        pass
    
    """
        predict_result : predict ONE possible result: the class with the biggest "probability" (score) for a specific image
    
        input : image (3D numpy array : height x length x RGB
        output : INT containing the most likely recognized class
    """
    def predict_result(self, img):
        self.result = self.model.predict_classes(img)[0]
        return self.result
        pass
    
    """
        show probabilities for each class, for an image. 
        Allows to see if a class is clearly recognized or if it is not that precise.
        
        input : image (3D numpy array : height x length x RGB
        output : numpy array of predictions (classes / scores)
    """
    def show_result_probabilities(self, img):
        self.result_probabilities = self.model.predict(img)
        return self.result_probabilities
        pass
        
    
    
    
    
    

        
