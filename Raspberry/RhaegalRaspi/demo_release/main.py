# -*- coding: utf-8 -*-

from threading import Event, Thread
from bleGattServer.bleThreads import BLETransmitterThread, BLEServer
import carControl.canControllerThreads as C
from roadSignDetection.object_detector import ObjectDetector
import messageManagement.messageFromIHMManager as msgManager
from messageManagement.messageToIHMManager import SpeedThread, EmergencyStopThread, SignNotificationThread, SearchObjectNotificationThread
from debugTraceback import Debug
import os, sys
sys.dont_write_bytecode = True

def main():   
    
    runRaspiCodeEvent = Event()
    runRaspiCodeEvent.set()

    #control part
    canControllerThread = C.CanControllerThread(runRaspiCodeEvent)
    
    #BLE part
    bleServer = BLEServer()
    bleTransmitterThread= BLETransmitterThread(bleServer,runRaspiCodeEvent) #for transmitting messages to the server

    # roadsign and objects detection part
    objectDetectorThread = ObjectDetector(runRaspiCodeEvent)
    
    #message management part
    messageFromIHMThread = msgManager.MessageFromIHMThread(runRaspiCodeEvent)
    speedLevelThread = SpeedThread(runRaspiCodeEvent)
    emergencyStopThread = EmergencyStopThread(runRaspiCodeEvent)
    signNotificationThread = SignNotificationThread(runRaspiCodeEvent)
    searchObjectNotificationThread = SearchObjectNotificationThread(runRaspiCodeEvent)
    
    try:
        canControllerThread.start()
        bleTransmitterThread.start()
        objectDetectorThread.start()
        messageFromIHMThread.start()
        speedLevelThread.start()
        emergencyStopThread.start()
        signNotificationThread.start()
        searchObjectNotificationThread.start()
        bleServer.run() ########################################################### to be run after all threads have started
    
    except KeyboardInterrupt:
        print ('Attempting to close all threads')
        runRaspiCodeEvent.clear()
        canControllerThread.join()
        print ("closed canController thread")
        bleTransmitterThread.join()
        print ("closed bleTransmitter thread")
        objectDetectorThread.join()
        print ("closed objectDetector thread")
        messageFromIHMThread.join()
        print ("closed messageFromIHM thread")
        speedLevelThread.join()
        print ("closed speedLevel thread")
        emergencyStopThread.join()
        print ("closed emergencyStop thread")
        signNotificationThread.join()
        print ("closed signNotification thread")
        searchObjectNotificationThread.join()
    
        print ('All threads successfully closed')
        bleServer.quit()
        os.system("sudo find . -type f -name \"*.pyc\" -delete")
        sys.exit(0)


    """
    except Exception as e:
        print ("error has occured : {}".format(str(e)))
        #bleServer.quit()
        os.system("sudo find . -type f -name \"*.pyc\" -delete")
        sys.exit(0)
    """
if __name__ == '__main__':
    main()

