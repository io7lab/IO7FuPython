# IO7 Foundataion for Micropython

This consists of two modules. the ComMgr and the IO7FuPython.

## IO7FuPython

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


## ESP32 CommMgr.py

This Micropython code has the BLE and WiFi connection function. When you pass some string like 'myDevice' as below, it will be the part of the mDNS hostname. The hostname would be myDevice-2cf0c0, where 2cf0c0 is the last three bytes of the MAC address.
```python
    nic = ComMgr.startWiFi('myDevice')                  # pass the name as the argumen for the hostname
```

The included boot.py shows the basic usage of this component with webrepl

# Library Installation
`mip.install('github:io7-dev/IO7FuPython/package.json')`