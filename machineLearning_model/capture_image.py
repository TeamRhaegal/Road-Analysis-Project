#!/usr/bin/env python
# coding=utf-8

# imports 
import os, sys, time,keyboard, can
from skimage import io as skio
from threading import Event, Thread, Lock
from picamera import PiCamera
from picamera.array import PiRGBArray
from PIL import Image
import cv2
import numpy as np

# import raspicam 
#sys.path.append('roadsign_python_source/')
#from roadsign_python_source import raspicam
    
folderpath = "dataset_original/"
MOT = 0x010    

class MyCapture(Thread):

    def __init__(self,camera,bus):
        Thread.__init__(self)
        self.camera = camera
        self.bus = bus


    def run(self):
        counter = 189
        y1 = 0
        y2 = 1080
        x1 = 800
        x2 = 1920
        CMD = 100
        while True : 
            if keyboard.is_pressed('space') :

             for i in range(3): 
                    # capture, process and save image
                    try : 
                        self.camera.capture(folderpath+str(counter)+".jpg", format="jpeg")
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
                        self.camera.close()
                        CMD = CMD + 0x80
                        msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, CMD,0,0,0,0,0],extended_id=False)
                        self.bus.send(msg)
                        
                        

class MyRun(Thread):

    def __init__(self,bus):
        Thread.__init__(self)
        self.bus = bus


    def run(self):
        
        while True : 
            if keyboard.is_pressed('r') :
                CMD_V = 60 + 0x80
                msg = can.Message(arbitration_id=MOT,data=[CMD_V, CMD_V, 0x00,0,0,0,0,0],extended_id=False)
                self.bus.send(msg)
                
                time.sleep(5)
                
                msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
                self.bus.send(msg)

                
           
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
     # define camera instance  
    try:
        #camera = Raspicam.camera
        camera = PiCamera()
        camera.resolution = (1640,922)

        
        
        threadcapture = MyCapture(camera,bus)
        threadrun=MyRun(bus)
        threadrun.start()
        threadcapture.start()

    except KeyboardInterrupt:
        threadcapture.join()
        threadcapture.join()
        pass


        

    
  

