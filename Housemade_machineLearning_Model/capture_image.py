#!/usr/bin/env python
# coding=utf-8

# imports 
import os, sys, time
from skimage import io as skio

# import raspicam 
sys.path.append('roadsign_python_source/')
from roadsign_python_source import raspicam
    
folderpath = "dataset/"    
    
if __name__ == "__main__":
    # define camera instance    
    camera = raspicam.Raspicam()
    # define 
    counter = 0
    
    y1 = 0
    y2 = 1080
    x1 = 0
    x2 = 1920
    
    
    while (counter < 100): 
        # capture, process and save image
        camera.capture_image()
        image = camera.read_image_as_numpy_array(save=False)
        
        image = image[y1:y2 , x1:x2]
        skio.imsave(folderpath+str(counter)+".rgb", image)
        print ("saved image number {}".format(counter))
            
        counter += 1
        time.sleep(10)
