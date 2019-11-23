#!/usr/bin/env python

import numpy as np
import cv2
import os

filename = "images/demo_imgs/location_demo/raspicam_capture.ppm"

img = cv2.imread(filename, 1)
#img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow("grayImage", grayImage)
cv2.waitKey(0)

#edges = cv2.Canny(grayImage,0,400)
#cv2.imshow("edges", edges)
#cv2.waitKey(0)

blurredImage = cv2.GaussianBlur(grayImage, (5, 5), 0)
cv2.imshow("blurred Image", blurredImage)
cv2.waitKey(0)

thresh1 = cv2.threshold(blurredImage, 60, 255, cv2.THRESH_BINARY)[1]
cv2.imshow("treshold", thresh1)
cv2.waitKey(0)


#ret,thresh1 = cv2.threshold(img[:,:,0], 0, 255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
#cv2.imshow('thresh1', thresh1)
#cv2.waitKey(0)

_, contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    approx = cv2.approxPolyDP(cnt,0.03*cv2.arcLength(cnt,True),True)
    if len(approx)>7 and len(approx)<10:
        print len(approx)
        print "octagon"
        cv2.drawContours(img, [cnt], 0, (0, 255, 0), 6)

cv2.imshow('sign', img)       
cv2.waitKey(0)
cv2.destroyAllWindows()
