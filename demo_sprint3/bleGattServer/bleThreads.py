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
        self.TXChara = self.retrieveTXCharacteristic(server)
        self.setDaemon(True)
        self.runEvent= runRaspiCodeEvent
        print('Open transmitter thread')

    def retrieveTXCharacteristic(self, server):               #get the transmitter characteristic
		serverService=server.services[0]                            #only one service in the app 
		serverCharacteristics = serverService.get_characteristics() #retrieve all characteristics in the service
		return serverCharacteristics[0]                          #the transmitter is the fist one in the list

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
			print ("message found")
		        for i in range(0,len(myMessagesToSend)):
			    self.TXChara.send_tx(myMessagesToSend.pop())
		
		time.sleep(0.2)
        print('Transmitter to server thread closed')
