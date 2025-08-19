# IO7 Framework for MicroPython (ESP32)


This is part of the io7 IoT Platform (https://github.com/io7lab) to help build IoT devices.


With this library, developers can create io7 ESP32 IoT devices using MicroPython.


# 1. IO7FuPython Introduction

This can be used to create an io7 IoT device. The initialization function can be called with either a configuration option or all parameters.

1. Configuring the Device
* With all arguments
```python
    from IOTDevice import Device
    
    device=Device(
        broker = '192.168.1.9',
        devId = 'mydevice',
        token = 'mytoken'
    )
    device.setCallback(sub_cb)                # subscription callback, i.e., command handler
    device.setResetCallback(reset_cb)         # factory reset callback; it clears the 'device.cfg' file.
```
* With a configuration dict object
```python
    from IOTDevice import Device
    
    option = {
        broker = '192.168.1.9',
        devId = 'mydevice',
        token = 'mytoken'
    }
    device = Device(cfg = option)
    device.setCallback(sub_cb)                # subscription callback, i.e., command handler
    device.setResetCallback(reset_cb)         # factory reset callback; it clears the 'device.cfg' file.
```
This can be especially useful when the configuration is stored in a file.
```python
    from IOTDevice import Device
    
    f = open('device.cfg', 'w')
    option = json.loads(f.read())
    device = Device(cfg = option)
    device.setCallback(sub_cb)                # subscription callback, i.e., command handler
    device.setResetCallback(reset_cb)         # factory reset callback; it clears the 'device.cfg' file.
```
* With a file named `device.cfg` containing the content below, you can use the ConfiguredDevice:
```json
{"broker": "yourio7.server.com", "token": "mytoken", "devId": "myid"}
```
2. Instantiate a ConfiguredDevice with the above configuration file as follows:
```python
    device = ConfiguredDevice()
    device.setCallback(sub_cb)                # subscription callback, i.e., command handler
```
3. If a secure MQTT connection is required, provide the `ca.pem` file. When there is a file named `ca.pem` containing the TLS CA certificate, the device will use a secure MQTT connection (i.e., MQTTS) to the server. If `device.cfg` has a `ca` attribute and there is a file specified by this, then that file will be used as the TLS certificate.
```json
{"broker": "yourio7.server.com", "token": "mytoken", "devId": "myid", "ca":"ca.pem"}
```

4. GPIO 0 is enabled for REPL mode. To use it, add the following `if` clause as shown below. This will break the while loop and enter the Python interpreter over the serial connection.

```python
while True:
    # this if clause breaks the loop if GPIO 0 is pressed
    if device.replMode():
        break
    device.loop()
    if (time.ticks_ms() - device.meta['pubInterval']) > lastPub:
        lastPub = time.ticks_ms()
        device.publishEvent('status', json.dumps({'d':{'valve': 'on' if led.value() else 'off'}}))
```
5. Sample Device: This is a sample io7 device using the IO7FuPython library.
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

* Connect the ESP32 to the Internet and run the following code:
```python
import network
nic = network.WLAN(network.STA_IF)
nic.active(True)
nic.connect('ssid', 'password')
    nic.ifconfig()          # check if WiFi is connected or wait until it is connected

import mip
mip.install('github:io7lab/IO7FuPython/')
```

# 3. MQTTS TLS Connection Setup

* As mentioned above, to enable the device to communicate with a secure MQTTS broker, copy the certificate file from the server and upload it to the ESP32 MicroPython environment with the name 'ca.pem', or any name you want, and specify it in the `device.cfg` file.

## Important
If `ca.pem` is found, the device will open a secure MQTT session. This applies even if `device.cfg` doesn't have the `ca` attribute. The `ca` attribute is used to specify the name of the certificate file if the name is other than `ca.pem`, or to ignore `ca.pem` even if it exists by giving an empty value to it, i.e., `"ca":""`.
