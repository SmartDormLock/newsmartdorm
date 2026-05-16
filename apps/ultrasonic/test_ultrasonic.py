# apps/ultrasonic/test_ultrasonic.py

import lgpio
import time

# ================= GPIO CONFIG =================
TRIG = 23
ECHO = 24

# ================= GPIO INIT =================
h = lgpio.gpiochip_open(0)

lgpio.gpio_claim_output(h, TRIG)
lgpio.gpio_claim_input(h, ECHO)

# ================= FUNCTION =================
def get_distance():

    # pastikan trigger LOW
    lgpio.gpio_write(h, TRIG, 0)
    time.sleep(0.05)

    # kirim pulse 10us
    lgpio.gpio_write(h, TRIG, 1)
    time.sleep(0.00001)
    lgpio.gpio_write(h, TRIG, 0)

    pulse_start = time.time()
    pulse_end = time.time()

    # ================= WAIT ECHO START =================
    timeout = time.time()

    while lgpio.gpio_read(h, ECHO) == 0:

        pulse_start = time.time()

        if time.time() - timeout > 0.03:
            return None

    # ================= WAIT ECHO END =================
    timeout = time.time()

    while lgpio.gpio_read(h, ECHO) == 1:

        pulse_end = time.time()

        if time.time() - timeout > 0.03:
            return None

    # ================= CALCULATE =================
    duration = pulse_end - pulse_start

    distance = duration * 17150

    # ================= FILTER INVALID =================
    if distance <= 2 or distance >= 400:
        return None

    return round(distance, 2)

# ================= MAIN LOOP =================
try:

    print("Ultrasonic Test Started")

    while True:

        distance = get_distance()

        if distance is not None:

            print(f"Distance: {distance} cm")

            # ================= DETECTION =================
            if distance < 15:

                print("OBJECT DETECTED!")

        else:

            print("Invalid reading")

        time.sleep(0.5)

except KeyboardInterrupt:

    print("\nStopped by user")

finally:

    lgpio.gpiochip_close(h)
