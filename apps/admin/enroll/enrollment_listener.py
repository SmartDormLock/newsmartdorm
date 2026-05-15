import sys
sys.stdout.reconfigure(encoding="utf-8")

import time

from core.utils.firebase_logger import db

import core.utils.logger as logger

from apps.admin.enroll.revisi_enroll_user import (
    auto_enroll
)

print(
    "\n🚀 Enrollment Listener Started"
)

logger.log_system(
    "Enrollment listener started"
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
                    "\n🚀 Enrollment Triggered"
                )

                logger.log_system(
                    "Enrollment triggered"
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
                    f"\n👤 USER : {user_name}"
                )

                # ====================================
                # VALIDATION
                # ====================================

                if not user_uid or not user_name:

                    raise Exception(
                        "UID atau nama user kosong"
                    )

                # ====================================
                # UPDATE STATUS
                # ====================================

                trigger_ref.set({

                    "status":
                        "processing",

                    "error":
                        "",

                    "updated_at":
                        time.time()

                }, merge=True)

                logger.log_system(
                    f"Enrollment processing for {user_name}"
                )

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

                logger.log_system(
                    f"User activated: {user_name}"
                )

                # ====================================
                # RESET TRIGGER
                # ====================================

                trigger_ref.set({

                    "start_enrollment":
                        False,

                    "status":
                        "success",

                    "error":
                        "",

                    "updated_at":
                        time.time()

                }, merge=True)

                print(
                    "\n✅ Enrollment Success"
                )

                logger.log_system(
                    f"Enrollment success: {user_name}"
                )

                is_running = False

                # ====================================
                # CLOSE PROGRAM
                # ====================================

                print(
                    "\n🛑 Closing enrollment listener..."
                )

                logger.log_system(
                    "Enrollment listener closed"
                )

                sys.exit(0)

            last_state = start_enrollment

        time.sleep(1)

    except Exception as e:

        print(
            f"\n❌ Enrollment Listener Error: {e}"
        )

        logger.log_error(
            f"Enrollment listener error: {e}"
        )

        try:

            trigger_ref.set({

                "status":
                    "failed",

                "error":
                    str(e),

                "updated_at":
                    time.time()

            }, merge=True)

        except Exception as firebase_error:

            print(
                f"\n❌ Firebase update failed: {firebase_error}"
            )

        is_running = False

        time.sleep(2)
