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
	print ("init Service OK")
		
    def initAdvertisement(self):
        adv = RaspAdvertisement(0) #advertize
        adv.register()
	print ("initAdvertissement OK ")

class BLETransmitterThread(Thread):

    def __init__(self, server,runRaspiCodeEvent):
        Thread.__init__(self)
        self.TXChara = self.retrieveTXCharacteristic(server,0)
        self.TXImgChara = self.retrieveTXCharacteristic(server,1)
        self.setDaemon(True)
        self.runEvent= runRaspiCodeEvent
        print('Open transmitter thread')

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
                        r.lockImgPartToSend.acquire()
                        myImgParts = r.listImgPartToSend
                        r.listImgPartToSend = []
                        r.lockImgPartToSend.release()
                        
                        if myImgParts :
                                for i in range(0,len(myImgParts)):				
                                    print ("To IHM : ", myImgParts[-1])
                                    self.TXImgChara.send_tx(myImgParts.pop())               
    
    		time.sleep(0.2)

