import time

from core.utils.firebase_logger import db

from apps.admin.revisi_enroll_user import (
    auto_enroll
)

print(
    "\n?? Enrollment Listener Started"
)

# ============================================
# FIRESTORE REFERENCE
# ============================================

trigger_ref = db.collection(
    "system_control"
).document(
    "enrollment_trigger"
)

# ============================================
# STATE
# ============================================

last_state = False

is_running = False

# ============================================
# MAIN LOOP
# ============================================

while True:

    try:

        doc = trigger_ref.get()

        if doc.exists:

            data = doc.to_dict()

            start_enrollment = data.get(
                "start_enrollment",
                False
            )

            # ====================================
            # NEW ENROLLMENT TRIGGER
            # ====================================

            if (
                start_enrollment is True
                and last_state is False
                and is_running is False
            ):

                is_running = True

                print(
                    "\n?? Enrollment Triggered"
                )

                # ====================================
                # GET USER DATA
                # ====================================

                user_uid = data.get(
                    "uid"
                )

                user_name = data.get(
                    "name"
                )

                print(
                    f"\n?? USER : {user_name}"
                )

                # ====================================
                # UPDATE STATUS
                # ====================================

                trigger_ref.set({

                    "status":
                        "processing"

                }, merge=True)

                # ====================================
                # RUN AUTO ENROLL
                # ====================================

                auto_enroll(
                    user_name
                )

                # ====================================
                # ACTIVATE USER
                # ====================================

                db.collection(
                    "users"
                ).document(
                    user_uid
                ).update({

                    "is_active":
                        True

                })

                # ====================================
                # RESET TRIGGER
                # ====================================

                trigger_ref.set({

                    "start_enrollment":
                        False,

                    "status":
                        "success"

                }, merge=True)

                print(
                    "\n?? Enrollment Success"
                )

                is_running = False

            last_state = start_enrollment

        time.sleep(1)

    except Exception as e:

        print(
            f"\n? Enrollment Listener Error: {e}"
        )

        trigger_ref.set({

            "status":
                "failed",

            "error":
                str(e)

        }, merge=True)

        is_running = False

        time.sleep(2)
