# core/hardware/ultrasonic.py

import lgpio
import time
import statistics

# ================= GPIO CONFIG =================
TRIG = 23
ECHO = 24

# ================= GPIO INIT =================
h = lgpio.gpiochip_open(0)

lgpio.gpio_claim_output(h, TRIG)
lgpio.gpio_claim_input(h, ECHO)

# ================= CONSTANT =================
MAX_DISTANCE = 400
MIN_DISTANCE = 2

SAMPLE_COUNT = 5

# ================= SINGLE READ =================
def _read_once():

    # ================= RESET TRIGGER =================
    lgpio.gpio_write(h, TRIG, 0)
    time.sleep(0.08)

    # ================= SEND PULSE =================
    lgpio.gpio_write(h, TRIG, 1)
    time.sleep(0.00001)
    lgpio.gpio_write(h, TRIG, 0)

    pulse_start = None
    pulse_end = None

    # ================= WAIT ECHO START =================
    timeout = time.time()

    while lgpio.gpio_read(h, ECHO) == 0:

        pulse_start = time.time()

        if time.time() - timeout > 0.04:
            return None

    # ================= WAIT ECHO END =================
    timeout = time.time()

    while lgpio.gpio_read(h, ECHO) == 1:

        pulse_end = time.time()

        if time.time() - timeout > 0.04:
            return None

    # ================= VALIDATE =================
    if pulse_start is None or pulse_end is None:
        return None

    # ================= CALCULATE =================
    duration = pulse_end - pulse_start

    distance = duration * 17150

    # ================= FILTER INVALID =================
    if (
        distance < MIN_DISTANCE
        or
        distance > MAX_DISTANCE
    ):
        return None

    return round(distance, 2)

# ================= GET DISTANCE =================
def get_distance():

    readings = []

    # ================= MULTI SAMPLE =================
    for _ in range(SAMPLE_COUNT):

        distance = _read_once()

        if distance is not None:

            readings.append(distance)

    # ================= NO VALID DATA =================
    if len(readings) < 2:

        return None

    # ================= MEDIAN FILTER =================
    filtered_distance = statistics.median(readings)

    return round(filtered_distance, 2)

# ================= CLEANUP =================
def cleanup():

    lgpio.gpiochip_close(h)
