from machine import I2C, Pin
from time import sleep_ms
from max30102 import MAX30102
 
 
def main():
    i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400_000)
 
    sensor = MAX30102(i2c)
 
    if not sensor.is_connected():
        print("ERROR: MAX30102 not found on I2C bus.")
        print("Detected devices:", i2c.scan())
        return
 
    print("MAX30102 found. Place your finger on the sensor...\n")

    while True:
        if sensor.get_data_present() > 0:
            red, ir = sensor.read_fifo()
            print(f"Red: {red}  |  IR: {ir}")
        sleep_ms(100)
 
 
if __name__ == "__main__":
    main()