from bleThread import BLEServer, BLETransmitterThread

#Global values
#Ressources 
listMessagesToSend = []
listMessagesReceived = []
	
#Mutex
mutexMessagesToSend = Mutex()
mutexMessagesReceived = Mutex()
	
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

