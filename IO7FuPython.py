import json
from umqtt.robust import MQTTClient
from machine import Pin, reset
import os
import re
import urequests

loopSuccess = True
replPin = Pin(0, Pin.IN, Pin.PULL_UP)
def replPin_pressed(p):
    global loopSuccess
    loopSuccess = False
    
deviceApp ='device.py'

replPin.irq(trigger=Pin.IRQ_FALLING|Pin.IRQ_RISING, handler=replPin_pressed)

def is_valid_url(url):
    if not url or not isinstance(url, str):
        return False
    
    if not (url.startswith('http://') or url.startswith('https://')):
        return False
    
    url_without_protocol = url.replace('https://', '').replace('http://', '')        
    if not url_without_protocol or url_without_protocol.startswith('/'):
        return False

    domain_part = url_without_protocol.split('/')[0]
    if '.' not in domain_part and domain_part != 'localhost':
        return False
        
    return True
                
def rotate_file():
    archive_dir = './archive'
    try:
        os.stat(archive_dir)
    except OSError:
        os.mkdir(archive_dir)
    
    try:
        files = os.listdir(archive_dir)
    except OSError:
        files = []

    #pattern = re.compile(r'^device\.py\.(\d+)$')
    pattern = re.compile(rf"^{deviceApp}\.(\d+)$")
    max_num = -1

    for f in files:
        match = pattern.match(f)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    print(f"mx {max_num}")
    with open(deviceApp, 'rb') as fsrc:
        with open(f"archive/{deviceApp}.{max_num + 1}", 'wb') as fdst:
            while True:
                buf = fsrc.read(512)  # read in small chunks to save RAM
                if not buf:
                    break
                fdst.write(buf)

class Device():
    '''
        This creates the IOTDevice. It can be called with either a configuration option or all parameters
        1. With all parameters
            device=Device(
                broker = '192.168.1.9',
                devId = 'mydevice',
                token = 'mytoken'
            )
        
        2. With option.
            option = {
                broker = '192.168.1.9',
                devId = 'mydevice',
                token = 'mytoken'
            }
            device = Device(cfg = option)

        This can be especially usefull when the configuration is stored in a file
            f = open('device.cfg', 'w')
            option = json.loads(f.read())
            device = Device(cfg = option)
 
    '''
    def __init__(self, cfg=None, broker=None, devId=None, token=None, keepalive=15):
        if cfg:
            self.broker = cfg['broker']
            self.devId = cfg['devId']
            self.token = cfg['token'] if 'token' in cfg else None
            self.meta = cfg['meta'] if 'meta' in cfg else {}
        else:
            self.broker = broker
            self.devId = devId
            self.token = token
            self.meta = {}
        self.meta['pubInterval'] = self.meta['pubInterval'] if 'pubInterval' in self.meta else 5000
        self.cmdCallback = None
        self.resetCallback = None
        self.updateCallback = None
        ca = cfg['ca'] if cfg and 'ca' in cfg else 'ca.pem' if 'ca.pem' in os.listdir() else ''
        if ca:
            port = '8883'
            ssl = True
            ssl_params = {'cert' : ca}
        else: 
            port = '1883'
            ssl = False
            ssl_params = {}
        
        self.client = MQTTClient(self.devId, self.broker, port, 
                                user=self.devId, password=self.token, ssl = ssl,
                                ssl_params = ssl_params,
                                keepalive=keepalive)
        self.client.set_callback(self.baseCallback)
        self.evtTopic     = f'iot3/{self.devId}/evt/'
        self.cmdTopicBase = f'iot3/{self.devId}/cmd/'
        self.cmdTopic     = self.cmdTopicBase + '+/fmt/+'
        self.metaTopic    = f'iot3/{self.devId}/mgmt/device/meta'
        self.logTopic     = f'iot3/{self.devId}/mgmt/device/status'
        self.updateTopic  = f'iot3/{self.devId}/mgmt/device/update'
        self.rebootTopic  = f'iot3/{self.devId}/mgmt/initiate/device/reboot'
        self.resetTopic   = f'iot3/{self.devId}/mgmt/initiate/device/factory_reset'
        self.upgradeTopic = f'iot3/{self.devId}/mgmt/initiate/firmware/update'
    
    def baseCallback(self, topic, msg):
        topicStr = topic.decode('utf-8')
        if topicStr == self.rebootTopic:
            self.client.disconnect()
            self.reboot()
        elif topicStr == self.resetTopic:
            if self.resetCallback:
                self.resetCallback(topic, msg)
        elif topicStr == self.updateTopic:
            metafields = json.loads(msg)['d']['fields'][0]
            if metafields['field'] == 'metadata':
                self.meta = metafields['value']
                self.saveCfg(self.cfg())
                self.client.publish(f"iot3/{self.devId}/mgmt/device/meta",
                    '{"d":{"metadata":' + json.dumps(self.meta) + '}}', qos=0, retain=True)
            if self.updateCallback:
                self.updateCallback(topic, msg)
        elif topicStr == self.upgradeTopic:
            if hasattr(self, 'upgradeCallback') and callable(getattr(self, 'upgradeCallback')):
                self.upgradeCallback(topic, msg)
        elif self.cmdTopicBase in topicStr and self.cmdCallback:
            self.cmdCallback(topic, msg)
    
    def publishEvent(self, evtId, data, fmt='json', qos=0, retain=False):
        self.client.publish(self.evtTopic + '%s/fmt/%s' % (evtId, fmt), data, qos=qos, retain=retain)

    def upgradeCallback(self, topic, msg):
        pass

    def connect(self):
        self.client.set_last_will(f"iot3/{self.devId}/evt/connection/fmt/json", 
                        '{"d":{"status":"offline"}}', retain=True, qos=0, )
        try:
            self.client.connect()
        except Exception as e:
            print(e)
            print('IO7FuPython : fix error for the connection information and/or certificate if required')
            print('Rebooting the Device')
            reset()
        self.client.subscribe(self.cmdTopic)
        self.client.subscribe(self.rebootTopic)
        self.client.subscribe(self.resetTopic)
        self.client.subscribe(self.updateTopic)
        self.client.subscribe(self.upgradeTopic)
        self.client.publish(f"iot3/{self.devId}/evt/connection/fmt/json", '{"d":{"status":"online"}}', qos=0, retain=True)
        self.client.publish(f"iot3/{self.devId}/mgmt/device/meta",
                            '{"d":{"metadata":' + json.dumps(self.meta) + '}}', qos=0, retain=True)

    def cfg(self):
        return {
            "broker": self.broker,
            "token": self.token,
            "devId": self.devId,
            "meta": self.meta
        }
        
    def reboot(self):
        reset()

    def setUserMeta(self, callback):
        self.updateCallback = callback

    def setUserCommand(self, callback):
        self.cmdCallback = callback

    def setResetCallback(self, callback):
        if self.__class__.__name__ == 'Device':   
            self.resetCallback = callback
        
    def loop(self):
        try:
            self.client.check_msg()
        except:
            pass
        return loopSuccess
        
    @classmethod
    def saveCfg(cls, cfg):
        pass

############### ConfiguredDeice ##############
device_cfg = 'device.cfg'

class ConfiguredDevice(Device):
    '''
    ConfiguredDevice is a subclass of Device. It adds the configuration file functionality to Device.
    
    '''
    def __init__(self, cfg=None, broker=None, devId=None, token=None, keepalive=60):
        if (cfg is None and devId is None):
            try:
                f = open(device_cfg, 'r')
                data = f.read().replace("'", '"')
                cfg = json.loads(data)
                if 'devId' not in cfg or 'broker' not in cfg:
                    raise Exception('the configuration file is invalid')
                super().__init__(cfg = cfg)
                f.close()
            except Exception as e:
                print(e)
                raise Exception('the configuration file is invalid')
            self.resetCallback = self.resetCfg
        else:
            super().__init__(cfg=cfg, devId=devId, broker=broker,
                             token=token, keepalive=keepalive)
            
    def resetCfg(self, topic, msg):
        '''
        This function erase the content of the configuration file to make the factory reset status.
        '''
        try:
            f = open(device_cfg, 'w')
            f.write('{"meta":{}}')
            f.close()
        except Exception as e:
            print(e)
            raise Exception('Error in erasing the config file')
        
    def upgradeCallback(self, topic, msg):
        try:
            upgrade_url = json.loads(msg)['d']['upgrade']['fw_url']
        except (ValueError, KeyError, TypeError):
            print('Error parsing upgrade message: invalid JSON or missing keys')
            return

        if is_valid_url(upgrade_url):
            print('rotate')
            rotate_file()
            print('rotated')
            # Download the firmware
            try:
                response = urequests.get(upgrade_url)
                
                if response.status_code == 200:
                    # Write the content to file
                    with open(deviceApp, 'wb') as f:
                        f.write(response.content)
                    
                    print('Firmware download completed')
                    response.close()
                    reset()
                else:
                    print('Download failed with status:', response.status_code)
                    response.close()
            except OSError as err:
                print('Network/file error:', str(err))
            except Exception as err:
                print('Download error:', str(err))
        else:
            print('Invalid URL for upgrade')

    @classmethod
    def saveCfg(cls, cfg):
        '''
        This function takes the configuration string or dict object and writes to the device.cfg configuration file.
        '''
        try:
            if type(cfg) is not dict:
                cfg = json.loads(cfg.replace("'", '"'))
            if 'devId' not in cfg or 'broker' not in cfg:
                raise Exception('the configuration data is invalid')
            f = open(device_cfg, 'w')
            f.write(json.dumps(cfg))
            f.close()
        except Exception as e:
            print(e)
            raise Exception('Error in writing the config file')

