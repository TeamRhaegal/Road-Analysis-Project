<<<<<<< HEAD
=======
from mutex import mutex
>>>>>>> a37b71bcebbf226ec0fd62aa73c0f4a0f0d9a089
from threading import Lock

#Global values
vitesseRoue = 50  
Turbo ="off"
Joystick = "none"
Mode = "assisted"
Panneau = "none"
NbPixel = 0

listMessagesToSend = ['batt$critic']
listMessagesReceived = []
connectedDevice= True
	

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

