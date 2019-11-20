#!/usr/bin/env python

import os, sys, traceback, time, psutil
from skimage import io, color, exposure, transform
import picamera

if __name__=="__main__":
	camera = picamera.PiCamera()
        camera.resolution = (1380, 800)
	camera.capture("raspicam_capture.gif")
	pass
