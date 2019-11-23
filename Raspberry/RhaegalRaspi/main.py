from bleGattServer.bleThreads import BLETransmitterThread,BLEServer
from threading import Event
import command as C
import os
import time
import can
	
def main():
    print('\n\rCAN Rx test')
    print('Bring up CAN0....')

    # Bring up can0 interface at 500kbps
    os.system("sudo /sbin/ip link set can0 up type can bitrate 400000")
    time.sleep(0.1)
    print('Press CTL-C to exit')
    try:
        bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
    except OSError:
        print('Cannot find PiCAN board.')
        exit()
    
    
    runRaspiCodeEvent = Event()
    runRaspiCodeEvent.set()
	
    #command part
    threadsense = C.MySensor(bus,runRaspiCodeEvent)
    threadcom = C.MyCommand(bus,runRaspiCodeEvent)
    
	#BLE part
    bleServer = BLEServer()
    bleTransmitterThread= BLETransmitterThread(bleServer,runRaspiCodeEvent) #for transmitting messages to the server
    
	

    try:
        threadsense.start()
        threadcom.start()
        TransmitterThread.start()
        Server.run() ############################### a la fin
				
    except KeyboardInterrupt:
        print ('Attempting to close all threads')
        runRaspiCodeEvent.clear()
        bleTransmitterThread.join()
        print ('All threads successfully closed')
        bleServer.quit()
        msg = can.Message(arbitration_id=MOT,data=[0x00, 0x00, 0x00,0,0,0,0,0],extended_id=False)
        bus.send(msg)
        os.system("sudo /sbin/ip link set can0 down")
		
if __name__ == '__main__':
    main()

