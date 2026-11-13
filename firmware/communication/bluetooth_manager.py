import bluetooth
from ble_simple_peripheral import BLESimplePeripheral
from time import sleep_ms
 
 
class BluetoothManager:
    def __init__(self, name="Wearable"):
        self._peripheral = None
        for attempt in range(3):
            try:
                self._ble = bluetooth.BLE()
                self._peripheral = BLESimplePeripheral(self._ble, name=name)
                print(f"BLE advertising as '{name}'")
                return
            except OSError:
                print(f"BLE init failed, retrying... ({attempt+1}/3)")
                sleep_ms(1000)
        print("WARNING: Bluetooth unavailable — continuing without BLE")
 
    def is_connected(self) -> bool:
        if self._peripheral is None:
            return False
        return self._peripheral.is_connected()
 
    def send(self, msg: str):
        if self._peripheral and self.is_connected():
            self._peripheral.send(msg.encode("utf-8"))
 
    def send_readings(self, hr, spo2, temp, contact, rr=None):
        hr_str   = str(hr)   if hr   is not None else "--"
        spo2_str = str(spo2) if spo2 is not None else "--"
        rr_str   = str(rr)   if rr   is not None else "--"
        msg = f"HR:{hr_str},SPO2:{spo2_str},TEMP:{temp},RR:{rr_str},CONTACT:{1 if contact else 0}\n"
        self.send(msg)