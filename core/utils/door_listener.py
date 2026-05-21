import time
import core.system.system_state as system_state

from core.utils.firebase_logger import db
from core.hardware.relay import (
    open_door
)

# ============================================
# STATE
# ============================================

is_unlocking = False

# ============================================
# FIRESTORE LISTENER
# ============================================

def on_snapshot(
    doc_snapshot,
    changes,
    read_time
):

    global is_unlocking

    for doc in doc_snapshot:

        data = doc.to_dict()

        emergency_unlock = data.get(
            "emergency_unlock",
            False,
        )

        # ====================================
        # EMERGENCY UNLOCK
        # ====================================

        if (
            emergency_unlock is True
            and not is_unlocking
        ):

            is_unlocking = True

            print(
                "\n[DOOR LISTENER] Emergency unlock received"
            )

            # ====================================
            # UPDATE STATUS
            # ====================================

            db.collection(
                "door_status"
            ).document(
                "current"
            ).set({

                "status":
                    "UNLOCKED",

                "timestamp":
                    time.time(),

            })

            # ====================================
            # OPEN DOOR
            # ====================================

            open_door()

            # ====================================
            # LOCK AGAIN
            # ====================================

            db.collection(
                "door_status"
            ).document(
                "current"
            ).set({

                "status":
                    "LOCKED",

                "timestamp":
                    time.time(),

            })

            # ====================================
            # RESET FIREBASE FLAG
            # ====================================

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

            is_unlocking = False


# ============================================
# START LISTENER
# ============================================

def start_door_listener():

    print(
        "\n[DOOR LISTENER] Starting..."
    )

    # ========================================
    # FIRESTORE REFERENCE
    # ========================================

    doc_ref = db.collection(
        "system_control"
    ).document(
        "main_door"
    )

    # ========================================
    # INIT DOCUMENT
    # ========================================

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
    # INIT DOOR STATUS
    # ========================================

    status_ref = db.collection(
        "door_status"
    ).document(
        "current"
    )

    status_doc = status_ref.get()

    if not status_doc.exists:

        status_ref.set({

            "status":
                "LOCKED",

            "timestamp":
                time.time(),

        })

    # ========================================
    # START REALTIME LISTENER
    # ========================================

    doc_ref.on_snapshot(
        on_snapshot
    )

    print(
        "[DOOR LISTENER] Listening realtime..."
    )
