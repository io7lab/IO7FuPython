from IO7FPython import Device, ConfiguredDevice
import json
import time
import ComMgr


def reset_cb(topic, msg):
    print('hello from reset')
    
def sub_cb(topic, msg):
    global pubInterval
    jo = json.loads(str(msg,'utf8'))
    if ("pubInterval" in jo['d']):
        pubInterval = jo['d']['pubInterval']
    elif ("turnOn" in jo['d']):
        led.on()
        lastPub = - pubInterval
    elif ("turnOff" in jo['d']):
        led.off()
        lastPub = - pubInterval

nic = ComMgr.startWiFi('iot')
device = ConfiguredDevice()
device.setCallback(sub_cb)
device.setResetCallback(reset_cb)

device.connect()

from machine import Pin
led = Pin(13, Pin.OUT)
pubInterval = 5000
lastPub = time.ticks_ms() - pubInterval

while True:
    # default is JSON format with QoS 0
    device.loop()
    if (time.ticks_ms() - pubInterval) > lastPub:
        lastPub = time.ticks_ms()
        device.publishEvent('status', json.dumps({'d':{'lamp': 'on' if led.value() else 'off'}}))





