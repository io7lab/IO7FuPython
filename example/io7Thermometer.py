from IO7FuPython import Device, ConfiguredDevice
import json
import time
import ComMgr
import dht
from machine import Pin


def handleCommand(topic, msg):
    pass

nic = ComMgr.startWiFi('iot')
device = ConfiguredDevice()
device.setUserCommand(handleCommand)

device.connect()
sensor = dht.DHT22(Pin(16))

lastPub = time.ticks_ms() - device.meta['pubInterval']

while True:
    # default is JSON format with QoS 0
    device.loop()
    if (time.ticks_ms() - device.meta['pubInterval']) > lastPub:
        lastPub = time.ticks_ms()
        sensor.measure()
        device.publishEvent('status', json.dumps({'d':{'temperature': sensor.temperature(),
                                                       'humidity': sensor.humidity()
                                                       }
                                                  }))
