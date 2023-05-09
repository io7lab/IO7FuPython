from IO7FuPython import Device, ConfiguredDevice
import json
import time
import ComMgr


def reset_cb(topic, msg):
    print('hello from reset')
    
def sub_cb(topic, msg):
    global pubInterval
    jo = json.loads(str(msg,'utf8'))
    if ("valve" in jo['d']):
        if jo['d']['valve'] is 'on':
            led.on()
        else:
            led.off()
        lastPub = - pubInterval

nic = ComMgr.startWiFi('iot')
device = ConfiguredDevice()
device.setCmdCallback(sub_cb)
device.setResetCallback(reset_cb)

device.connect()

from machine import Pin
led = Pin(13, Pin.OUT)
lastPub = time.ticks_ms() - device.meta['pubInterval']

print(device.cfg())

while True:
    # default is JSON format with QoS 0
    device.loop()
    if (time.ticks_ms() - device.meta['pubInterval']) > lastPub:
        lastPub = time.ticks_ms()
        device.publishEvent('status', json.dumps({'d':{'lamp': 'on' if led.value() else 'off'}}))
