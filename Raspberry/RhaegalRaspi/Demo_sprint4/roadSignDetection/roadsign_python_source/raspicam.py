#!/usr/bin/env python

"""
    RASPICAM.PY

This code defines a Raspicam class that allows you to configure the camera of the Raspberry Pi (named Raspicam), which offers to capture photos or videos, and save them or not.
images are captured and saved as PPM files (if enabled)

"""

from picamera import PiCamera
from picamera.array import PiRGBArray
from skimage import io as skio
from PIL import Image
import cv2
import numpy as np

class Raspicam(object):

    def __init__(self, resolution = (1640,922), save=False, preview=False):
        # create raspicam instance
        self.camera = PiCamera()
        self.resolution = resolution
        self.save = save
        # init camera resolution
        self.set_resolution(resolution)
        # init stream variable (contains the image at different times as BYTES (no image format specified))
        self.stream = PiRGBArray(self.camera)
        # check if preview option is True and if it is the case, start camera preview (only useful for debugging purposes
        if(preview):
            self.enable_preview()
        pass
    
    """
        set_resolution : modify camera resolution property with defined tupple parameter (resolution x, y)
        
        input : resolution : X, Y tupple
    """
    def set_resolution(self, resolution=(1640,922)):
        self.camera.resolution = (resolution[0], resolution[1])
        pass
    
    """
        capture_image : capture one image in our stream variable and eventually save it as ppm file (if enabled)
        
        input : save boolean value
    """
    def capture_image(self):
        self.camera.capture(self.stream, format="rgb", use_video_port=True)
        pass
     
    """
        read_image_as_numpy_array : return image as classic RGB numpy array
        
        output : image as numpy array
    """
    def read_image_as_numpy_array(self, save=False):
        #self.stream.seek(0)
        image = self.stream.array
        #data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
        #image = cv2.imdecode(data, 1)
        #image = image[:, :, ::-1]   # return image as RGB format and not BGR 
        if (save):
            skio.imsave("raspicam_capture.ppm", image)
            
        self.stream.truncate()
        self.stream.seek(0)
        return image
        pass
     
    """
        read current image as PIL IMAGE format (not numpy array) 
        
        output : image as PIL image variable
    """
    def read_image_as_pil(self):
        self.stream.seek(0)
        return Image.open(self.stream)
        pass
    
    """
        show_image : brutal way to show current capture as image. Only useful for debug, you should use QT window file instead (in the same folder)
    """
    def show_image(self):
        self.stream.seek(0)
        image = Image.open(self.stream)
        image.show()
        pass
      
    """
        enable_preview : show a camera preview if decided by the user
    """
    def enable_preview(self):
        self.camera.start_preview()
        pass
        
    """
        disable_preview : close the camera vision (preview window) if decided by the user
    """
    def disable_preview(self):
        self.camera.stop_preview()
        pass
    
