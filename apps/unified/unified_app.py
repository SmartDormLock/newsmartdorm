import subprocess
import time

from core.auth.fingerprint_auth import scan_fingerprint
from core.auth.rfid_auth import scan_rfid
from core.hardware.relay import open_door
from core.hardware.lcd import lcd_write
from core.auth.master_user import load_master_users


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

    safe_lcd(
        "ACCESS GRANTED",
        str(name),
        "Door Opening..."
    )

    open_door()

    time.sleep(0.5)

    safe_lcd(
        "DOOR LOCKED",
        "",
        "Ready..."
    )

    time.sleep(2)

    safe_lcd(
        "SYSTEM READY",
        "",
        ""
    )


# ================= FACE =================
def scan_face_external(attempt):

    print("\n📷 Menjalankan Face Recognition...")

    safe_lcd(
        "MODE: FACE",
        "Scanning wajah...",
        f"{attempt}/{MAX_ATTEMPT}"
    )

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

        safe_lcd(
            "SCAN RFID",
            "Tempel kartu",
            f"{attempt}/{MAX_ATTEMPT}"
        )

        result = scan_rfid()

        if result:

            rfid_name = result["name"]

            print(f"✅ RFID valid: {rfid_name}")

            safe_lcd(
                "RFID OK",
                str(rfid_name),
                ""
            )

            time.sleep(1)

            return rfid_name

        else:

            print(f"❌ RFID gagal ({attempt}/{MAX_ATTEMPT})")

            safe_lcd(
                "RFID FAILED",
                "",
                f"{attempt}/{MAX_ATTEMPT}"
            )

            time.sleep(1)

    return None


# ================= MODE FACE =================
def mode_face():

    print("\n=== MODE 1: FACE + RFID ===")

    # reload dynamic
    master_users = load_master_users()

    for attempt in range(1, MAX_ATTEMPT + 1):

        result = scan_face_external(attempt)

        if result:

            print(f"🎉 Face dikenali: {result}")

            safe_lcd(
                "FACE OK",
                f"Hello {result}",
                "Scan RFID..."
            )

            time.sleep(1)

            # RFID setelah face sukses
            rfid_name = rfid_verify()

            # ================= RFID SUCCESS =================
            if rfid_name:

                print(f"📡 RFID terbaca: {rfid_name}")

                if result in master_users:

                    if rfid_name == result:

                        print("🔐 MATCH: Face & RFID sesuai")

                        door_sequence(result)

                        return True

                    else:

                        print("🚫 MISMATCH: Face != RFID")

                        safe_lcd(
                            "RFID MISMATCH",
                            "Use Finger",
                            ""
                        )

                        time.sleep(3)

                        # fallback contextual
                        return {
                            "status": "rfid_failed",
                            "user": result
                        }

                else:

                    print("🚫 User tidak ada di master")

                    safe_lcd(
                        "UNKNOWN USER",
                        "",
                        ""
                    )

                    time.sleep(2)

                    return False

            # ================= RFID FAILED =================
            else:

                print("❌ RFID gagal")

                safe_lcd(
                    "RFID FAILED",
                    "Use Finger",
                    ""
                )

                time.sleep(3)

                # fallback contextual
                return {
                    "status": "rfid_failed",
                    "user": result
                }

        # ================= FACE FAILED =================
        else:

            print(f"❌ Face gagal ({attempt}/{MAX_ATTEMPT})")

            remaining = MAX_ATTEMPT - attempt

            safe_lcd(
                "FACE FAILED",
                f"Sisa: {remaining}",
                "Retry..."
            )

            time.sleep(2)

    return False


# ================= MODE FINGER =================
def mode_fingerprint(expected_user=None):

    print("\n=== MODE 2: FINGERPRINT + RFID ===")

    for attempt in range(1, MAX_ATTEMPT + 1):

        safe_lcd(
            "MODE: FINGER",
            "Scan Finger",
            f"{attempt}/{MAX_ATTEMPT}"
        )

        result = scan_fingerprint()

        if result:

            print(f"🎉 Fingerprint dikenali: {result}")

            # ================= CONTEXTUAL CHECK =================
            if expected_user:

                if result != expected_user:

                    print("🚫 Fingerprint bukan user yang sama")

                    safe_lcd(
                        "INVALID USER",
                        "Fingerprint mismatch",
                        ""
                    )

                    time.sleep(2)

                    return False

            safe_lcd(
                "FINGER OK",
                str(result),
                "Scan RFID..."
            )

            time.sleep(1)

            rfid_name = rfid_verify()

            if rfid_name:

                if rfid_name == result:

                    print("🔐 MATCH: Fingerprint & RFID sesuai")

                    door_sequence(result)

                    return True

                else:

                    print("🚫 MISMATCH Fingerprint & RFID")

                    safe_lcd(
                        "ACCESS DENIED",
                        "Mismatch!",
                        ""
                    )

                    time.sleep(2)

                    return False

            else:

                print("❌ RFID gagal")

                safe_lcd(
                    "RFID FAILED",
                    "",
                    ""
                )

                time.sleep(2)

                return False

        else:

            print(f"❌ Fingerprint gagal ({attempt}/{MAX_ATTEMPT})")

            safe_lcd(
                "FINGER FAILED",
                "",
                f"{attempt}/{MAX_ATTEMPT}"
            )

            time.sleep(1)

    return False


# ================= MAIN =================
def main():

    print("\n🔐 SMART DOOR SYSTEM STARTED")

    safe_lcd(
        "SYSTEM READY",
        "",
        ""
    )

    time.sleep(2)

    # ================= FACE MODE =================
    face_result = mode_face()

    # ================= SUCCESS =================
    if face_result == True:
        return

    # ================= CONTEXTUAL FALLBACK =================
    if isinstance(face_result, dict):

        if face_result["status"] == "rfid_failed":

            expected_user = face_result["user"]

            print(f"\n⚠️ Fallback fingerprint untuk {expected_user}")

            safe_lcd(
                "USE FINGER",
                expected_user,
                "5 sec..."
            )

            # countdown
            for i in range(5, 0, -1):

                safe_lcd(
                    "USE FINGER",
                    expected_user,
                    f"{i} sec..."
                )

                time.sleep(1)

            # fingerprint contextual
            if mode_fingerprint(expected_user):
                return

            # gagal contextual fingerprint
            print("\n⛔ AKSES DITOLAK")

            safe_lcd(
                "ACCESS DENIED",
                "Fingerprint Failed",
                ""
            )

            time.sleep(2)

            return

    # ================= GLOBAL FALLBACK =================
    # HANYA kalau face benar-benar gagal total
    print("\n⚠️ Face gagal total")

    safe_lcd(
        "FACE UNKNOWN",
        "Use Fingerprint",
        ""
    )

    time.sleep(3)

    if mode_fingerprint():
        return

    # ================= TOTAL FAILED =================
    print("\n⛔ AKSES DITOLAK TOTAL")

    safe_lcd(
        "ACCESS DENIED",
        "Try Again",
        ""
    )

    time.sleep(2)


# ================= ENTRY =================
if __name__ == "__main__":
    main()
