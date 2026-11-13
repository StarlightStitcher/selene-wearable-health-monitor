from ble_simple_peripheral import BLEUART as _BLEUART

class BLEUART:
    def __init__(self, name="Wearable"):
        self.ble = _BLEUART(name)

    def send(self, msg):
        self.ble.write(msg)