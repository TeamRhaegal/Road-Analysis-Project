#!/usr/bin/env python
# coding=utf-8

# imports 
import os, sys, time,keyboard, can
sys.dont_write_bytecode = True
from skimage import io as skio
from threading import Event, Thread, Lock
from picamera import PiCamera
from picamera.array import PiRGBArray
from PIL import Image
import cv2
import numpy as np
import random

# import raspicam 
#sys.path.append('roadsign_python_source/')
#from roadsign_python_source import raspicam
    
folderpath = "new_images_search/"
MOT = 0x010    

class MyCapture(Thread):

    def __init__(self, camera, bus, runEvent):
        Thread.__init__(self)
        self.runEvent = runEvent
        self.camera = camera
        self.bus = bus


    def run(self):
        counter = 0
        rnd = random.Random()
        n1 = rnd.randint(0,10000)
        n2 = rnd.randint(0,10000)
        n3 = rnd.randint(0,10000)
        y1 = 0
        y2 = 1080
        x1 = 800
        x2 = 1920
        CMD = 100
        while (self.runEvent.isSet()) : 
                
                try:
                        
                        if keyboard.is_pressed('space') :
                                for i in range(3): 
                                        # capture, process and save image
                                        try : 
                                                self.camera.capture(folderpath+str(n1)+"_"+str(n2)+"_"+str(n3)+"_"+str(counter)+".jpg", format="jpeg")
                                                print(counter)
                                                '''image = self.stream.array

                                                #data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
                                                #image = cv2.imdecode(data, 1)
                                                #image = image[:, :, ::-1]   # return image as RGB format and not BGR 
                                                #if (save):
                                                #    skio.imsave("raspicam_capture.ppm", image)

                                                self.stream.truncate()
                                                self.stream.seek(0)

                                                #image = self.camera.read_image_as_numpy_array(save=False)

                                                image = image[y1:y2 , x1:x2]
                                                skio.imsave(folderpath+str(counter)+".rgb", image)
                                                print ("saved image number {}".format(counter))
                                                '''
                                                counter += 1
                                                time.sleep(1)
                                        except Exception as e:
                                                print ("ERROR : there is an exception : {}".format(str(e)))
                                                self.camera.close()
                                                CMD = CMD + 0x80
                                                msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, CMD,0,0,0,0,0],extended_id=False)
                                                self.bus.send(msg)
                except KeyboardInterrupt:
                        print ("j'me casse")

                        

class MyRun(Thread):

    def __init__(self, bus, runEvent):
        Thread.__init__(self)
        self.runEvent = runEvent
        self.bus = bus

    def run(self):
        
        while (self.runEvent.isSet()) : 
                try:
                        if keyboard.is_pressed('r') :
                                CMD_V = 60 + 0x80
                                msg = can.Message(arbitration_id=MOT,data=[CMD_V, CMD_V, 0x00,0,0,0,0,0],extended_id=False)
                                self.bus.send(msg)

                                time.sleep(5)

                                msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
                                self.bus.send(msg)
                                
                except KeyboardInterrupt:
                        print ("ntm")

if __name__ == "__main__":
    print('\n\rCAN Rx test')
    print('Bring up CAN0....')

    # Bring up can0 interface at 500kbps
    os.system("sudo /sbin/ip link set can0 up type can bitrate 400000")
    print('Press CTL-C to exit')
    try:
        bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
    except OSError:
        print('Cannot find PiCAN board.')
        exit()

    runEvent = Event()
    runEvent.set()
    
    # define camera instance  
    try:
        camera = PiCamera()
        camera.resolution = (300,300)
        
        # thread definition
        threadcapture = MyCapture(camera, bus, runEvent)
        threadrun= MyRun(bus, runEvent)
        # daemonize threads
        #threadcapture.daemon = True
        #threadrun.daemon = True
        # start threads
        threadrun.start()
        threadcapture.start()

    except KeyboardInterrupt:
        runEvent.clear()
        print ("arret arret ARRET ARRETT")
        threadcapture.join()
        threadrun.join()
        sys.exit(0)
        pass


        

    
  

