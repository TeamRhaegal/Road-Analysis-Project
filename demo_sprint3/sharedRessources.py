from mutex import mutex
from threading import Lock

#Global values
wheelSpeed = 0  
turbo ="off"
joystick = "none"
mode = "assist"
sign = "none"
signWidth = 0
<<<<<<< HEAD

=======
maxDistanceUS = 10   #distance max ultrasons obstacle
obstacleRear = 0
obstacleFront = 0
>>>>>>> f289d6bf46ff39eb6d76f37f46127629f2a0642a

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


