from mutex import mutex
from threading import Lock

#Global values
wheelSpeed = 0  
turbo ="off"
joystick = "none"
mode = "assist"

# variables to detect road sign and specify their width
widthStop = 0
widthSearch = 0

listMessagesToSend = []
listMessagesReceived = []
connectedDevice= False

#Locks
lockMessagesToSend = Lock()
lockMessagesReceived = Lock()
lockConnectedDevice = Lock()
lockWidthStop = Lock()
lockWidthSearch = Lock()


modeLock =Lock()
joystickLock = Lock()
turboLock = Lock()
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
	
	
	



