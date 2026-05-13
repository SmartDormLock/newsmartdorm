import subprocess
import time

from core.auth.fingerprint_auth import scan_fingerprint
from core.auth.rfid_auth import scan_rfid
from core.auth.master_user import load_master_users

from core.hardware.relay import open_door
from core.hardware.lcd import lcd_write

from core.hardware.buzzer import (
    success_beep,
    error_beep,
    warning_beep,
    scan_beep
)

import core.utils.logger as logger
from core.utils.door_listener import start_door_listener


# ================= CONFIG =================
MAX_ATTEMPT = 3

FACE_PY = (
    "/home/raspi5/newsmartdorm/"
    "envs/face_env/bin/python"
)


# ================= SAFE LCD =================
def safe_lcd(*args):

    try:

        lcd_write(*args)

    except Exception as e:

        print(f"⚠️ LCD ERROR: {e}")

        logger.log_error(
            f"LCD ERROR: {e}"
        )


# ================= NOTIFY =================
def notify(
    beep_type,
    line1,
    line2="",
    line3="",
    delay=2
):

    if beep_type == "success":

        success_beep()

    elif beep_type == "warning":

        warning_beep()

    elif beep_type == "error":

        error_beep()

    elif beep_type == "scan":

        scan_beep()

    safe_lcd(
        line1,
        line2,
        line3
    )

    time.sleep(delay)


# ================= AUTH STATE =================
def update_state(
    step,
    text,

    face=0,
    finger=0,
    rfid=0,

    granted=False,
    denied=False
):

    try:

        logger.update_auth_state(

            step,
            text,

            face,
            finger,
            rfid,

            granted,
            denied
        )

    except Exception as e:

        print(f"⚠️ Auth state error: {e}")


# ================= NORMALIZE USER =================
def normalize_user(data):

    if isinstance(data, dict):

        return (
            data.get("name"),
            data.get("fid", "UNKNOWN")
        )

    return str(data), "UNKNOWN"


# ================= OPEN DOOR =================
def door_sequence(name):

    notify(
        "success",
        "ACCESS GRANTED",
        str(name),
        "Door Opening...",
        delay=1
    )

    logger.log_access(
        name,
        "SUCCESS",
        "DOOR_OPEN"
    )

    logger.update_door_status(
        "OPEN"
    )

    open_door()

    time.sleep(3)

    logger.update_door_status(
        "LOCKED"
    )

    notify(
        None,
        "DOOR LOCKED",
        "",
        "Ready...",
        delay=2
    )

    safe_lcd(
        "SYSTEM READY",
        "",
        ""
    )


# ================= FACE SCAN =================
def scan_face(attempt):

    print("\n📷 Face Recognition...")

    update_state(

        "Face Recognition",
        "Scanning wajah...",

        face=attempt
    )

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

        print(f"❌ FACE ERROR: {e}")

        logger.log_error(
            f"FACE ERROR: {e}"
        )

    logger.log_face(
        "UNKNOWN",
        status="FAILED"
    )

    return None


# ================= RFID VERIFY =================
def verify_rfid():

    print("\n📡 RFID Verification...")

    for attempt in range(1, MAX_ATTEMPT + 1):

        update_state(

            "RFID Verification",
            "Tempelkan kartu RFID",

            face=-1,
            rfid=attempt
        )

        safe_lcd(
            "SCAN RFID",
            "Tempel kartu",
            f"{attempt}/{MAX_ATTEMPT}"
        )

        result = scan_rfid()

        if result:

            notify(
                "scan",
                "RFID OK",
                result["name"],
                "",
                delay=1
            )

            logger.log_rfid(
                uid="UNKNOWN",
                user=result["name"],
                status="SUCCESS"
            )

            return result["name"]

        logger.log_rfid(
            uid="UNKNOWN",
            status="FAILED"
        )

        notify(
            None,
            "RFID FAILED",
            "",
            f"{attempt}/{MAX_ATTEMPT}",
            delay=1
        )

    return None


# ================= AUTH SUCCESS =================
def auth_success(user, method):

    print(f"🔐 AUTH SUCCESS: {user}")

    logger.log_auth(
        user,
        method,
        "GRANTED"
    )

    update_state(

        "Authentication Complete",
        "Akses diterima",

        granted=True
    )

    door_sequence(user)

    return True


# ================= AUTH FAILED =================
def auth_failed(
    user,
    method,
    status,

    lcd1,
    lcd2="",

    beep="warning",
    delay=2
):

    logger.log_auth(
        user,
        method,
        status
    )

    notify(
        beep,
        lcd1,
        lcd2,
        "",
        delay=delay
    )

    return False


# ================= FACE MODE =================
def mode_face():

    print("\n=== FACE + RFID ===")

    master_users = load_master_users()

    for attempt in range(1, MAX_ATTEMPT + 1):

        face_user = scan_face(attempt)

        if not face_user:

            notify(
                None,
                "FACE FAILED",
                f"Sisa: {MAX_ATTEMPT - attempt}",
                "Retry...",
                delay=2
            )

            continue

        print(f"✅ FACE: {face_user}")

        safe_lcd(
            "FACE OK",
            f"Hello {face_user}",
            "Scan RFID..."
        )

        time.sleep(1)

        rfid_user = verify_rfid()

        # ================= RFID FAILED =================
        if not rfid_user:

            logger.log_auth(
                face_user,
                "FACE+RFID",
                "RFID_FAILED"
            )

            notify(
                "warning",
                "RFID FAILED",
                "Use Finger",
                "",
                delay=3
            )

            return {
                "status": "rfid_failed",
                "user": face_user
            }

        # ================= UNKNOWN USER =================
        if face_user not in master_users:

            return auth_failed(

                face_user,
                "FACE+RFID",
                "UNKNOWN_USER",

                "UNKNOWN USER",

                beep="error"
            )

        # ================= MATCH =================
        if rfid_user == face_user:

            return auth_success(
                face_user,
                "FACE+RFID"
            )

        # ================= MISMATCH =================
        logger.log_auth(
            face_user,
            "FACE+RFID",
            "MISMATCH"
        )

        notify(
            "warning",
            "RFID MISMATCH",
            "Use Finger",
            "",
            delay=3
        )

        return {
            "status": "rfid_failed",
            "user": face_user
        }

    return False


# ================= FINGER MODE =================
def mode_fingerprint(expected_user=None):

    print("\n=== FINGERPRINT + RFID ===")

    logger.log_system(
        "Fingerprint mode started"
    )

    for attempt in range(1, MAX_ATTEMPT + 1):

        update_state(

            "Fingerprint Authentication",
            "Scanning fingerprint...",

            finger=attempt
        )

        safe_lcd(
            "MODE: FINGER",
            "Scan Finger",
            f"{attempt}/{MAX_ATTEMPT}"
        )

        try:

            result = scan_fingerprint()

        except Exception as e:

            print(f"❌ FINGER ERROR: {e}")

            logger.log_error(
                f"FINGERPRINT SENSOR ERROR: {e}"
            )

            logger.log_fingerprint(
                fid="UNKNOWN",
                status="SENSOR_ERROR"
            )

            return auth_failed(

                "UNKNOWN",
                "FINGERPRINT",
                "SENSOR_ERROR",

                "FINGER ERROR",
                "Sensor Failed",

                beep="error"
            )

        # ================= FAILED =================
        if not result:

            logger.log_fingerprint(
                fid="UNKNOWN",
                status="FAILED"
            )

            notify(
                None,
                "FINGER FAILED",
                "",
                f"{attempt}/{MAX_ATTEMPT}",
                delay=1
            )

            continue

        # ================= SUCCESS =================
        notify(
            "scan",
            "FINGER OK",
            "",
            "",
            delay=1
        )

        finger_name, finger_id = (
            normalize_user(result)
        )

        logger.log_fingerprint(
            fid=finger_id,
            user=finger_name,
            status="SUCCESS"
        )

        # ================= CONTEXT CHECK =================
        if (
            expected_user
            and finger_name != expected_user
        ):

            return auth_failed(

                finger_name,
                "FINGER+RFID",
                "MISMATCH",

                "INVALID USER",
                "Fingerprint mismatch"
            )

        safe_lcd(
            "FINGER OK",
            finger_name,
            "Scan RFID..."
        )

        time.sleep(1)

        rfid_user = verify_rfid()

        # ================= RFID FAILED =================
        if not rfid_user:

            return auth_failed(

                finger_name,
                "FINGER+RFID",
                "RFID_FAILED",

                "RFID FAILED"
            )

        # ================= MATCH =================
        if rfid_user == finger_name:

            return auth_success(
                finger_name,
                "FINGER+RFID"
            )

        # ================= MISMATCH =================
        return auth_failed(

            finger_name,
            "FINGER+RFID",
            "MISMATCH",

            "ACCESS DENIED",
            "Mismatch!"
        )

    logger.log_auth(
        "UNKNOWN",
        "FINGERPRINT",
        "DENIED"
    )

    return False


# ================= MAIN =================
def main():

    print("\n🔐 SMART DOOR SYSTEM STARTED")
    
    start_door_listener()

    logger.log_system(
        "Unified authentication started"
    )

    safe_lcd(
        "SYSTEM READY",
        "",
        ""
    )

    update_state(

        "Face Recognition",
        "Menunggu scan wajah dari perangkat"
    )

    time.sleep(2)

    # ================= FACE FLOW =================
    face_result = mode_face()

    if face_result is True:

        return

    # ================= CONTEXTUAL FALLBACK =================
    if (
        isinstance(face_result, dict)
        and face_result["status"] == "rfid_failed"
    ):

        expected_user = (
            face_result["user"]
        )

        logger.log_system(
            f"Fallback fingerprint for {expected_user}"
        )

        notify(
            "warning",
            "USE FINGER",
            expected_user,
            "5 sec...",
            delay=1
        )

        for i in range(5, 0, -1):

            safe_lcd(
                "USE FINGER",
                expected_user,
                f"{i} sec..."
            )

            time.sleep(1)

        if mode_fingerprint(expected_user):

            return

        auth_failed(

            expected_user,
            "FINGER+RFID",
            "DENIED",

            "ACCESS DENIED",
            "Fingerprint Failed",

            beep="error"
        )

        return

    # ================= GLOBAL FALLBACK =================
    logger.log_system(
        "Face failed total, fallback fingerprint"
    )

    notify(
        "warning",
        "FACE UNKNOWN",
        "Use Fingerprint",
        "",
        delay=3
    )

    if mode_fingerprint():

        return

    # ================= TOTAL FAILED =================
    logger.log_auth(
        "UNKNOWN",
        "GLOBAL",
        "DENIED"
    )

    update_state(

        "Authentication Failed",
        "Akses ditolak",

        denied=True
    )

    notify(
        "error",
        "ACCESS DENIED",
        "Try Again",
        "",
        delay=2
    )


# ================= ENTRY =================
if __name__ == "__main__":

    main()
