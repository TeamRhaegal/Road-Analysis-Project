from bleGattServer.bleThreads import BLEServerThread, BLETransmitterThread,BLEServer
from threading import Event

"""import bleGattServer.utils.service as serv
import bleGattServer.utils.serverSettings as sett
import sharedRessources as r
import time"""

	
def main():
	"""runRaspiCodeEvent = Event()
	runRaspiCodeEvent.set()
	
	#BLE part
	bleServerThread = BLEServerThread(runRaspiCodeEvent) #server thread

	#bleTransmitterThread= BLETransmitterThread(bleServerThread,runRaspiCodeEvent) #for transmitting messages to the server
	
	#Test Transmitter"""
	
	""""while (not r.listMessagesReceived):
		time.sleep(1)
	r.lockConnectedDevice.acquire()
	r.connectedDevice = True
	r.lockConnectedDevice.release()"""
	
	bleServer = BLEServer()


	try:
		#bleServerThread.start()
		#bleTransmitterThread.start()
		bleServer.run()
		
		
	except KeyboardInterrupt:
		"""print ('Attempting to close all threads')
        runRaspiCodeEvent.clear()
        bleServerThread.join()
        #bleTransmitterThread.join()
        #print ('All threads successfully closed')"""
		bleServer.quit()
		
if __name__ == '__main__':
    main()

