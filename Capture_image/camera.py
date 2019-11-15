# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 14:07:27 2019

@author: Nicolas
"""

from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.start_preview()
i=0
while True :
    sleep(0.5)
    camera.capture('/home/pi/Desktop/image%s.jpg' % i)
    i=i+1
camera.stop_preview()