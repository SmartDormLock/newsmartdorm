import os
from datetime import datetime

import requests


# ================= BACKEND =================
BACKEND_URL = (
    "https://smart-dorm-backend-rose.vercel.app"
)


from core.utils.firebase_logger import (
    push_access_log,
    push_system_log,
    push_error_log,
    update_door_status as firebase_update_door_status,
    update_auth_state as firebase_update_auth_state
)


# ================= CONFIG =================
LOG_DIR = "logs"

ACCESS_LOG = os.path.join(
    LOG_DIR,
    "access.log"
)

SYSTEM_LOG = os.path.join(
    LOG_DIR,
    "system.log"
)

ERROR_LOG = os.path.join(
    LOG_DIR,
    "error.log"
)


# ================= INIT =================
os.makedirs(
    LOG_DIR,
    exist_ok=True
)


# ================= TIME =================
def get_timestamp():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ================= CORE WRITE =================
def write_log(
    log_file,
    level,
    message
):

    timestamp = get_timestamp()

    log_line = (
        f"[{timestamp}] "
        f"[{level}] "
        f"{message}\n"
    )

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(log_line)


# ================= SEND TO BACKEND =================
def send_to_backend(
    user_name,
    method,
    status,
    detail=""
):

    try:

        response = requests.post(

            f"{BACKEND_URL}/api/device/access",

            json={

                "user_name": user_name,
                "method": method,
                "status": status,
                "detail": detail
            },

            timeout=10
        )

        print(
            "[BACKEND SUCCESS]",
            response.json()
        )

    except Exception as e:

        print(
            f"[BACKEND FAILED] {e}"
        )


# ================= SYSTEM =================
def log_system(message):

    write_log(
        SYSTEM_LOG,
        "SYSTEM",
        message
    )

    # ================= FIREBASE =================
    try:

        push_system_log(message)

    except Exception as e:

        print(
            f"⚠️ Firebase system log error: {e}"
        )


# ================= ERROR =================
def log_error(message):

    write_log(
        ERROR_LOG,
        "ERROR",
        message
    )

    # ================= FIREBASE =================
    try:

        push_error_log(message)

    except Exception as e:

        print(
            f"⚠️ Firebase error log error: {e}"
        )


# ================= FACE =================
def log_face(
    user,
    status="SUCCESS",
    confidence=None
):

    message = (
        f"USER={user} | "
        f"STATUS={status}"
    )

    if confidence is not None:

        message += (
            f" | CONFIDENCE={confidence}"
        )

    write_log(
        ACCESS_LOG,
        "FACE",
        message
    )


# ================= RFID =================
def log_rfid(
    uid,
    user=None,
    status="SUCCESS"
):

    message = (
        f"UID={uid} | "
        f"STATUS={status}"
    )

    if user:

        message += (
            f" | USER={user}"
        )

    write_log(
        ACCESS_LOG,
        "RFID",
        message
    )


# ================= FINGERPRINT =================
def log_fingerprint(
    fid,
    user=None,
    confidence=None,
    status="SUCCESS"
):

    message = (
        f"FID={fid} | "
        f"STATUS={status}"
    )

    if user:

        message += (
            f" | USER={user}"
        )

    if confidence is not None:

        message += (
            f" | CONFIDENCE={confidence}"
        )

    write_log(
        ACCESS_LOG,
        "FINGERPRINT",
        message
    )


# ================= AUTH =================
def log_auth(
    user,
    method,
    result,
    detail=""
):

    message = (
        f"USER={user} | "
        f"METHOD={method} | "
        f"RESULT={result}"
    )

    if detail:

        message += (
            f" | DETAIL={detail}"
        )

    write_log(
        ACCESS_LOG,
        "AUTH",
        message
    )

    # ================= FIREBASE =================
    try:

        push_access_log(
            user,
            method,
            result,
            detail
        )

    except Exception as e:

        print(
            f"⚠️ Firebase auth log error: {e}"
        )

    # ================= BACKEND =================
    send_to_backend(
        user_name=user,
        method=method,
        status=result,
        detail=detail
    )


# ================= ACCESS =================
def log_access(
    user,
    status,
    method
):

    message = (
        f"USER={user} | "
        f"STATUS={status} | "
        f"METHOD={method}"
    )

    write_log(
        ACCESS_LOG,
        "ACCESS",
        message
    )

# ================= DOOR STATUS =================
def update_door_status(status):

    try:

        print(
            f"[DOOR STATUS] {status}"
        )

        firebase_update_door_status(
            status
        )

        print(
            "[DOOR STATUS SUCCESS]"
        )

    except Exception as e:

        print(
            f"?? Firebase door status error: {e}"
        )

# ================= AUTH STATE =================
def update_auth_state(

    current_step,
    status_text,

    face_attempt=0,
    fingerprint_attempt=0,
    rfid_attempt=0,

    access_granted=False,
    access_denied=False
):

    try:

        firebase_update_auth_state(

            current_step,
            status_text,

            face_attempt,
            fingerprint_attempt,
            rfid_attempt,

            access_granted,
            access_denied
        )

    except Exception as e:

        print(
            f"?? Auth state error: {e}"
        )

# ================= TEST =================
if __name__ == "__main__":

    print("\n🧪 Testing logger...\n")

    log_system(
        "SmartDormLock started"
    )

    log_face(
        "Naufal",
        confidence=0.82
    )

    log_rfid(
        "16159127116",
        user="Naufal"
    )

    log_fingerprint(
        1,
        user="Naufal",
        confidence=342
    )

    log_auth(
        "Naufal",
        "FACE+RFID",
        "GRANTED"
    )

    log_access(
        "Naufal",
        "SUCCESS",
        "MULTI_FACTOR"
    )

    log_error(
        "Camera disconnected"
    )

    print("✅ Logger test selesai\n")
