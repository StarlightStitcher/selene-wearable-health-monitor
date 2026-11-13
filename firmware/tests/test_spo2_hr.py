from machine import I2C, Pin
from time import sleep_ms
from max30102 import MAX30102
from spo2_hr import calculate_heart_rate, calculate_spo2

def main():
    i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400_000)
 
    sensor = MAX30102(i2c)
 
    if not sensor.is_connected():
        print("ERROR: MAX30102 not found on I2C bus.")
        print("Detected devices:", i2c.scan())
        return
 
    print("MAX30102 found.")
    print("Place your finger firmly on the sensor and hold still...\n")

    while True:
        print("Collecting samples...")
 
        # Collect 100 samples at 100Hz = ~1 second of data
        red_buf, ir_buf = sensor.read_samples(200)
 
        # Calculate heart rate and SpO2
        hr   = calculate_heart_rate(ir_buf, sample_rate=25)
        spo2 = calculate_spo2(red_buf, ir_buf)
 
        # Print results
        if hr is None:
            print("Heart Rate: -- (no finger detected or not enough peaks)")
        else:
            print(f"Heart Rate: {hr} BPM")
 
        if spo2 is None:
            print("SpO2: -- (no finger detected or signal too weak)")
        else:
            print(f"SpO2: {spo2} %")
 
        print()
        sleep_ms(500)
 
 
if __name__ == "__main__":
    main()    