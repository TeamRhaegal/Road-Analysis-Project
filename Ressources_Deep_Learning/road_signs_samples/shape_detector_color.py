#!/usr/bin/env python

# import the necessary packages
import imutils
import cv2
import time
import numpy as np

class ShapeDetector(object):
    
    def __init__(self):
        pass

    def detect(self, c):
        # initialize the shape name and approximate the contour
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.0* peri, True)
        
        # if the shape is a triangle, it will have 3 vertices
        """
        if len(approx) == 3:
            shape = "triangle"
        """
        # if the shape has 4 vertices, it is either a square or
        # a rectangle
        """
        elif len(approx) == 4:
            # compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)

            # a square will have an aspect ratio that is approximately
            # equal to one, otherwise, the shape is a rectangle
            shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
        """
        
        # if approx size is 8, we have an octagon (stop sign for example)
        if len(approx) == 8: 
            shape = "octagon"
            
        # otherwise, we assume the shape is a circle
        """
        else:
            shape = "circle"
        """
        # return the name of the shape
        return shape


filename = "images/demo_imgs/location_demo/raspicam_capture.ppm"


if __name__=="__main__" : 
    sd = ShapeDetector()
    camera = cv2.VideoCapture(0)
    camera.set(3, 1380)
    camera.set(4, 800)
    cv2.namedWindow('image',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', 1280,720)
    # load the image and resize it to a smaller factor so that
    # the shapes can be approximated better

    while(True):
        #image = cv2.imread(filename)
        
        # load camera and read image
        return_value, image = camera.read()
        
        # convert to HSV format, then apply red filter to detect red road signs
        hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        low_red = np.array([161, 155, 84])
        high_red = np.array([179, 255, 255])
        red_mask = cv2.inRange(hsvImage, low_red, high_red)
        red = cv2.bitwise_and(image, image, mask=red_mask)
        

        
        #cv2.imshow('image', cannyImage)       
        #cv2.waitKey(0)
        
        """
        # find contours in the thresholded image
        contours = cv2.findContours(red.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        # loop over the contours
        for c in contours:
            # first, detect areas larger than minimal size and thiner than maximal size
            area = cv2.contourArea(c)
            if (area >= 500  and area <= 7000):
                print ("areas : {}".format(area))
                # compute the center of the contour, then detect the name of the
                # shape using only the contour
                M = cv2.moments(c)
                
                if(M["m00"] != 0):
                    cX = int((M["m10"] / M["m00"]) * ratio)
                    cY = int((M["m01"] / M["m00"]) * ratio)
                    shape = sd.detect(c)
                    
                    # multiply the contour (x, y)-coordinates by the resize ratio,
                    # then draw the contours and the name of the shape on the image
                    if (shape != "unidentified"):
                        c = c.astype("float")
                        c *= ratio
                        c = c.astype("int")
                        cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                        cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # show the output image
        cv2.imshow("image", image)
        cv2.waitKey(1)
        """

        cv2.imshow("image", red)
        cv2.waitKey(1)
      #  cv2.destroyAllWindows()
