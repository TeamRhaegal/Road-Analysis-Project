import numpy as np
import cv2
import os, time
from roadsign_python_source import raspicam

filename = "images/demo_imgs/location_demo/img_0003.ppm"

time.sleep(5)

camera = raspicam.Raspicam()
camera.capture_image()
location_input_image = camera.read_image_as_numpy_array(save=True)


img = cv2.imread("raspicam_capture.ppm", 1)
#img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow("grayImage", grayImage)
cv2.waitKey(0)

edges = cv2.Canny(grayImage,0,300)
cv2.imshow("edges", edges)
cv2.waitKey(0)

#ret,thresh1 = cv2.threshold(img[:,:,0], 0, 255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
#cv2.imshow('thresh1', thresh1)
#cv2.waitKey(0)

_, contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

for cnt in contours:
    approx = cv2.approxPolyDP(cnt,0.03*cv2.arcLength(cnt,True),True)
    print len(approx)
    if len(approx)==8:
        print "octagon"
        cv2.drawContours(img, [cnt], 0, (0, 255, 0), 6)

cv2.imshow('sign', img)       
cv2.waitKey(0)
cv2.destroyAllWindows()
