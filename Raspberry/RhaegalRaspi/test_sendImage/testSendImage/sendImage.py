# -*- coding: utf-8 -*-
#!/usr/bin/env python
import cv2
from threading import Thread
import time
import sharedRessources as R

IMAGE_PATH = "/home/pi/Documents/projet_SIEC/Road-Analysis-Project/Raspberry/RhaegalRaspi/test_sendImage/testSendImage/266.jpg"

class SendImageThread(Thread):
    def __init__(self, runEvent):
        Thread.__init__(self)
        self.runEvent= runEvent
        
    def run(self):
        flag = 0
        while self.runEvent.isSet():
            R.lockConnectedDevice.acquire()
            check_connected = R.connectedDevice
            R.lockConnectedDevice.release()
            
            if(check_connected and flag==0):
                time.sleep(1)
                shared_image = cv2.imread(IMAGE_PATH)
                encodedImage = cv2.imencode('.jpg', shared_image)[1].tobytes()
                             
                for i in range (0,309):
                    R.lockImagePartsToSend.acquire()
                    R.listImagePartsToSend.append(bytearray(encodedImage[900*i:(900*i)+900]))
                    R.lockImagePartsToSend.release()
                    time.sleep(0.3)
                R.lockImagePartsToSend.acquire()
                R.listImagePartsToSend.append(bytearray(encodedImage[900*i:-1]))
                R.lockImagePartsToSend.release()
                
                flag = 1
            time.sleep(0.5)
                
                
    
    
