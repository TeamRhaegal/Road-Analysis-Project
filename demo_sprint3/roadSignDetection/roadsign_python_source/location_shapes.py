#!/usr/bin/env python
# coding=utf-8

"""
    Program used to detect the location of a stop sign for the moment (and others later depending on the desired shape). 
    The location of the road sign in an image is done using image modification techniques, and using the openCV library (not machine learning)
    The location is returned from the "find_roadsign" function and allows the classification to be focused on the panel. 
"""

# import the necessary packages
import imutils
import cv2
import time
import numpy as np

class LocationShapes(object):
    
    def __init__(self, draw=False):
        self.draw = draw
        
        pass
    
    """
        pre process image before finding contours
    """
    def process_image(self, image):
        self.image = image.copy()
        # resize and process image 
        # convert the resized image to grayscale, blur it slightly,
        # and threshold it
        self.resizedImage = imutils.resize(self.image, width=1920)
        self.ratio = image.shape[0] / float(self.resizedImage.shape[0])
        self.grayImage = cv2.cvtColor(self.resizedImage, cv2.COLOR_BGR2GRAY)
        self.blurredImage = cv2.boxFilter(self.grayImage, 0, (5, 5))
        #thresh1 = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        self.thresh1 = cv2.threshold(self.blurredImage, 240, 255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        # process canny edge detection on it
        self.cannyImage = cv2.Canny(self.thresh1, 50, 500)
    
    """
        process countours from one image and return them
    """
    def process_contours(self):
        # find contours in the thresholded image
        self.contours = cv2.findContours(self.cannyImage.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.contours = imutils.grab_contours(self.contours)
        return self.contours

    """
        depending on some thresholds, return the coordinates of box around shapes in order to process roadsign
    """
    def find_shape_box(self, c):
        # loop over the contours
        # first, detect areas larger than minimal size and thiner than maximal size
        area = cv2.contourArea(c)
        if (area >= 20000 and area <= 100000000000000):
            # compute the center of the contour, then detect the name of the
            # shape using only the contour
            M = cv2.moments(c)
            
            if(M["m00"] != 0):
                #cX = int((M["m10"] / M["m00"]) * self.ratio)
                #cY = int((M["m01"] / M["m00"]) * self.ratio)
                shape = self.detect_shape(c)

                if (shape != "unidentified"):
                    # multiply the contour (x, y)-coordinates by the resize ratio,
                    c = c.astype("float")
                    c *= self.ratio
                    c = c.astype("int")
                    (x,y,w,h) = cv2.boundingRect(c)
                    # then draw the contours and the name of the shape on the image (if object.draw is true)
                    if (self.draw):
                        cv2.rectangle(self.image, (x,y), (x+w,y+h), (0,255,0), 2)
                        """
                        c = c.astype("float")
                        c *= ratio
                        c = c.astype("int")
                        cv2.drawContours(self.image, [c], -1, (0, 255, 0), 2)
                        cv2.putText(self.image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                        """
                        # show the output image
                        cv2.imshow("image", self.image)
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()
                    return x, y, w, h
                else:
                    return -1, -1, -1, -1
            else:
                 return -1, -1, -1, -1
        else:
            return -1, -1, -1, -1
                        
    def detect_shape(self, c):
        # initialize the shape name and approximate the contour
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.01* peri, True)
        
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
        pass
