#!/usr/bin/env python

"""
    RASPICAM.PY

This code defines a Raspicam class that allows you to configure the camera of the Raspberry Pi (named Raspicam), which offers to capture photos or videos, and save them or not.

"""

# import libraries
from picamera import PiCamera
from picamera.array import PiRGBArray
from skimage import io as skio
from PIL import Image
import cv2
import numpy as np

"""
    You can create an instance of this class to open and conntrol the camera in the front of the car
"""
class Raspicam(object):

    def __init__(self, resolution = (300,300), save=False, preview=False):
        # create raspicam instance
        self.camera = PiCamera()
        self.resolution = resolution
        self.save = save
        # init camera resolution
        self.setResolution(resolution)
        # init stream variable (contains the image at different times as BYTES (no image format specified))
        self.stream = PiRGBArray(self.camera)
        # check if preview option is True and if it is the case, start camera preview (only useful for debugging purposes
        if(preview):
            self.enablePreview()
        pass
    """
        setResolution : modify camera resolution property with defined tupple parameter (resolution x, y)
        input : resolution : X, Y tupple
    """
    def setResolution(self, resolution=(300,300)):
        self.camera.resolution = (resolution[0], resolution[1])
        pass
    """
        captureImage : capture one image in our stream variable 
    """
    def captureImage(self):
        self.camera.capture(self.stream, format="rgb", use_video_port=True)
        pass
    """
        readImageAsNumpyArray : return image as classic RGB numpy array 
        output : image as numpy array
    """
    def readImageAsNumpyArray(self, save=False):
        #self.stream.seek(0)
        image = self.stream.array
        if (save):
            skio.imsave("raspicam_capture.ppm", image)
            
        self.stream.truncate()
        self.stream.seek(0)
        return image
        pass
    """
        read current image as PIL IMAGE format (not numpy array but a dedicated PIL class) 
        output : image as PIL image variable
    """
    def readImageAsPil(self):
        self.stream.seek(0)
        return Image.open(self.stream)
        pass
    """
        showImage : show current capture as image in a dedicated window. Only useful for debug
    """
    def showImage(self):
        self.stream.seek(0)
        image = Image.open(self.stream)
        image.show()
        pass
    """
        enablePreview : show a camera preview in real time 
    """
    def enablePreview(self):
        self.camera.start_preview()
        pass
    """
        disablePreview : close the camera vision (preview window)
    """
    def disablePreview(self):
        self.camera.stop_preview()
        pass
    
