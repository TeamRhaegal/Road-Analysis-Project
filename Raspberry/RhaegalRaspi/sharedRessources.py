from mutex import mutex

#Global values
#Ressources 
listMessagesToSend = []
listMessagesReceived = []
	
#Mutex
mutexMessagesToSend = mutex()
mutexMessagesReceived = mutex()
