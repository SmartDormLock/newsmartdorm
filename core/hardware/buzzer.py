import time
import lgpio


# ================= CONFIG =================
BUZZER_PIN = 18

BUZZER_ENABLED = True


# ================= GPIO INIT =================
h = lgpio.gpiochip_open(0)

lgpio.gpio_claim_output(
    h,
    BUZZER_PIN
)


# ================= LOW LEVEL =================
def beep(duration=0.1):

    if not BUZZER_ENABLED:
        return

    lgpio.gpio_write(
        h,
        BUZZER_PIN,
        1
    )

    time.sleep(duration)

    lgpio.gpio_write(
        h,
        BUZZER_PIN,
        0
    )


# ================= SUCCESS =================
def success_beep():

    if not BUZZER_ENABLED:
        return

    for _ in range(2):

        beep(0.1)

        time.sleep(0.1)


# ================= ERROR =================
def error_beep():

    if not BUZZER_ENABLED:
        return

    beep(0.7)


# ================= WARNING =================
def warning_beep():

    if not BUZZER_ENABLED:
        return

    for _ in range(3):

        beep(0.08)

        time.sleep(0.08)


# ================= SCAN =================
def scan_beep():

    if not BUZZER_ENABLED:
        return

    beep(0.05)


# ================= CUSTOM =================
def custom_beep(
    count=1,
    duration=0.1,
    delay=0.1
):

    if not BUZZER_ENABLED:
        return

    for _ in range(count):

        beep(duration)

        time.sleep(delay)


# ================= CLEANUP =================
def cleanup_buzzer():

    lgpio.gpio_write(
        h,
        BUZZER_PIN,
        0
    )

    lgpio.gpiochip_close(h)


# ================= TEST =================
if __name__ == "__main__":

    print("\n🔊 Testing buzzer...\n")

    print("✅ Success beep")
    success_beep()

    time.sleep(1)

    print("⚠️ Warning beep")
    warning_beep()

    time.sleep(1)

    print("❌ Error beep")
    error_beep()

    print("\n🎉 Test selesai\n")

    cleanup_buzzer()
