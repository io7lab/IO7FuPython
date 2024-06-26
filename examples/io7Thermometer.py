from IO7FuPython import ConfiguredDevice
import json
import time
import uComMgr32
import dht
from machine import Pin


def handleCommand(topic, msg):
    pass

nic = uComMgr32.startWiFi('iot')
device = ConfiguredDevice()
device.setUserCommand(handleCommand)

device.connect()
sensor = dht.DHT22(Pin(16))

lastPub = time.ticks_ms() - device.meta['pubInterval']

while True:
    if not device.loop():
        break
    if (time.ticks_ms() - device.meta['pubInterval']) > lastPub:
        lastPub = time.ticks_ms()
        sensor.measure()
        device.publishEvent('status', json.dumps({'d':{'temperature': sensor.temperature(),
                                                       'humidity': sensor.humidity()
                                                       }
                                                  }))
