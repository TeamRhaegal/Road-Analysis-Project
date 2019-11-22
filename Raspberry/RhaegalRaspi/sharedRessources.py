from mutex import Mutex

#Global values
#Ressources 
listMessagesToSend = []
listMessagesReceived = []
	
#Mutex
mutexMessagesToSend = Mutex()
mutexMessagesReceived = Mutex()