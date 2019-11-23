from bleGattServer.bleThreads import BLEServerThread, BLETransmitterThread
from Threading import Event

"""import bleGattServer.utils.service as serv
import bleGattServer.utils.serverSettings as sett
import sharedRessources as r
import time"""

	
def main():
	runRaspiCodeEvent = Event()
	runRaspiCodeEvent.set()
	
	#BLE part
	bleServerThread = BLEServer(runRaspiCodeEvent) #server thread

	bleTransmitterThread= BLETransmitterThread(bleServerThread,runRaspiCodeEvent) #for transmitting messages to the server
	
	#Test Transmitter
	
	""""while (not r.listMessagesReceived):
		time.sleep(1)
	r.lockConnectedDevice.acquire()
	r.connectedDevice = True
	r.lockConnectedDevice.release()"""


	try:
		bleServerThread.start()
		bleTransmitterThread.start()
		
		
	except KeyboardInterrupt:
		print ('Attempting to close all threads')
        runRaspiCodeEvent.clear()
        bleServerThread.join()
        bleTransmitterThread.join()
        print ('All threads successfully closed')
		
if __name__ == '__main__':
    main()

