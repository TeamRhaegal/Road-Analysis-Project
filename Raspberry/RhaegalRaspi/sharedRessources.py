from mutex import mutex
from threading import Lock

#Global values
vitesseRoue = 50  
Turbo ="off"
Joystick = "none"
Mode = "assisted"
sign = "none"
signWidth = 0

listMessagesToSend = []
listMessagesReceived = []
connectedDevice= False
	

#Locks
lockMessagesToSend = Lock()
lockMessagesReceived = Lock()
lockConnectedDevice = Lock()

ModeLock =Lock()
JoystickLock = Lock()
TurboLock = Lock()
signLock = Lock()
signWidthLock = Lock()
VitesseLock = Lock()


