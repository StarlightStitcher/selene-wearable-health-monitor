from machine import I2C
from time import sleep_ms

_CALIBRATION_OFFSET = 67.5
 
class MAX30205:
    _REG_TEMPERATURE = 0x00
    _REG_CONFIG      = 0x01
 
    def __init__(self, i2c: I2C, addr: int = 0x48):
        self.i2c  = i2c
        self.addr = addr
        self._init_sensor()
 
    def _init_sensor(self):
        self.i2c.writeto_mem(self.addr, self._REG_CONFIG, b'\x00')
        sleep_ms(50)
 
    def _read_raw(self) -> int:
        data = self.i2c.readfrom_mem(self.addr, self._REG_TEMPERATURE, 2)
        raw = (data[0] << 8) | data[1]
        if raw & 0x8000:
            raw -= 65536
        return raw
 
    def read_celsius(self) -> float:
        raw_temp = self._read_raw() / 256.0
        return round(raw_temp + _CALIBRATION_OFFSET, 2)
 
    def is_connected(self) -> bool:
        return self.addr in self.i2c.scan()
    