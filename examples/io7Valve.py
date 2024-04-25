from IO7FuPython import ConfiguredDevice
import json
import time
import uComMgr32
from machine import Pin
valve = Pin(15, Pin.OUT)

def handleCommand(topic, msg):
    global lastPub
    jo = json.loads(str(msg,'utf8'))
    if ("valve" in jo['d']):
        if jo['d']['valve'] is 'on':
            valve.on()
        else:
            valve.off()
        lastPub = - device.meta['pubInterval']

nic = uComMgr32.startWiFi('iot')
device = ConfiguredDevice()
device.setUserCommand(handleCommand)

device.connect()

lastPub = time.ticks_ms() - device.meta['pubInterval']

while True:
    if not device.loop():
        break
    if (time.ticks_ms() - device.meta['pubInterval']) > lastPub:
        lastPub = time.ticks_ms()
        device.publishEvent('status', json.dumps({'d':{'valve': 'on' if valve.value() else 'off'}}))
