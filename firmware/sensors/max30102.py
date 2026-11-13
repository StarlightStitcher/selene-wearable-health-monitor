from machine import I2C
from time import sleep_ms

_REG_INTR_STATUS_1  = 0x00
_REG_INTR_STATUS_2  = 0x01
_REG_INTR_ENABLE_1  = 0x02
_REG_INTR_ENABLE_2  = 0x03
_REG_FIFO_WR_PTR    = 0x04
_REG_OVF_COUNTER    = 0x05
_REG_FIFO_RD_PTR    = 0x06
_REG_FIFO_DATA      = 0x07
_REG_FIFO_CONFIG    = 0x08
_REG_MODE_CONFIG    = 0x09
_REG_SPO2_CONFIG    = 0x0A
_REG_LED1_PA        = 0x0C
_REG_LED2_PA        = 0x0D
_REG_PILOT_PA       = 0x10
_REG_PART_ID        = 0xFF


class MAX30102:
    def __init__(self, i2c: I2C, addr: int = 0x57):
        self.i2c  = i2c
        self.addr = addr
        self._reset()
        sleep_ms(1000)
        self._clear_interrupts()
        self._setup()

    def _write(self, reg: int, value: int):
        self.i2c.writeto_mem(self.addr, reg, bytes([value]))

    def _read(self, reg: int, length: int) -> bytes:
        return self.i2c.readfrom_mem(self.addr, reg, length)

    def _reset(self):
        self._write(_REG_MODE_CONFIG, 0x40)

    def _clear_interrupts(self):
        self._read(_REG_INTR_STATUS_1, 1)
        self._read(_REG_INTR_STATUS_2, 1)

    def _setup(self):
        self._write(_REG_INTR_ENABLE_1, 0xC0)
        self._write(_REG_INTR_ENABLE_2, 0x00)
        self._write(_REG_FIFO_WR_PTR,   0x00)
        self._write(_REG_OVF_COUNTER,   0x00)
        self._write(_REG_FIFO_RD_PTR,   0x00)
        self._write(_REG_FIFO_CONFIG,   0x4F)
        self._write(_REG_MODE_CONFIG,   0x03)
        self._write(_REG_SPO2_CONFIG,   0x07)
        self._write(_REG_LED1_PA,       0x1F)
        self._write(_REG_LED2_PA,       0x1F)
        self._write(_REG_PILOT_PA,      0x7F)

    def is_connected(self) -> bool:
        return self.addr in self.i2c.scan()

    def flush_fifo(self):
        """Reset FIFO pointers to discard stale data."""
        self._write(_REG_FIFO_WR_PTR, 0x00)
        self._write(_REG_OVF_COUNTER, 0x00)
        self._write(_REG_FIFO_RD_PTR, 0x00)

    def get_data_present(self) -> int:
        read_ptr  = self._read(_REG_FIFO_RD_PTR, 1)[0]
        write_ptr = self._read(_REG_FIFO_WR_PTR, 1)[0]
        if read_ptr == write_ptr:
            return 0
        num_samples = write_ptr - read_ptr
        if num_samples < 0:
            num_samples += 32
        return num_samples

    def read_fifo(self) -> tuple:
        self._clear_interrupts()
        d = self._read(_REG_FIFO_DATA, 6)
        red = (d[0] << 16 | d[1] << 8 | d[2]) & 0x03FFFF
        ir  = (d[3] << 16 | d[4] << 8 | d[5]) & 0x03FFFF
        return red, ir

    def read_samples(self, amount: int = 100) -> tuple:
        red_buf = []
        ir_buf  = []
        count   = amount
        while count > 0:
            available = self.get_data_present()
            while available > 0 and count > 0:
                red, ir = self.read_fifo()
                red_buf.append(red)
                ir_buf.append(ir)
                available -= 1
                count     -= 1
        return red_buf, ir_buf