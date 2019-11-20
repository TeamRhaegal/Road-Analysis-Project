#!/usr/bin/env python

import numpy as np
import cv2
import os, time
from roadsign_python_source import raspicam

filename = "images/demo_imgs/location_demo/raspicam_capture.ppm"

<<<<<<< HEAD
time.sleep(5)

camera = raspicam.Raspicam()
camera.capture_image()
location_input_image = camera.read_image_as_numpy_array(save=True)


img = cv2.imread("raspicam_capture.ppm", 1)
#img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
=======
img = cv2.imread(filename, 1)
#img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

>>>>>>> cc38e8b6a298677198e5177f2615a8eb25de82d1
grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow("grayImage", grayImage)
cv2.waitKey(0)

<<<<<<< HEAD
edges = cv2.Canny(grayImage,0,300)
cv2.imshow("edges", edges)
cv2.waitKey(0)

=======
#edges = cv2.Canny(grayImage,0,400)
#cv2.imshow("edges", edges)
#cv2.waitKey(0)

blurredImage = cv2.GaussianBlur(grayImage, (5, 5), 0)
cv2.imshow("blurred Image", blurredImage)
cv2.waitKey(0)

thresh1 = cv2.threshold(blurredImage, 60, 255, cv2.THRESH_BINARY)[1]
cv2.imshow("treshold", thresh1)
cv2.waitKey(0)


>>>>>>> cc38e8b6a298677198e5177f2615a8eb25de82d1
#ret,thresh1 = cv2.threshold(img[:,:,0], 0, 255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
#cv2.imshow('thresh1', thresh1)
#cv2.waitKey(0)

<<<<<<< HEAD
_, contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
=======
_, contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
>>>>>>> cc38e8b6a298677198e5177f2615a8eb25de82d1

for cnt in contours:
    approx = cv2.approxPolyDP(cnt,0.03*cv2.arcLength(cnt,True),True)
    if len(approx)>7 and len(approx)<10:
        print len(approx)
        print "octagon"
        cv2.drawContours(img, [cnt], 0, (0, 255, 0), 6)

cv2.imshow('sign', img)       
cv2.waitKey(0)
cv2.destroyAllWindows()
