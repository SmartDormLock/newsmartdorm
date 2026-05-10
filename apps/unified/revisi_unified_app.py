import subprocess
import time

from core.auth.fingerprint_auth import scan_fingerprint
from core.auth.rfid_auth import scan_rfid
from core.hardware.relay import open_door
from core.hardware.lcd import lcd_write

# ================= BUZZER =================
from core.hardware.buzzer import (
    success_beep,
    error_beep,
    warning_beep,
    scan_beep
)

# ================= LOGGER =================
import core.utils.logger as logger

from core.auth.master_user import load_master_users


MAX_ATTEMPT = 3
FACE_PY = "/home/raspi5/newsmartdorm/envs/face_env/bin/python"


# ================= SAFE LCD =================
def safe_lcd(*args):

    try:

        lcd_write(*args)

    except Exception as e:

        print("⚠️ LCD skip:", e)

        logger.log_error(
            f"LCD ERROR: {e}"
        )


# ================= EXTRACT NAME =================
def extract_name(data):

    if isinstance(data, dict):

        return data.get("name")

    return str(data)


# ================= DOOR SEQUENCE =================
def door_sequence(name):

    safe_lcd(
        "ACCESS GRANTED",
        str(name),
        "Door Opening..."
    )

    # ================= SUCCESS BEEP =================
    success_beep()

    # ================= LOGGER =================
    logger.log_access(
        name,
        "SUCCESS",
        "DOOR_OPEN"
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
            [
                FACE_PY,
                "-m",
                "apps.face.face_app",
                "--no-relay"
            ],
            capture_output=True,
            text=True
        )

        output = (
            (result.stdout or "")
            + "\n"
            + (result.stderr or "")
        )

        output = output.strip()

        print("----- FACE OUTPUT -----")

        print(output)

        print("-----------------------")

        for line in output.splitlines():

            if "Akses:" in line:

                user = (
                    line
                    .split("Akses:")[-1]
                    .strip()
                )

                logger.log_face(
                    user,
                    status="SUCCESS"
                )

                return user

    except Exception as e:

        print("❌ Face error:", e)

        logger.log_error(
            f"FACE ERROR: {e}"
        )

    logger.log_face(
        "UNKNOWN",
        status="FAILED"
    )

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

            # ================= SCAN BEEP =================
            scan_beep()

            rfid_name = result["name"]

            print(f"✅ RFID valid: {rfid_name}")

            # ================= LOGGER =================
            logger.log_rfid(
                uid="UNKNOWN",
                user=rfid_name,
                status="SUCCESS"
            )

            safe_lcd(
                "RFID OK",
                str(rfid_name),
                ""
            )

            time.sleep(1)

            return rfid_name

        else:

            print(
                f"❌ RFID gagal "
                f"({attempt}/{MAX_ATTEMPT})"
            )

            logger.log_rfid(
                uid="UNKNOWN",
                status="FAILED"
            )

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

            # ================= RFID VERIFY =================
            rfid_name = rfid_verify()

            # ================= RFID SUCCESS =================
            if rfid_name:

                print(f"📡 RFID terbaca: {rfid_name}")

                if result in master_users:

                    if rfid_name == result:

                        print(
                            "🔐 MATCH: "
                            "Face & RFID sesuai"
                        )

                        logger.log_auth(
                            result,
                            "FACE+RFID",
                            "GRANTED"
                        )

                        door_sequence(result)

                        return True

                    else:

                        print(
                            "🚫 MISMATCH: "
                            "Face != RFID"
                        )

                        logger.log_auth(
                            result,
                            "FACE+RFID",
                            "MISMATCH"
                        )

                        # ================= WARNING BEEP =================
                        warning_beep()

                        safe_lcd(
                            "RFID MISMATCH",
                            "Use Finger",
                            ""
                        )

                        time.sleep(3)

                        return {
                            "status": "rfid_failed",
                            "user": result
                        }

                else:

                    print(
                        "🚫 User tidak ada "
                        "di master"
                    )

                    logger.log_auth(
                        result,
                        "FACE+RFID",
                        "UNKNOWN_USER"
                    )

                    # ================= ERROR BEEP =================
                    error_beep()

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

                logger.log_auth(
                    result,
                    "FACE+RFID",
                    "RFID_FAILED"
                )

                # ================= WARNING BEEP =================
                warning_beep()

                safe_lcd(
                    "RFID FAILED",
                    "Use Finger",
                    ""
                )

                time.sleep(3)

                return {
                    "status": "rfid_failed",
                    "user": result
                }

        # ================= FACE FAILED =================
        else:

            print(
                f"❌ Face gagal "
                f"({attempt}/{MAX_ATTEMPT})"
            )

            remaining = (
                MAX_ATTEMPT - attempt
            )

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

            # ================= SCAN BEEP =================
            scan_beep()

            print(
                f"🎉 Fingerprint dikenali: "
                f"{result}"
            )

            # ================= FIX =================
            if isinstance(result, dict):

                finger_name = result.get("name")
                finger_id = result.get("fid")

            else:

                finger_name = str(result)
                finger_id = "UNKNOWN"

            # ================= LOGGER =================
            logger.log_fingerprint(
                fid=finger_id,
                user=finger_name,
                status="SUCCESS"
            )

            # ================= CONTEXTUAL CHECK =================
            if expected_user:

                if finger_name != expected_user:

                    print(
                        "🚫 Fingerprint "
                        "bukan user yang sama"
                    )

                    logger.log_auth(
                        finger_name,
                        "FINGER+RFID",
                        "MISMATCH"
                    )

                    # ================= WARNING BEEP =================
                    warning_beep()

                    safe_lcd(
                        "INVALID USER",
                        "Fingerprint mismatch",
                        ""
                    )

                    time.sleep(2)

                    return False

            safe_lcd(
                "FINGER OK",
                str(finger_name),
                "Scan RFID..."
            )

            time.sleep(1)

            rfid_name = rfid_verify()

            if rfid_name:

                if rfid_name == finger_name:

                    print(
                        "🔐 MATCH: "
                        "Fingerprint & RFID sesuai"
                    )

                    logger.log_auth(
                        finger_name,
                        "FINGER+RFID",
                        "GRANTED"
                    )

                    door_sequence(
                        finger_name
                    )

                    return True

                else:

                    print(
                        "🚫 MISMATCH "
                        "Fingerprint & RFID"
                    )

                    logger.log_auth(
                        finger_name,
                        "FINGER+RFID",
                        "MISMATCH"
                    )

                    # ================= WARNING BEEP =================
                    warning_beep()

                    safe_lcd(
                        "ACCESS DENIED",
                        "Mismatch!",
                        ""
                    )

                    time.sleep(2)

                    return False

            else:

                print("❌ RFID gagal")

                logger.log_auth(
                    finger_name,
                    "FINGER+RFID",
                    "RFID_FAILED"
                )

                # ================= WARNING BEEP =================
                warning_beep()

                safe_lcd(
                    "RFID FAILED",
                    "",
                    ""
                )

                time.sleep(2)

                return False

        else:

            print(
                f"❌ Fingerprint gagal "
                f"({attempt}/{MAX_ATTEMPT})"
            )

            logger.log_fingerprint(
                fid="UNKNOWN",
                status="FAILED"
            )

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

    logger.log_system(
        "Unified authentication started"
    )

    safe_lcd(
        "SYSTEM READY",
        "",
        ""
    )

    time.sleep(2)

    # ================= FACE MODE =================
    face_result = mode_face()

    # ================= SUCCESS =================
    if face_result is True:

        return

    # ================= CONTEXTUAL FALLBACK =================
    if isinstance(face_result, dict):

        if (
            face_result["status"]
            == "rfid_failed"
        ):

            expected_user = (
                face_result["user"]
            )

            print(
                f"\n⚠️ Fallback fingerprint "
                f"untuk {expected_user}"
            )

            logger.log_system(
                f"Fallback fingerprint for {expected_user}"
            )

            # ================= WARNING BEEP =================
            warning_beep()

            safe_lcd(
                "USE FINGER",
                expected_user,
                "5 sec..."
            )

            # ================= COUNTDOWN =================
            for i in range(5, 0, -1):

                safe_lcd(
                    "USE FINGER",
                    expected_user,
                    f"{i} sec..."
                )

                time.sleep(1)

            # ================= CONTEXTUAL VERIFY =================
            if mode_fingerprint(expected_user):

                return

            # ================= FAILED =================
            print("\n⛔ AKSES DITOLAK")

            logger.log_auth(
                expected_user,
                "FINGER+RFID",
                "DENIED"
            )

            # ================= ERROR BEEP =================
            error_beep()

            safe_lcd(
                "ACCESS DENIED",
                "Fingerprint Failed",
                ""
            )

            time.sleep(2)

            return

    # ================= GLOBAL FALLBACK =================
    print("\n⚠️ Face gagal total")

    logger.log_system(
        "Face failed total, fallback fingerprint"
    )

    # ================= WARNING BEEP =================
    warning_beep()

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

    logger.log_auth(
        "UNKNOWN",
        "GLOBAL",
        "DENIED"
    )

    # ================= ERROR BEEP =================
    error_beep()

    safe_lcd(
        "ACCESS DENIED",
        "Try Again",
        ""
    )

    time.sleep(2)


# ================= ENTRY =================
if __name__ == "__main__":
    main()
