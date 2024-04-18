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

# B. ESP32 CommMgr.py
## WiFi Client
This Micropython library has the BLE and WiFi connection function. This uses the configuration file `wifi.cfg` to get the ssid and wifi password. The format is as follows.
```json
{ "ssid" : "wifi ssid", "pw" : "wifi password"}
```

```python
# uComMgr32.startWiFi(name, ssid=None, pw=None)
nic = uComMgr32.startWiFi('myDevice')                  
```
When you pass some string like 'myDevice' as above, this will connects to the wifi and the name will be the part of the mDNS hostname. The hostname would be myDevice-2cf0c0, where 2cf0c0 is the last three bytes of the MAC address.



## BLE Client

```python
# startBLE(name, myBLECallback=None)
uComMgr32.startBLE('myDevice', myCallback)
```

This starts the BLE service with the given name and the callback if specified. The `name` will be the BLE device name once started, myBLECallback is the optional callback function you can define and pass. 

This callback process the passed message if the message is what it is supposed to handle and should return `True`, otherwise return `False`. If it returns `False` the libray's built-in remaining callback will continue processing.

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
