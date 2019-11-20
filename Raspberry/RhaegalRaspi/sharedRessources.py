from threading import Lock

#Global values
#Ressources 
listMessagesToSend = ['batt$critic']
listMessagesReceived = []
connectedDevice= True
	
#Locks
lockMessagesToSend = Lock()
lockMessagesReceived = Lock()
lockConnectedDevice = Lock()
