from mutex import mutex
from threading import Lock

#Global values
wheelSpeed = 0  
turbo ="off"
joystick = "none"
mode = "assist"
signDetection = []

listMessagesToSend = []
listMessagesReceived = []
connectedDevice= False
	

#Locks
lockMessagesToSend = Lock()
lockMessagesReceived = Lock()
lockConnectedDevice = Lock()

modeLock =Lock()
joystickLock = Lock()
turboLock = Lock()
signDetectionLock = Lock()
speedLock = Lock()

def constructMsgToIHM(key,*args):
	msg = str(key)
	if len(args) :
		int i = 0;
		for i in range (0,len(args)):
			msg= msg+"$"+str(args[i])
			
		lockMessagesToSend.acquire()
		listMessagesToSend.append(msg)
		lockMessagesToSend.release()
	
	
	



