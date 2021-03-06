from utils.serverSettings import *
from utils.service import Application
from threading import Thread
import time
import sharedRessources as r

		
class BLEServer(Application):
    def __init__(self):
	Application.__init__(self)
	self.initService()
	self.initAdvertisement()
	
    def initService(self):
        self.add_service(RaspService(0))
        self.register()
		
    def initAdvertisement(self):
        adv = RaspAdvertisement(0) #advertize
        adv.register()

class BLETransmitterThread(Thread):

    def __init__(self, server,runRaspiCodeEvent):
        Thread.__init__(self)
        self.TXChara = self.retrieveTXCharacteristic(server,0)
        self.TXImgChara = self.retrieveTXCharacteristic(server,1)
        self.setDaemon(True)
        self.runEvent= runRaspiCodeEvent

    def retrieveTXCharacteristic(self, server,nbChara):               #get the transmitter characteristic
    	serverService=server.services[0]                            #only one service in the app 
    	serverCharacteristics = serverService.get_characteristics() #retrieve all characteristics in the service
    	return serverCharacteristics[nbChara]                          

    def run(self):
        while self.runEvent.isSet() :	
    		r.lockConnectedDevice.acquire()
    		deviceIsConnected= r.connectedDevice
    		r.lockConnectedDevice.release()
    		
    		if (deviceIsConnected):	
    		    r.lockMessagesToSend.acquire()
    		    myMessagesToSend = r.listMessagesToSend
    		    r.listMessagesToSend = []          
    		    r.lockMessagesToSend.release()
                
    		    if myMessagesToSend :
                        for i in range(0,len(myMessagesToSend)):				
                                print ("To IHM : ", myMessagesToSend[0])
                                for k in range(0,3):
                                        self.TXChara.send_tx(myMessagesToSend[0])
                                myMessagesToSend.pop(0)
                        
                r.lockImgPartToSend.acquire()
                myImgParts = r.listImgPartToSend
                r.listImgPartToSend = []
                r.lockImgPartToSend.release()
                
                if myImgParts :
        			for i in range(0,len(myImgParts)):				
        			    print ("To IHM : ", myImgParts[0])
        			    self.TXImgChara.send_tx(myImgParts.pop(0))               
    
    		time.sleep(0.2)

