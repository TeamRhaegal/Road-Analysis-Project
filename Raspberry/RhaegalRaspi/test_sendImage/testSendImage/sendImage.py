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
                reconstitueBytes = []
                
                
                for i in range (0,309):
                    #R.constructMsgToIHM("img",encodedImage[900*i:(900*i)+900])
                    reconstitueBytes = reconstitueBytes + encodedImage[900*i:(900*i)+900]
                #R.constructMsgToIHM("img",encodedImage[900*i:-1])
                reconstitueBytes = reconstitueBytes + encodedImage[900*i:-1]
                
                flag = 1
            time.sleep(0.5)
                
                
    
    
