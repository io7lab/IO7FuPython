# IO7 Framework for Micropython(esp32)

With this library, the developer can create an io7 ESP32 IOT devices with Micropython.

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
3. With a file named `device.cfg` and the content is something like this, you can use the ConfiguredDevice.
```json
{"broker": "yourio7.server.com", "token": "mytoken", "devType": "mytype", "devId": "myid"}
```
Just create a ConfiguredDevice as follows with above configuration file.
```python
    device = ConfiguredDevice()
    device.setCallback(sub_cb)				# subsription callback. ie. command handler
```
4. If there is a file named `ca.pem` with the TLS certicate in it, the device will use the secure mqtt connection to the server. Or if device.cfg has `ca` and there is a file specified by `ca`, then the file will be used as the TLS Certificate.
```json
{"broker": "yourio7.server.com", "token": "mytoken", "devType": "mytype", "devId": "myid", "ca":"ca.txt"}
```

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
* As mentioned above, in order to make the device talk to a secure MQTTS broker, copy the certificate file from the server and upload to the ESP32 Micropython environment with the name 'ca.pem', or any name you want and specify in the `device.cfg` file.
