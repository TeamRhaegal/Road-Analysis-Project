from bleGattServer.bleThreads import BLETransmitterThread,BLEServer
from threading import Event

	
def main():
	runRaspiCodeEvent = Event()
	runRaspiCodeEvent.set()
	
	#BLE part
	bleServer = BLEServer()
	bleTransmitterThread= BLETransmitterThread(bleServer,runRaspiCodeEvent) #for transmitting messages to the server
	

	try:
		bleTransmitterThread.start()
		bleServer.run() ############################### a la fin #############
				
	except KeyboardInterrupt:
		print ('Attempting to close all threads')
        runRaspiCodeEvent.clear()
        bleTransmitterThread.join()
        print ('All threads successfully closed')
        bleServer.quit()
		
if __name__ == '__main__':
    main()

