# -*- coding: utf-8 -*-
#!/usr/bin/env python

from threading import Event, Thread
from bleGattServer.bleThreads import BLETransmitterThread, BLEServer
import carControl.canControllerThreads as C
import roadSignDetection.object_detector as detection
import messageManagement.messageFromIHMManager as msgManager
from messageManagement.messageToIHMManager import BatteryLevelThread, SpeedThread, EmergencyStopThread, SignNotificationThread
import os, sys

def main():   
    
    runRaspiCodeEvent = Event()
    runRaspiCodeEvent.set()
    
    #control part
    canControllerThread = C.CanControllerThread(runRaspiCodeEvent)
    
    #BLE part
    bleServer = BLEServer()
    bleTransmitterThread= BLETransmitterThread(bleServer,runRaspiCodeEvent) #for transmitting messages to the server
    
    # roadsign and objects detection part
    objectDetectorThread = detection.ObjectDetector(runRaspiCodeEvent)
    
    #message management part
    messageFromIHMThread = msgManager.MessageFromIHMThread(runRaspiCodeEvent)
    batteryLevelThread = BatteryLevelThread(runRaspiCodeEvent)
    speedLevelThread = SpeedThread(runRaspiCodeEvent)
    emergencyStopThread = EmergencyStopThread(runRaspiCodeEvent)
    signNotificationThread = SignNotificationThread(runRaspiCodeEvent)
    searchObjectNotificationThread = SearchObjectNotificationThread(runRaspiCodeEvent)
    
    try:
        canControllerThread.daemon = True
        bleTransmitterThread.daemon = True
        objectDetectorThread.daemon = True
        messageFromIHMThread.daemon = True
        batteryLevelThread.daemon = True
        speedLevelThread.daemon = True
        emergencyStopThread.daemon = True
        signNotificationThread.daemon = True
        searchObjectNotificationThread.daemon = True
        
        canControllerThread.start()
        bleTransmitterThread.start()
        objectDetectorThread.start()
        messageFromIHMThread.start()
        batteryLevelThread.start()
        speedLevelThread.start()
        emergencyStopThread.start()
        signNotificationThread.start()
        searchObjectNotificationThread.start()
        bleServer.run() ##################################################################################################### a la fin

    except KeyboardInterrupt:
        print ('Attempting to close all threads')
        runRaspiCodeEvent.clear()
        canControllerThread.join()
        bleTransmitterThread.join()
        objectDetectorThread.join()
        messageFromIHMThread.join()
        batteryLevelThread.join()
        speedLevelThread.join()
        emergencyStopThread.join()
        signNotificationThread.join()
        searchObjectNotificationThread.join()
    
        print ('All threads successfully closed')
        bleServer.quit()
        os.system("sudo find . -type f -name \"*.pyc\" -delete")
        sys.exit(0)

if __name__ == '__main__':
    main()

