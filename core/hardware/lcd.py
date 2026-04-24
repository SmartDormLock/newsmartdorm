from RPLCD.i2c import CharLCD
import time

lcd = CharLCD(
    i2c_expander='PCF8574',
    address=0x27,
    port=1,
    cols=20,
    rows=4,
    charmap='A00',
    auto_linebreaks=True
)

HEADER = "Smart Dorm Lock"


def pad(text):
    return (text or "")[:20]


def lcd_write(line2="", line3="", line4=""):
    # 🔥 retry biar tahan error I2C
    for _ in range(2):
        try:
            lcd.clear()

            lcd.cursor_pos = (0, 0)
            lcd.write_string(pad(HEADER))

            lcd.cursor_pos = (1, 0)
            lcd.write_string(pad(line2))

            lcd.cursor_pos = (2, 0)
            lcd.write_string(pad(line3))

            lcd.cursor_pos = (3, 0)
            lcd.write_string(pad(line4))

            return

        except Exception as e:
            print("⚠️ LCD error retry:", e)
            time.sleep(0.1)

    print("⚠️ LCD gagal update (skip)")
