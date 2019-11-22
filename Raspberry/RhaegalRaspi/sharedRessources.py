from mutex import mutex
from threading import Lock

#Global values
vitesseRoue = 50  
Turbo ="off"
Joystick = "none"
Mode = "assisted"
Panneau = "none"
NbPixel = 0

#Ressources 
listMessagesToSend = []
listMessagesReceived = []
	
#Mutex
mutexMessagesToSend = mutex()
mutexMessagesReceived = mutex()

ModeLock =Lock()
JoystickLock = Lock()
TurboLock = Lock()
PanneauLock = Lock()
NbPixelLock = Lock()
VitesseLock = Lock()