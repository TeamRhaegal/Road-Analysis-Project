
"""Copyright (c) 2019, Douglas Otwell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import dbus
import sys 

from advertisement import Advertisement
from service import Service, Characteristic, Descriptor
from gi.repository import GObject
import sharedRessources as r


GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000
RASP_SERVICE_UUID =            '7fb9ad0f-3040-496f-af83-c7bc55c304db'
RASP_RX_CHARACTERISTIC_UUID =  '7a9eb5fc-8b0f-4057-ba14-ebcc98bbeb11'
RASP_TX_CHARACTERISTIC_UUID =  'f83c3290-43fa-469b-a819-73b8ffb6890e'
LOCAL_NAME =                   'RaspberryPi3_Rhaegal'

class RaspAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name(LOCAL_NAME)
        self.include_tx_power = True

class RaspService(Service):
    def __init__(self,index):
        Service.__init__(self, index, RASP_SERVICE_UUID, True)
        self.add_characteristic(TxCharacteristic(self))
        self.add_characteristic(RxCharacteristic(self))

class TxCharacteristic(Characteristic):
    def __init__(self, service):
        Characteristic.__init__(self, RASP_TX_CHARACTERISTIC_UUID,
                                ['notify'], service)
        self.notifying = True
 
    def send_tx(self, s):
        if not self.notifying:
            return
        value = []
        for c in s:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])
        print('send message to IHM')
 
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
 
    def StopNotify(self):
        if not self.notifying:
            return
        self.notifying = False
        
class RxCharacteristic(Characteristic):
    def __init__(self, service):
        Characteristic.__init__(self, RASP_RX_CHARACTERISTIC_UUID,
                                ['write'], service)

    def WriteValue(self, value, options):
        print('remote BLE: {}'.format(bytearray(value).decode()))
        
        r.lockMessagesReceived.acquire()	
        r.listMessagesReceived.append(bytearray(value).decode())
        r.lockMessagesReceived.release()
		
        

