from threading import Lock

#Global values
wheelSpeed = 0  
turbo ="off"
joystick = "none"
mode = "assist"
state = "off"

wheelSpeed = 0
batteryLevel = 0
UFC = 180
UFL = 180
UFR = 180
modeLaunched = 0; #0 nothing, 1 assisted, 2 autonomous

emergencyOn = False

# variables to detect road sign and specify their width
widthStop = 0
widthSearch = 0

listMessagesToSend = []
listMessagesReceived = []
connectedDevice= False

#Locks
lockWheelSpeed = Lock()
lockBatteryLevel = Lock()
lockFrontRadar = Lock()
lockModeLaunched = Lock()

lockMessagesToSend = Lock()
lockMessagesReceived = Lock()
lockConnectedDevice = Lock()
lockWidthStop = Lock()
lockWidthSearch = Lock()

lockEmergencyOn = Lock()

modeLock =Lock()
joystickLock = Lock()
turboLock = Lock()
speedLock = Lock()
stateLock = Lock()

def constructMsgToIHM(key,*args):
	msg = str(key)
	if len(args) :
		i = 0
		for i in range (0,len(args)):
			msg= msg+"$"+str(args[i])
			
		lockMessagesToSend.acquire()
		listMessagesToSend.append(msg)
		lockMessagesToSend.release()
	
	
	



