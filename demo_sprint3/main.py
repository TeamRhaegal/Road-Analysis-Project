from threading import Event, Thread, Lock
from bleGattServer.bleThreads import BLETransmitterThread,BLEServer
import carCommand.command as C
import roadSignDetection.roadsign_detector as detection
import threadManagement.messageFromIHMManager as msgManager
import os
import can
	
def main():
    # Bring up can0 interface at 500kbps
    os.system("sudo /sbin/ip link set can0 up type can bitrate 400000")
    try:
        bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
    except OSError:
        print('Cannot find PiCAN board.')
        exit()
    
    
    runRaspiCodeEvent = Event()
    runEmergencyEvent = Event()
    runRaspiCodeEvent.set()
	
    #command part
    threadsense = C.MySensor(bus,runRaspiCodeEvent,runEmergencyEvent)
    threadcom = C.MyCommand(bus,runRaspiCodeEvent,runEmergencyEvent)
    
	#BLE part
    bleServer = BLEServer()
    bleTransmitterThread= BLETransmitterThread(bleServer,runRaspiCodeEvent) #for transmitting messages to the server
    
    # roadsign detection part
    thread_roadsign_detector = Thread(target=detection.roadsign_detector, args=(runRaspiCodeEvent,))
    
    #seprate the Message
    messageFromIHMThread = msgManager.MessageFromIHMThread(runRaspiCodeEvent)
    
    
    try:
        threadsense.start()
        threadcom.start()
        bleTransmitterThread.start()
        thread_roadsign_detector.start()
        messageFromIHMThread.start()
        bleServer.run() ##################################################################################################### a la fin
				
    except KeyboardInterrupt:
        print ('Attempting to close all threads')
        runRaspiCodeEvent.clear()
        threadsense.join()
        threadcom.join()
        bleTransmitterThread.join()
        thread_roadsign_detector.join()
        messageFromIHMThread.join()
    
        print ('All threads successfully closed')
        bleServer.quit()
        os.system("sudo find . -type f -name \"*.pyc\" -delete")

if __name__ == '__main__':
    main()

