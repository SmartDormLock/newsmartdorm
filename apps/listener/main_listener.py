import sys
sys.stdout.reconfigure(encoding="utf-8")

import time

from core.utils.firebase_logger import db

import core.utils.logger as logger

# =========================
# AUTH
# =========================

from apps.unified.revisi_unified_app import (
    main as auth_main
)

# =========================
# ENROLL
# =========================

from apps.admin.enroll.revisi_enroll_user import (
    auto_enroll
)

print("\n🚀 SmartDorm Main Listener Started")

logger.log_system(
    "Main listener started"
)

# ====================================
# FIRESTORE REFERENCES
# ====================================

auth_ref = db.collection(
    "system_control"
).document(
    "auth_trigger"
)

enroll_ref = db.collection(
    "system_control"
).document(
    "enrollment_trigger"
)

# ====================================
# STATE
# ====================================

is_running = False

# ====================================
# MAIN LOOP
# ====================================

while True:

    try:

        # ====================================
        # JANGAN JALANKAN DUA PROCESS
        # ====================================

        if is_running:

            time.sleep(1)
            continue

        # ====================================
        # AUTH TRIGGER
        # ====================================

        auth_doc = auth_ref.get()

        if auth_doc.exists:

            auth_data = auth_doc.to_dict()

            start_auth = auth_data.get(
                "start_auth",
                False
            )

            if start_auth:

                is_running = True

                print(
                    "\n🔐 AUTH STARTED"
                )

                logger.log_system(
                    "Authentication started"
                )

                try:

                    # =========================
                    # RUN AUTH
                    # =========================

                    auth_main()

                    # =========================
                    # RESET FIREBASE
                    # =========================

                    auth_ref.set({

                        "start_auth": False

                    }, merge=True)

                    print(
                        "\n✅ AUTH SUCCESS"
                    )

                    logger.log_system(
                        "Authentication success"
                    )

                except Exception as e:

                    print(
                        f"\n❌ AUTH ERROR: {e}"
                    )

                    logger.log_error(
                        f"Auth error: {e}"
                    )

                is_running = False

        # ====================================
        # ENROLLMENT TRIGGER
        # ====================================

        enroll_doc = enroll_ref.get()

        if enroll_doc.exists:

            enroll_data = enroll_doc.to_dict()

            start_enrollment = enroll_data.get(
                "start_enrollment",
                False
            )

            if start_enrollment:

                is_running = True

                print(
                    "\n📝 ENROLLMENT STARTED"
                )

                logger.log_system(
                    "Enrollment started"
                )

                try:

                    # =========================
                    # GET USER DATA
                    # =========================

                    user_uid = enroll_data.get(
                        "uid"
                    )

                    user_name = enroll_data.get(
                        "name"
                    )

                    if not user_uid or not user_name:

                        raise Exception(
                            "UID atau nama kosong"
                        )

                    # =========================
                    # STATUS PROCESSING
                    # =========================

                    enroll_ref.set({

                        "status": "processing"

                    }, merge=True)

                    # =========================
                    # RUN ENROLL
                    # =========================

                    auto_enroll(
                        user_name
                    )

                    # =========================
                    # ACTIVATE USER
                    # =========================

                    db.collection(
                        "users"
                    ).document(
                        user_uid
                    ).update({

                        "is_active": True

                    })

                    # =========================
                    # RESET FIREBASE
                    # =========================

                    enroll_ref.set({

                        "start_enrollment": False,
                        "status": "success"

                    }, merge=True)

                    print(
                        "\n✅ ENROLL SUCCESS"
                    )

                    logger.log_system(
                        f"Enrollment success: {user_name}"
                    )

                except Exception as e:

                    print(
                        f"\n❌ ENROLL ERROR: {e}"
                    )

                    logger.log_error(
                        f"Enroll error: {e}"
                    )

                    enroll_ref.set({

                        "status": "failed",
                        "error": str(e)

                    }, merge=True)

                is_running = False

        time.sleep(1)

    except Exception as e:

        print(
            f"\n❌ MAIN LOOP ERROR: {e}"
        )

        logger.log_error(
            f"Main listener error: {e}"
        )

        time.sleep(2)
