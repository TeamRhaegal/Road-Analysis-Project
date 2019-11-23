#!/usr/bin/env python

import imutils
import cv2
import time
import numpy as np


template_filepath = "images/roadsigns_representation/00014/stop.png"

camera = cv2.VideoCapture(0)
camera.set(3, 1920)
camera.set(4, 1080)
cv2.namedWindow('image',cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', 1280,720)
    

if __name__ == "__main__":
    
    # load template file.
    template = cv2.imread(template_filepath)
    grayTemplate = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    cannyTemplate = cv2.Canny(template, 50, 200)
    (tH, tW) = template.shape[:2]

    while(1): 
        # load the image, convert it to grayscale, and initialize the
        # bookkeeping variable to keep track of the matched region
        return_value, image = camera.read()
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        found = None

        # loop over the scales of the image
        for scale in np.linspace(0.2, 1.0, 10)[::-1]:
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resizedImage = imutils.resize(grayImage, width = int(grayImage.shape[1] * scale))
            r = grayImage.shape[1] / float(resizedImage.shape[1])

            # if the resized image is smaller than the template, then break
            # from the loop
            if resizedImage.shape[0] < tH or resizedImage.shape[1] < tW:
                break
            
            # detect edges in the resized, grayscale image and apply template
            # matching to find the template in the image
            cannyImage = cv2.Canny(resizedImage, 50, 200)
            result = cv2.matchTemplate(cannyImage, cannyTemplate, cv2.TM_CCOEFF_NORMED)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            # if we have found a new maximum correlation value, then update
            # the bookkeeping variable
            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

        # unpack the bookkeeping variable and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio
        (_, maxLoc, r) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

        # draw a bounding box around the detected result and display the image
        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
        cv2.imshow("Image", image)
        cv2.waitKey(1)
