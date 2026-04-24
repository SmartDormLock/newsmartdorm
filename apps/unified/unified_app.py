import subprocess
import time

from core.auth.fingerprint_auth import scan_fingerprint
from core.auth.rfid_auth import scan_rfid
from core.hardware.relay import open_door
from core.hardware.lcd import lcd_write


MAX_ATTEMPT = 3
FACE_PY = "/home/raspi5/newsmartdorm/envs/face_env/bin/python"


# ================= SAFE LCD =================
def safe_lcd(*args):
    try:
        lcd_write(*args)
    except Exception as e:
        print("⚠️ LCD skip:", e)


# ================= DOOR SEQUENCE =================
def door_sequence(name):
    safe_lcd("ACCESS GRANTED", str(name), "Door Opening...")

    open_door()

    time.sleep(0.5)  # 🔥 penting buat stabilin I2C

    safe_lcd("DOOR LOCKED", "", "Ready...")
    time.sleep(2)

    safe_lcd("SYSTEM READY", "", "")


# ================= FACE =================
def scan_face_external(attempt):
    print("\n📷 Menjalankan Face Recognition...")

    safe_lcd("MODE: FACE", "Scanning wajah...", f"{attempt}/{MAX_ATTEMPT}")

    try:
        result = subprocess.run(
            [FACE_PY, "-m", "apps.face.face_app", "--no-relay"],
            capture_output=True,
            text=True
        )

        output = (result.stdout or "") + "\n" + (result.stderr or "")
        output = output.strip()

        print("----- FACE OUTPUT -----")
        print(output)
        print("-----------------------")

        for line in output.splitlines():
            if "Akses:" in line:
                return line.split("Akses:")[-1].strip()

    except Exception as e:
        print("❌ Face error:", e)

    return None


# ================= RFID =================
def rfid_verify():
    print("\n📡 Verifikasi RFID...")

    for attempt in range(1, MAX_ATTEMPT + 1):
        safe_lcd("SCAN RFID", "Tempel kartu", f"{attempt}/{MAX_ATTEMPT}")

        result = scan_rfid()

        if result:
            print(f"✅ RFID valid: {result}")
            safe_lcd("RFID OK", str(result), "")
            time.sleep(1)
            return True
        else:
            print(f"❌ RFID gagal ({attempt}/{MAX_ATTEMPT})")
            safe_lcd("RFID FAILED", "", f"{attempt}/{MAX_ATTEMPT}")
            time.sleep(1)

    return False


# ================= MODE FACE =================
def mode_face():
    print("\n=== MODE 1: FACE + RFID ===")

    for attempt in range(1, MAX_ATTEMPT + 1):
        result = scan_face_external(attempt)

        if result:
            print(f"🎉 Face dikenali: {result}")

            safe_lcd("FACE OK", f"Hello {result}", "Scan RFID...")
            time.sleep(1)

            if rfid_verify():
                door_sequence(result)
                return True
            else:
                safe_lcd("RFID FAILED", "", "Back")
                time.sleep(2)
                return False

        else:
            print(f"❌ Face gagal ({attempt}/{MAX_ATTEMPT})")
            safe_lcd("FACE FAILED", "", f"{attempt}/{MAX_ATTEMPT}")
            time.sleep(1)

    return False


# ================= MODE FINGER =================
def mode_fingerprint():
    print("\n=== MODE 2: FINGERPRINT + RFID ===")

    for attempt in range(1, MAX_ATTEMPT + 1):
        safe_lcd("MODE: FINGER", "Scan Finger", f"{attempt}/{MAX_ATTEMPT}")

        result = scan_fingerprint()

        if result:
            print(f"🎉 Fingerprint dikenali: {result}")

            safe_lcd("FINGER OK", str(result), "Scan RFID...")
            time.sleep(1)

            if rfid_verify():
                door_sequence(result)
                return True
            else:
                safe_lcd("RFID FAILED", "", "Back")
                time.sleep(2)
                return False

        else:
            print(f"❌ Fingerprint gagal ({attempt}/{MAX_ATTEMPT})")
            safe_lcd("FINGER FAILED", "", f"{attempt}/{MAX_ATTEMPT}")
            time.sleep(1)

    return False


# ================= MAIN =================
def main():
    print("\n🔐 SMART DOOR SYSTEM STARTED")

    safe_lcd("SYSTEM READY", "", "")
    time.sleep(2)

    if mode_face():
        return

    print("\n⚠️ Pindah ke mode fingerprint...")
    safe_lcd("SWITCH MODE", "Fingerprint", "")
    time.sleep(2)

    if mode_fingerprint():
        return

    print("\n⛔ AKSES DITOLAK TOTAL")
    safe_lcd("ACCESS DENIED", "Try Again", "")
    time.sleep(2)


# ================= ENTRY =================
if __name__ == "__main__":
    main()
