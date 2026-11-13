from machine import I2C, Pin
from time import sleep
from max30205 import MAX30205 
 
def main():
    i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
 
    sensor = MAX30205(i2c)

    if not sensor.is_connected():
        print("ERROR: MAX30205 not found on I2C bus.")
        print("Detected devices:", i2c.scan())
        return 
 
    print("MAX30205 found. Starting temperature readings...\n")

    while True:
        temp_c = sensor.read_celsius()
        print(f"Temperature: {temp_c} °C")
        sleep(1)

if __name__ == "__main__": 
    main()
