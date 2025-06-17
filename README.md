# IO7 Framework for Micropython(esp32)

This is a part of io7 IOT Platform https://github.com/io7lab to help build an IOT device.

With this library, the developer can create an io7 ESP32 IOT devices with Micropython.

# 1. IO7FuPython Introduction

This can be used to create an io7 IOT Device. The initializaiton function can be called with either a configuration option or all parameters
1. Configuring the Device
* with all arguments 
```python
    from IOTDevice import Device
    
    device=Device(
        broker = '192.168.1.9',
        devId = 'mydevice',
        token = 'mytoken'
    )
    device.setCallback(sub_cb)				# subsription callback. ie. command handler
    device.setResetCallback(reset_cb)			# factory reset callback. it clears 'device.cfg' file.
```
* With configuration dict object.
```python
    from IOTDevice import Device
    
    option = {
        broker = '192.168.1.9',
        devId = 'mydevice',
        token = 'mytoken'
    }
    device = Device(cfg = option)
    device.setCallback(sub_cb)				# subsription callback. ie. command handler
    device.setResetCallback(reset_cb)			# factory reset callback. it clears 'device.cfg' file.
```
This can be especially useful when the configuration is stored in a file
```python
    from IOTDevice import Device
    
    f = open('device.cfg', 'w')
    option = json.loads(f.read())
    device = Device(cfg = option)
    device.setCallback(sub_cb)				# subsription callback. ie. command handler
    device.setResetCallback(reset_cb)			# factory reset callback. it clears 'device.cfg' file.
```
* With a file named `device.cfg` of the content like below, you can use the ConfiguredDevice.
```json
{"broker": "yourio7.server.com", "token": "mytoken", "devId": "myid"}
```
2. Instantiate a ConfiguredDevice with above configuration file as follows.
```python
    device = ConfiguredDevice()
    device.setCallback(sub_cb)				# subsription callback. ie. command handler
```
3. If a secure MQTT connection is required, create the `ca.pem` file. When there is a file named `ca.pem` with the TLS CA certicate in it, the device will use the secure mqtt connection(ie. mqtts) to the server. Or if device.cfg has `ca` attribute and there is a file specified by this, then the file will be used as the TLS Certificate.
```json
{"broker": "yourio7.server.com", "token": "mytoken", "devId": "myid", "ca":"ca.pem"}
```

4. GPIO 0 is enabled for the REPL mode. In order to use it include this, add this `if clause` as below. This will breaks the while loop and get in to the Python interpreter over the Serial connection.

```python
while True:
    # this if clause break the loop if the GPIO 0 is pressed
    if device.replMode():
        break
    device.loop()
    if (time.ticks_ms() - device.meta['pubInterval']) > lastPub:
        lastPub = time.ticks_ms()
        device.publishEvent('status', json.dumps({'d':{'valve': 'on' if led.value() else 'off'}}))
```
5. Sample Device : This is a sample io7 Device with IO7FuPython library. 
```python
from IO7FuPython import ConfiguredDevice
import json
import time
import uComMgr32

def handleCommand(topic, msg):
    global lastPub
    jo = json.loads(str(msg,'utf8'))
    if ("lamp" in jo['d']):
        if jo['d']['lamp'] is 'on':
            lamp.on()
        else:
            lamp.off()
        lastPub = - device.meta['pubInterval']

nic = uComMgr32.startWiFi('lamp')
device = ConfiguredDevice()
device.setUserCommand(handleCommand)

device.connect()

from machine import Pin
lamp = Pin(15, Pin.OUT)
lastPub = time.ticks_ms() - device.meta['pubInterval']

while True:
    # default is JSON format with QoS 0
    if not device.loop():
        break
    if (time.ticks_ms() - device.meta['pubInterval']) > lastPub:
        lastPub = time.ticks_ms()
        device.publishEvent('status', json.dumps({'d':{'lamp': 'on' if lamp.value() else 'off'}}))

```
# 2. Library Installation
* Connect ESP32 to the Internet and run the following code
```python
import network
nic = network.WLAN(network.STA_IF)
nic.active(True)
nic.connect('ssid', 'password')
nic.ifconfig()          # check if the WiFi is connected or wait until connected

import mip
mip.install('github:io7lab/IO7FuPython/')
```

# 3. MQTTS TLS Conecction Setup
* As mentioned above, in order to make the device talk to a secure MQTTS broker, copy the certificate file from the server and upload to the ESP32 Micropython environment with the name 'ca.pem', or any name you want and specify in the `device.cfg` file.

## Important
If 'ca.pem' is found, the device will open the secure mqtt session. This applies even `device.cfg` doesn't have the `ca` attribute. The `ca` attribute is used to specify the name of the certificate file if the name is other than `ca.pem`, or to ignore the `ca.pem` even if it exists by giving empty value to it, ie. `"ca":""`.
