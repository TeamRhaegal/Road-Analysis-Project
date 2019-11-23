from mutex import mutex
from threading import Lock

#Global values
wheelSpeed = 0  
turbo ="off"
joystick = "none"
mode = "assisted"
sign = "none"
signWidth = 0
maxDistanceUS = 10   #distance max ultrasons obstacle
obstacleRear = 0
obstacleFront = 0

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
signLock = Lock()
signWidthLock = Lock()
speedLock = Lock()


