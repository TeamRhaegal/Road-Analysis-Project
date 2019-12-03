<<<<<<< HEAD
from bleGattServer.bleThreads import BLETransmitterThread,BLEServer
from threading import Event, Thread, Lock
import command as C
import roadsign_detector as detection
import seprateMessageThread as sm
import os
import time
import can
	
def main():
    print('\n\rCAN Rx test')
    print('Bring up CAN0....')

    # Bring up can0 interface at 500kbps
    os.system("sudo /sbin/ip link set can0 up type can bitrate 400000")
    print('Press CTL-C to exit')
=======
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
>>>>>>> f289d6bf46ff39eb6d76f37f46127629f2a0642a
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
<<<<<<< HEAD
    seprateMessageThread = sm.SeprateMessageThread(runRaspiCodeEvent)
=======
    messageFromIHMThread = msgManager.MessageFromIHMThread(runRaspiCodeEvent)
>>>>>>> f289d6bf46ff39eb6d76f37f46127629f2a0642a
    
    
    try:
        threadsense.start()
        threadcom.start()
        bleTransmitterThread.start()
        thread_roadsign_detector.start()
<<<<<<< HEAD
        seprateMessageThread.start()
=======
        messageFromIHMThread.start()
>>>>>>> f289d6bf46ff39eb6d76f37f46127629f2a0642a
        bleServer.run() ##################################################################################################### a la fin
				
    except KeyboardInterrupt:
        print ('Attempting to close all threads')
        runRaspiCodeEvent.clear()
        threadsense.join()
        threadcom.join()
        bleTransmitterThread.join()
        thread_roadsign_detector.join()
<<<<<<< HEAD
        seprateMessageThread.join()
    
        print ('All threads successfully closed')
        bleServer.quit()
        """msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
        bus.send(msg)
        os.system("sudo /sbin/ip link set can0 down")"""
=======
        messageFromIHMThread.join()
    
        print ('All threads successfully closed')
		bleServer.quit()
		os.system("sudo find . -type f -name \"*.pyc\" -delete")		

>>>>>>> f289d6bf46ff39eb6d76f37f46127629f2a0642a
		
if __name__ == '__main__':
    main()

