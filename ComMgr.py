import ubluetooth
import network
from machine import reset, unique_id
import time
import ubinascii
import json

wifi_cfg = 'wifi.cfg'


def getUniqName(name):
    '''
    Generate the unique device name
    '''
    mac = ubinascii.hexlify(unique_id()).decode('utf-8')
    devName = name + '-' + mac[-6:-1] + mac[-1]
    return devName

####### BLE Manger ###########


class BLE():
    def __init__(self, name, myCallback=None):
        self.name = name
        self.myCallback = myCallback
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        # these 3 lines is the temp fix for the BLE Device name
        self.ble.config('gap_name')
        self.ble.config(gap_name=name)
        self.ble.config('gap_name')

        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        print('connected')
        self.send('hello')

    def disconnected(self):
        print('disconnected')

    def ble_irq(self, event, data):
        if event == 1:
            '''Central connected'''
            self.conn, addr_type, addr = data
            self.connected()

        elif event == 2:
            '''Central disconnected'''
            self.advertiser()
            self.disconnected()

        elif event == 3:
            '''New message received'''
            buffer = self.ble.gatts_read(self.rx)
            message = buffer.decode('UTF-8').strip()
            if message == 'reboot':
                reset()
            elif saveWiFiConfig(message):
                # successful exit with cfg saved. if no ssid/pw,
                # then the next elif will be evaluated
                self.send('wifi config saved')
            elif self.myCallback:       # if myCallback is a valid function
                if not self.myCallback(message):
                    self.send('"' + message + '" not understood')
            else:
                self.send('"' + message + '" not understood')

    def register(self):
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID),
                  ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY)

        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        try:
            self.ble.gatts_notify(self.conn, self.tx, data + '\n')
        except:
            pass

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        self.ble.gap_advertise(100, bytearray(
            '\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name)

    def setCallback(self, callback):
        self.myCallback = callback


##### WiFi Manager ##########
wifi_conn = False


def connectWiFi(uniqName):
    '''
    This connects the device to the Wireless LAN, if The ssid and 
    the password are stored in the file named 'wifi.cfg'
    '''
    global wifi_conn
    try:
        f = open(wifi_cfg, 'r')
        line = f.read()
        cred = json.loads(line)
        ssid = cred['ssid'].strip()
        pw = cred['pw'].strip()
        f.close()
    except OSError as e:
        print('no config file')
        return False
    except:
        print('other exception')
        return False

    try:
        if ssid is '':
            print('ssid is empty')
        else:
            try:
                import network
                import time
                nic = network.WLAN(network.STA_IF)
                nic.active(True)
                time.sleep_ms(1)
                nic.config(dhcp_hostname=uniqName)
                nic.connect(ssid, pw)
                n_wait = 0
                while (not wifi_conn and n_wait < 10):
                    time.sleep(2)
                    if nic.status() == network.STAT_GOT_IP:
                        wifi_conn = True
                    n_wait = n_wait + 1
                if wifi_conn:
                    print(nic.ifconfig())
                    nic.config(dhcp_hostname=uniqName)
                    print('\n\t\t\tHOSTNAME : ' + uniqName + '\n')
                    return nic
                else:
                    print('wifi connection faild. check ssid / pw')
            except Exception as e:
                print(e)
                print('other exception')
    except:
        print('ssid not defined')

    return False


def saveWiFiConfig(message):
    '''
    This saves the WiFi ssid and password to 'wifi.cfg'
    '''
    key_value = message.split(':')
    if key_value[0].strip() not in 'ssid|pw':
        return False
    try:
        try:
            f = open(wifi_cfg, 'r')
            line = f.read()
            cred = json.loads(line)
            f.close()
        except:
            cred = {}
        cred[key_value[0]] = key_value[1]
        cred = json.dumps(cred)

        f = open(wifi_cfg, 'w')
        f.write(cred)
        f.close()
    except OSError:
        print('error in wifi cfg file wriging')
        return False

    return True


####### BLE / WiFi APIs ######

def startBLE(name, myBLECallback=None):
    '''
    This starts the BLE service with the given name and the callback if specified.
        startBLE(devName, myBLEcallback)
        devName will be the BLE device name once started
        myBLECallback is the optional callback function you define and pass.
        This callback should return True, if the callback processed as desired,
        or return False/do nothing if the given message is not processed by
        this callback, so the remaining built-in callback should continue if any
    '''
    ble = BLE(getUniqName(name), myBLECallback)
    return ble


def startWiFi(name):
    '''
    This starts the WiFi connection with the given name as the mDNS name.
    "name.local" is the mDNS name for the device, when you connect to it.
    '''
    return connectWiFi(getUniqName(name))
