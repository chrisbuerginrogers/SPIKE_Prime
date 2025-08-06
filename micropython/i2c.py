from machine import Pin, SoftI2C
import time

p = Pin.cpu

p.A10.value(1)
p.D7.value(1)
p.D8.value(1)

i2c = SoftI2C(freq=1000, scl=p.D8, sda=p.D7, timeout=5000)

devices = i2c.scan()
if devices:
    for d in devices:
        print(hex(d))