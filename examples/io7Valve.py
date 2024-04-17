from IO7FuPython import ConfiguredDevice
import json
import time
import ComMgr

def handleCommand(topic, msg):
    global lastPub
    jo = json.loads(str(msg,'utf8'))
    if ("valve" in jo['d']):
        if jo['d']['valve'] is 'on':
            led.on()
        else:
            led.off()
        lastPub = - device.meta['pubInterval']

nic = ComMgr.startWiFi('iot')
device = ConfiguredDevice()
device.setUserCommand(handleCommand)

device.connect()

from machine import Pin
led = Pin(13, Pin.OUT)
lastPub = time.ticks_ms() - device.meta['pubInterval']

while True:
    if not device.loop():
        break
    if (time.ticks_ms() - device.meta['pubInterval']) > lastPub:
        lastPub = time.ticks_ms()
        device.publishEvent('status', json.dumps({'d':{'valve': 'on' if led.value() else 'off'}}))

