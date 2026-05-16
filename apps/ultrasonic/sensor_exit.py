import time

from core.hardware.ultrasonic import (
    get_distance
)

from core.hardware.relay import (
    open_door
)

from core.hardware.buzzer import (
    success_beep
)

from core.hardware.lcd import (
    lcd_write
)

# ================= CONFIG =================
DETECTION_DISTANCE = 15
COOLDOWN = 5

# ================= GLOBAL STATE =================
EXIT_ENABLED = True

# ================= LOOP =================
def inside_exit_loop():

    global EXIT_ENABLED

    print("Inside Exit Thread Started")

    last_open = 0

    while True:

        try:

            # ================= PAUSE IF DISABLED =================
            if not EXIT_ENABLED:

                time.sleep(1)
                continue

            # ================= READ SENSOR =================
            distance = get_distance()

            # ================= INVALID =================
            if distance is None:

                time.sleep(1)
                continue

            print(
                f"[EXIT] {distance} cm"
            )

            # ================= DETECT =================
            if distance < DETECTION_DISTANCE:

                now = time.time()

                # ================= COOLDOWN =================
                if (
                    now - last_open
                    > COOLDOWN
                ):

                    print(
                        "INSIDE EXIT DETECTED"
                    )

                    # ================= LCD =================
                    try:

                        lcd_write(

                            "EXIT DETECTED",

                            "Door Opening",

                            ""
                        )

                    except Exception as lcd_error:

                        print(
                            f"[LCD ERROR] {lcd_error}"
                        )

                    # ================= BEEP =================
                    try:

                        success_beep()

                    except Exception as beep_error:

                        print(
                            f"[BUZZER ERROR] {beep_error}"
                        )

                    # ================= OPEN DOOR =================
                    open_door()

                    last_open = now

                    # ================= LCD RESET =================
                    time.sleep(1)

                    try:

                        lcd_write(

                            "SYSTEM READY",

                            "",

                            ""
                        )

                    except Exception as lcd_error:

                        print(
                            f"[LCD ERROR] {lcd_error}"
                        )

            # ================= LOOP DELAY =================
            time.sleep(1)

        except Exception as e:

            print(
                f"[EXIT ERROR] {e}"
            )

            # ================= LCD ERROR =================
            try:

                lcd_write(

                    "EXIT ERROR",

                    "Check Sensor",

                    ""
                )

            except:

                pass

            time.sleep(2)
