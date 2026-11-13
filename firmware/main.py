# https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html
# https://docs.micropython.org/en/latest/rp2/quickref.html
# https://docs.micropython.org/en/latest/library/index.html

# Potential Library Candidate for MAX30102
# https://github.com/n-elia/MAX30102-MicroPython-driver

# =============================================================================
# main.py — EGRE 541 Wireless Vital Signs Wearable
# Regina Velazquez Hernandez & Sarah Garza
# Virginia Commonwealth University
# =============================================================================

import bluetooth
from machine import I2C, Pin
from time import sleep_ms
from max30205 import MAX30205
from veml7700 import VEML7700
from max30102 import MAX30102
from ble_simple_peripheral import BLESimplePeripheral
from spo2_hr import calculate_heart_rate, calculate_spo2, calculate_respiratory_rate


def main():
    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------
    print("Initializing system...")

    sleep_ms(2000)
    ble = bluetooth.BLE()
    p   = BLESimplePeripheral(ble, name="Wearable")

    i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400_000)

    temp_sensor  = MAX30205(i2c)
    light_sensor = VEML7700(i2c)
    pulse_sensor = MAX30102(i2c)

    print("Scanning I2C bus:", [hex(x) for x in i2c.scan()])

    if not temp_sensor.is_connected():
        print("WARNING: MAX30205 temperature sensor not found")
    if not light_sensor.is_connected():
        print("WARNING: VEML7700 light sensor not found")
    if not pulse_sensor.is_connected():
        print("WARNING: MAX30102 pulse sensor not found")

    print("System ready.\n")

    prev_contact = False

    # -------------------------------------------------------------------------
    # MAIN LOOP
    # -------------------------------------------------------------------------
    while True:
        contact = light_sensor.is_dark()
        temp    = temp_sensor.read_celsius()

        if contact:
            # Re-initialize sensor when contact is first detected
            # _setup() resets FIFO and puts sensor back into SpO2 mode
            if not prev_contact:
                print("Contact detected — reinitializing sensor...")
                pulse_sensor._setup()
                sleep_ms(1000)

            red_buf, ir_buf = pulse_sensor.read_samples(300)
            hr   = calculate_heart_rate(ir_buf, sample_rate=25)
            spo2 = calculate_spo2(red_buf, ir_buf)
            rr   = calculate_respiratory_rate(ir_buf, sample_rate=25)
        else:
            hr   = None
            spo2 = None
            rr   = None
            print("WARNING: No skin contact detected — reposition sensor")

        prev_contact = contact

        hr_str   = f"{hr} BPM"    if hr   is not None else "--"
        spo2_str = f"{spo2}%"     if spo2 is not None else "--"
        rr_str   = f"{rr} br/min" if rr   is not None else "--"

        print(f"Temp: {temp}°C | HR: {hr_str} | SpO2: {spo2_str} | RR: {rr_str} | Contact: {'YES' if contact else 'NO'}")

        if p.is_connected():
            msg  = 'HR:' + str(hr) + ',SPO2:' + str(spo2) + ',TEMP:' + str(temp)
            msg += ',RR:' + str(rr) + ',CONTACT:' + str(1 if contact else 0)
            p.send(msg.encode('utf-8'))

        sleep_ms(500)


while True:
    try:
        main()
    except Exception as e:
        print("Error:", e)
        sleep_ms(1000)