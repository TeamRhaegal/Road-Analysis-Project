from threading import Lock
import numpy as np

#Global values
wheelSpeed = 0  
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
searchModeActivated = False # True if a search sign has been detected and the car is in front of it

emergencyFrontOn = False
emergencyRearOn = False

# variables to detect road sign and specify their width
widthStop = 0
widthSearch = 0

# variables to detect sized objects from search mode
widthSmall = 0
widthMedium = 0
widthBig = 0
# variable that contains an image with detected objects from search mode, and boxes around interesting objects
# careful, image is given as A NUMPY ARRAY
# numpy.empty(0) gives the same result as : "a = []"
imageSearchObject = np.empty(0)

listMessagesToSend = []
listImgPartToSend = []
listMessagesReceived = []
connectedDevice= False

#Locks
lockWheelSpeed = Lock()
lockBatteryLevel = Lock()
lockFrontRadar = Lock()
lockRearRadar = Lock()
lockModeLaunched = Lock()
lockSearchModeActivated = Lock()

lockMessagesToSend = Lock()
lockImgPartToSend = Lock ()
lockMessagesReceived = Lock()
lockConnectedDevice = Lock()

lockWidthStop = Lock()
lockWidthSearch = Lock()
lockWidthSmall = Lock()
lockWidthMedium = Lock()
lockWidthBig = Lock()
lockImageSearchObject = Lock()

lockEmergencyFrontOn = Lock()
lockEmergencyRearOn = Lock()

lockMode = Lock()
lockJoystick = Lock()
lockSpeed = Lock()
lockState = Lock()


def constructMsgToIHM(key,*args):
    msg = str(key)
    if len(args) :
        i = 0
        for i in range (0,len(args)):
            msg= msg+"$"+str(args[i])
    
        lockMessagesToSend.acquire()
        listMessagesToSend.append(msg)
        lockMessagesToSend.release()




