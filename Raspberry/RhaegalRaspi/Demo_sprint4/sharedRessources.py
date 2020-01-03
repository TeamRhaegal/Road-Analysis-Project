from threading import Lock

#Global values
wheelSpeed = 0  
turbo ="off"
joystick = "none"
mode = "assist"
state = "off"

wheelSpeed = 0
batteryLevel = 0
UFC = 180      #front center US sensor
UFL = 180       #front left US sensor
UFR = 180       #front right US sensor
URC = 180       #front center US sensor
URL = 180       #front left US sensor
URR = 180       #front right US sensor
modeLaunched = 0; #0 nothing, 1 assisted, 2 autonomous

emergencyFrontOn = False
emergencyRearOn = False

# variables to detect road sign and specify their width
widthStop = 0
widthSearch = 0

# variables to detect sized objects from search mode
widthSmall = 0
widthMedium = 0
widthBig = 0

listMessagesToSend = []
listMessagesReceived = []
connectedDevice= False

#Locks
lockWheelSpeed = Lock()
lockBatteryLevel = Lock()
lockFrontRadar = Lock()
lockRearRadar = Lock()
lockModeLaunched = Lock()

lockMessagesToSend = Lock()
lockMessagesReceived = Lock()
lockConnectedDevice = Lock()
lockWidthStop = Lock()
lockWidthSearch = Lock()

lockEmergencyFrontOn = Lock()
lockEmergencyRearOn = Lock()

lockMode = Lock()
lockJoystick = Lock()
lockTurbo = Lock()
lockSpeed = Lock()
lockState = Lock()

"""
NEXT VARIABLES ARE NOW USELESS ! (replaced by the ones just before) 

modeLock = Lock()
joystickLock = Lock()
turboLock = Lock()
speedLock = Lock()
stateLock = Lock()
"""


def constructMsgToIHM(key,*args):
	msg = str(key)
	if len(args) :
		i = 0
		for i in range (0,len(args)):
			msg= msg+"$"+str(args[i])
			
		lockMessagesToSend.acquire()
		listMessagesToSend.append(msg)
		lockMessagesToSend.release()
	
	
	



