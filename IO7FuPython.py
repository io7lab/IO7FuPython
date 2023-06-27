import time
import json
from umqtt.robust import MQTTClient
import machine
import os

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
        else:
            self.broker = broker
            self.devId = devId
            self.token = token
        self.meta = cfg['meta'] if 'meta' in cfg else {}
        self.meta['pubInterval'] = self.meta['pubInterval'] if 'pubInterval' in self.meta else 5000
        self.cmdCallback = None
        self.resetCallback = None
        self.updateCallback = None
        self.upgradeCallback = None
        if 'ca.crt' in os.listdir():
            port = '8883'
            ssl = True
            ssl_params = {'cert' : 'ca.crt'}
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
            if self.upgradeCallback:
                self.upgradeCallback(topic, msg)
        elif self.cmdTopicBase in topicStr and self.cmdCallback:
            self.cmdCallback(topic, msg)
            
    def publishEvent(self, evtId, data, fmt='json', qos=0, retain=False):
        self.client.publish(self.evtTopic + '%s/fmt/%s' % (evtId, fmt), data, qos=qos, retain=retain)
        
    def connect(self):
        self.client.set_last_will(f"iot3/{self.devId}/evt/connection/fmt/json", 
                        '{"d":{"status":"offline"}}', retain=True, qos=0, )
        self.client.connect()
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
        machine.reset()

    def setUserMeta(self, callback):
        self.updateCallback = callback
        
    def setUpgradeCallback(self, callback):
        self.upgradeCallback = callback

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