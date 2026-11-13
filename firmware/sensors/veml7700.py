from machine import I2C
from time import sleep_ms

class VEML7700:
    def __init__(self, i2c, addr=0x10):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(addr, 0x00, b'\x00\x08')
        sleep_ms(100)

    def read_lux(self):
        data = self.i2c.readfrom_mem(self.addr, 0x04, 2)
        raw = int.from_bytes(data, 'little')
        return round(raw * 0.0576, 2)

    def is_dark(self, threshold=6.0):
        return self.read_lux() < threshold

    def is_connected(self):
        return self.addr in self.i2c.scan()