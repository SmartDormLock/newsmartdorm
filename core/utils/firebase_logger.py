import firebase_admin

from firebase_admin import (
    credentials,
    firestore
)

from datetime import datetime


# ================= INIT =================
cred = credentials.Certificate(
    "config/firebase/serviceAccountKey.json"
)

if not firebase_admin._apps:

    firebase_admin.initialize_app(cred)

db = firestore.client()


# ================= ACCESS LOG =================
def push_access_log(
    user_name,
    method,
    status,
    detail=""
):

    data = {

        "user_name": user_name,
        "method": method,
        "status": status,
        "detail": detail,
        "timestamp": datetime.utcnow()
    }

    db.collection(
        "access_logs"
    ).add(data)


# ================= SYSTEM LOG =================
def push_system_log(message):

    data = {

        "message": message,
        "timestamp": datetime.utcnow()
    }

    db.collection(
        "system_logs"
    ).add(data)


# ================= ERROR LOG =================
def push_error_log(message):

    data = {

        "message": message,
        "timestamp": datetime.utcnow()
    }

    db.collection(
        "error_logs"
    ).add(data)
    
# ================= DOOR STATUS =================
def update_door_status(

    building,
    room,
    status,
    user_name=""
):

    try:

        room_id = (
            f"{building}_{room}"
        )

        data = {

            "building": building,
            "room": room,

            "status": status,

            "last_user": user_name,

            "timestamp":
                datetime.utcnow()
        }

        db.collection(
            "door_status"
        ).document(
            room_id
        ).set(
            data,
            merge=True
        )

        print(

            "[FIREBASE] "
            f"Door status updated: "
            f"{room_id} -> {status}"
        )

    except Exception as e:

        print(
            f"[FIREBASE ERROR] {e}"
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

    db.collection(
        "auth_state"
    ).document(
        "current"
    ).set({

        "current_step": current_step,
        "status_text": status_text,

        "face_attempt": face_attempt,
        "fingerprint_attempt": fingerprint_attempt,
        "rfid_attempt": rfid_attempt,

        "access_granted": access_granted,
        "access_denied": access_denied,

        "timestamp":
            firestore.SERVER_TIMESTAMP

    }, merge=True)

# ================= ENROLLMENT LOG =================
def push_enrollment_log(

    user_name,
    step,
    status,
    detail=""
):

    data = {

        "user_name": user_name,
        "step": step,
        "status": status,
        "detail": detail,
        "timestamp": datetime.utcnow()
    }

    db.collection(
        "enrollment_logs"
    ).add(data)
