import numpy as np
import cv2
import os

filename = "images/demo_imgs/location_demo/img_0003.ppm"

img = cv2.imread(filename, 1)
grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow("grayImage", grayImage)
cv2.waitKey(0)

#edges = cv2.Canny(grayImage,0,300)
#cv2.imshow("edges", edges)
#cv2.waitKey(0)

ret,thresh1 = cv2.threshold(img[:,:,0], 0, 255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
cv2.imshow('thresh1', thresh1)
cv2.waitKey(0)

_, contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

for cnt in contours:
    approx = cv2.approxPolyDP(cnt,0.03*cv2.arcLength(cnt,True),True)
    print len(approx)
    if len(approx)==8:
        print "octagon"
        cv2.drawContours(img, [cnt], 0, (0, 255, 0), 6)

cv2.imshow('sign', img)       
cv2.waitKey(0)
cv2.destroyAllWindows()
