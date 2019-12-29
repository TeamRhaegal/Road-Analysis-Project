from threading import Event, Thread
from bleGattServer.bleThreads import BLETransmitterThread,BLEServer
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
    
    # roadsign and ojbects detection part
    thread_object_detector = detection.ObjectDetector(runRaspiCodeEvent)
    
    #message management part
    messageFromIHMThread = msgManager.MessageFromIHMThread(runRaspiCodeEvent)
    batteryLevelThread = BatteryLevelThread(runRaspiCodeEvent)
    speedLevelThread = SpeedThread(runRaspiCodeEvent)
    emergencyStopThread = EmergencyStopThread(runRaspiCodeEvent)
    signNotificationThread = SignNotificationThread(runRaspiCodeEvent)
    
    try:
        canControllerThread.daemon = True
        bleTransmitterThread.daemon = True
        thread_object_detector.daemon = True
        messageFromIHMThread.daemon = True
        batteryLevelThread.daemon = True
        speedLevelThread.daemon = True
        emergencyStopThread.daemon = True
        signNotificationThread.daemon = True
        
        canControllerThread.start()
        bleTransmitterThread.start()
        thread_object_detector.start()
        messageFromIHMThread.start()
        batteryLevelThread.start()
        speedLevelThread.start()
        emergencyStopThread.start()
        signNotificationThread.start()
        bleServer.run() ##################################################################################################### a la fin
				
    except KeyboardInterrupt:
        print ('Attempting to close all threads')
        runRaspiCodeEvent.clear()
        canControllerThread.join()
        bleTransmitterThread.join()
        thread_object_detector.join()
        messageFromIHMThread.join()
        batteryLevelThread.join()
        speedLevelThread.join()
        emergencyStopThread.join()
        signNotificationThread.join()
    
        print ('All threads successfully closed')
        bleServer.quit()
        os.system("sudo find . -type f -name \"*.pyc\" -delete")
        sys.exit(0)

if __name__ == '__main__':
    main()

