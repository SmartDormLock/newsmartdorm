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
