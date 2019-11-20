from bleGattServer.bleThreads import BLEServer, BLETransmitterThread
import bleGattServer.utils.service as serv
import bleGattServer.utils.serverSettings as sett
import sharedRessources as r
import time

	
def main():
	#BLE part
	bleServer = BLEServer() #server thread

	bleTransmitterThread= BLETransmitterThread(bleServer) #for transmitting messages to the server
	bleTransmitterThread.daemon=True
	
	#Test Transmitter
	
	""""while (not r.listMessagesReceived):
		time.sleep(1)
	r.lockConnectedDevice.acquire()
	r.connectedDevice = True
	r.lockConnectedDevice.release()"""


	try:
		bleServer.run()
		bleTransmitterThread.start()
		
		
	except KeyboardInterrupt:
		bleServer.quit()
		
if __name__ == '__main__':
    main()

