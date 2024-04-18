# IO7 Framework for Micropython(esp32)

With this library, the developer can create an IO7 ESP32 IOT devices with Micropython.

## A. IO7FuPython

This can be used to create an IO7 IOT Device. The initializaiton function can be called with either a configuration option or all parameters
1. With all parameters
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
2. With configuration dict object.
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
This can be especially usefull when the configuration is stored in a file
```python
    from IOTDevice import Device
    
    f = open('device.cfg', 'w')
    option = json.loads(f.read())
    device = Device(cfg = option)
    device.setCallback(sub_cb)				# subsription callback. ie. command handler
    device.setResetCallback(reset_cb)			# factory reset callback. it clears 'device.cfg' file.
```
3. If there is a file named 'device.cfg' and the content is something like this, you can use the ConfiguredDevice.
```json
{"broker": "192.168.1.9", "token": "mytoken", "devType": "mytype", "devId": "myid"}
```
If there is a file named 'device.cfg' and the content is something like above, you just create a ConfiguredDevice as follows.
```python
    device = ConfiguredDevice()
    device.setCallback(sub_cb)				# subsription callback. ie. command handler
```
4. If there is a file named 'ca.crt' with the TLS certicate in it, the device will use the secure mqtt connection to the server.

5. GPIO 0 is enabled for the REPL mode. In order to use it include this if an break clause as below.

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

# Library Installation
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

# MQTTS TLS Conecction Setup
* In order to make the device talk to a secure MQTTS broker, copy the certificate file from the server and upload to the ESP32 with the name 'ca.crt'
