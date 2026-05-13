import time
import threading

from config.firebase.firebase_config import db

# ============================================
# DOOR RELAY CONTROL
# ============================================

# TODO:
# Ganti dengan relay GPIO asli nanti

def unlock_door():

    print("\n================================")
    print("EMERGENCY UNLOCK ACTIVATED")
    print("DOOR OPEN")
    print("================================\n")

    # SIMULASI RELAY ON
    time.sleep(5)

    print("\n================================")
    print("DOOR LOCKED AGAIN")
    print("================================\n")


# ============================================
# FIRESTORE LISTENER
# ============================================

def on_snapshot(doc_snapshot,
                changes,
                read_time):

    for doc in doc_snapshot:

        data = doc.to_dict()

        emergency_unlock = data.get(
            "emergency_unlock",
            False,
        )

        # ====================================
        # EMERGENCY UNLOCK
        # ====================================

        if emergency_unlock:

            print(
                "\n[DOOR LISTENER] Emergency unlock received"
            )

            # UPDATE STATUS
            db.collection(
                "door_status"
            ).document(
                "current"
            ).set({

                "status": "UNLOCKED",

                "timestamp":
                    time.time(),

            })

            # UNLOCK DOOR
            unlock_door()

            # LOCK AGAIN
            db.collection(
                "door_status"
            ).document(
                "current"
            ).set({

                "status": "LOCKED",

                "timestamp":
                    time.time(),

            })

            # RESET FIREBASE FLAG
            db.collection(
                "system_control"
            ).document(
                "main_door"
            ).update({

                "emergency_unlock":
                    False,

            })

            print(
                "[DOOR LISTENER] Reset complete"
            )


# ============================================
# START LISTENER
# ============================================

def start_door_listener():

    print(
        "\n[DOOR LISTENER] Starting..."
    )

    # ========================================
    # INIT DOCUMENT IF NOT EXISTS
    # ========================================

    doc_ref = db.collection(
        "system_control"
    ).document(
        "main_door"
    )

    doc = doc_ref.get()

    if not doc.exists:

        doc_ref.set({

            "emergency_unlock":
                False,

        })

        print(
            "[DOOR LISTENER] Firestore initialized"
        )

    # ========================================
    # START REALTIME LISTENER
    # ========================================

    doc_watch = doc_ref.on_snapshot(
        on_snapshot
    )

    print(
        "[DOOR LISTENER] Listening realtime..."
    )

    return doc_watch
