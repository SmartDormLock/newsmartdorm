from RPLCD.i2c import CharLCD

from threading import Lock

import time

# ================= LCD INIT =================
lcd = CharLCD(

    i2c_expander='PCF8574',

    address=0x27,

    port=1,

    cols=20,

    rows=4,

    charmap='A00',

    auto_linebreaks=True
)

# ================= LOCK =================
lcd_lock = Lock()

# ================= HEADER =================
HEADER = "Smart Dorm Lock"

# ================= PAD =================
def pad(text):

    return (text or "")[:20]

# ================= LCD WRITE =================
def lcd_write(

    line2="",
    line3="",
    line4=""
):

    # ================= THREAD SAFE =================
    with lcd_lock:

        # ================= RETRY =================
        for _ in range(2):

            try:

                lcd.clear()

                # ================= HEADER =================
                lcd.cursor_pos = (0, 0)

                lcd.write_string(
                    pad(HEADER)
                )

                # ================= LINE 2 =================
                lcd.cursor_pos = (1, 0)

                lcd.write_string(
                    pad(line2)
                )

                # ================= LINE 3 =================
                lcd.cursor_pos = (2, 0)

                lcd.write_string(
                    pad(line3)
                )

                # ================= LINE 4 =================
                lcd.cursor_pos = (3, 0)

                lcd.write_string(
                    pad(line4)
                )

                return

            except Exception as e:

                print(
                    "?? LCD error retry:",
                    e
                )

                time.sleep(0.1)

        # ================= FAILED =================
        print(
            "?? LCD gagal update (skip)"
        )
