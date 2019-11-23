from mutex import mutex
from threading import Lock

#Global values
vitesseRoue = 50  
Turbo ="off"
Joystick = "none"
Mode = "assisted"
Panneau = "none"
NbPixel = 0

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
PanneauLock = Lock()
NbPixelLock = Lock()
VitesseLock = Lock()

