# -*- coding: utf-8 -*-
#!/usr/bin/env python
import cv2
from threading import Thread
import time
import sharedRessources as R
import sys
import base64
import json

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
                print("shared image format : {}".format(shared_image.shape))
                encodedImage = cv2.imencode('.jpg', shared_image)[1].tobytes()
                
                time.sleep(10)
                for i in range (0,309):
                    listImg = self.convertToListInt(bytearray(encodedImage[900*i:(900*i)+900]))
                    if(i==0):
                        print(listImg)
                    listImgStr = json.dumps(listImg)
                    listImgBase64 = base64.b64encode(listImgStr)
                    R.lockImgPartToSend.acquire()
                    R.listImgPartToSend.append(listImgBase64 )
                    R.lockImgPartToSend.release()
                    time.sleep(0.3)
                listImg = self.convertToListInt(bytearray(encodedImage[900*i:-1]))
                listImgStr = json.dumps(listImg)
                listImgBase64 = base64.b64encode(listImgStr)
                R.lockImgPartToSend.acquire()
                R.listImgPartToSend.append(listImgBase64)
                R.lockImgPartToSend.release()
                print("fin")
                
                flag = 1
            time.sleep(0.5)
            
    def convertToListInt(self,imagePart):
        listImg = []
        for i in range(0,len(imagePart)):
            conv = imagePart[i] & 0xFF
            if (conv > 127):
                conv -=256
            listImg.append(conv)
        return listImg
            
                
                
    
    
