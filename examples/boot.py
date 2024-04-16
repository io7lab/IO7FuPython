# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()

from machine import Pin
pin = Pin(14, Pin.IN, Pin.PULL_UP)        # choose the pin depending on your module
if pin.value():
    import MyDevice
