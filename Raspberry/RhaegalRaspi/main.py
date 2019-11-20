from bleGattServer.bleThreads import BLEServer, BLETransmitterThread
	
def main():
	#BLE part
	bleServer = BLEServer() #server thread

	bleTransmitterThread= BLETransmitterThread(bleServer) #for transmitting messages to the server
	bleTransmitterThread.daemon=True

	try:
		bleServer.run()
		bleTransmitterThread.start()
	except KeyboardInterrupt:
		bleServer.quit()
		
if __name__ == '__main__':
    main()

