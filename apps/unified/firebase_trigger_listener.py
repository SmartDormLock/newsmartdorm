import time

from google.cloud.firestore import DocumentSnapshot

from core.utils.firebase_logger import db

from apps.unified.revisi_unified_app import main


print(
    "\n?? Firebase Trigger Listener Started"
)

trigger_ref = db.collection(
    "system_control"
).document(
    "auth_trigger"
)

last_state = False

is_running = False

while True:

    try:

        doc = trigger_ref.get()

        if doc.exists:

            data = doc.to_dict()

            start_auth = data.get(
                "start_auth",
                False
            )

            # ================= NEW TRIGGER =================

            if (
                start_auth is True
                and last_state is False
                and is_running is False
            ):

                is_running = True

                print(
                    "\n?? Authentication Triggered"
                )

                # ================= RUN AUTH =================

                main()

                # ================= RESET =================

                trigger_ref.set({

                    "start_auth": False

                }, merge=True)

                is_running = False

            last_state = start_auth

        time.sleep(1)

    except Exception as e:

        print(
            f"? Listener Error: {e}"
        )

        time.sleep(2)
