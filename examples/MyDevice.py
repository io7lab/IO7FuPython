from IO7FuPython import ConfiguredDevice
import json
import time
import ComMgr


def reset_cb(topic, msg):
    print('hello from reset')

def handleCommand(topic, msg):
    print('topic is ', topic)
    print('message is ', str(msg, 'utf-8'))

def handleMeta(topic, msg):
    print('handling metadata update')

nic = ComMgr.startWiFi('iot')
device = ConfiguredDevice()
device.setUserCommand(handleCommand)
device.setUserMeta(handleMeta)
device.setResetCallback(reset_cb)

device.connect()

lastPub = time.ticks_ms() - device.meta['pubInterval']

while True:
    # default is JSON format with QoS 0
    if not device.loop():
        break
    if (time.ticks_ms() - device.meta['pubInterval']) > lastPub:
        lastPub = time.ticks_ms()
        device.publishEvent('status', json.dumps({'d':{'alive': 'true'}}))
