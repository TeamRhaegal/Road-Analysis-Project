from threading import Event, Thread
from bleGattServer.bleThreads import BLETransmitterThread,BLEServer
import carControl.canControllerThread as C
import roadSignDetection.roadsign_detector as detection
import messageManagement.messageFromIHMManager as msgManager
from messageManagement.messageToIHMManager import BatteryLevelThread, SpeedThread, EmergencyStopThread
import os, sys
	
def main():   
    
    runRaspiCodeEvent = Event()
    runRaspiCodeEvent.set()
	
    #control part
    canControllerThread = C.CanControllerThread(runRaspiCodeEvent)
    
	#BLE part
    bleServer = BLEServer()
    bleTransmitterThread= BLETransmitterThread(bleServer,runRaspiCodeEvent) #for transmitting messages to the server
    
    # roadsign detection part
    thread_roadsign_detector = Thread(target=detection.roadsign_detector, args=(runRaspiCodeEvent,))
    
    #message management part
    messageFromIHMThread = msgManager.MessageFromIHMThread(runRaspiCodeEvent)
    batteryLevelThread = BatteryLevelThread(runRaspiCodeEvent)
    speedLevelThread = SpeedThread(runRaspiCodeEvent)
    emergencyStopThread = EmergencyStopThread(runRaspiCodeEvent)
    
    try:
        canControllerThread.daemon = True
        bleTransmitterThread.daemon = True
        thread_roadsign_detector.daemon = True
        messageFromIHMThread.daemon = True
        batteryLevelThread.daemon = True
        speedLevelThread.daemon = True
        emergencyStopThread.daemon = True
        
        
        canControllerThread.start()
        bleTransmitterThread.start()
        thread_roadsign_detector.start()
        messageFromIHMThread.start()
        batteryLevelThread.start()
        speedLevelThread.start()
        emergencyStopThread.start()
        bleServer.run() ##################################################################################################### a la fin
				
    except KeyboardInterrupt:
        print ('Attempting to close all threads')
        runRaspiCodeEvent.clear()
        canControllerThread.join()
        bleTransmitterThread.join()
        thread_roadsign_detector.join()
        messageFromIHMThread.join()
        batteryLevelThread
        speedLevelThread
        emergencyStopThread
    
        print ('All threads successfully closed')
        bleServer.quit()
        os.system("sudo find . -type f -name \"*.pyc\" -delete")
        sys.exit(0)

if __name__ == '__main__':
    main()

