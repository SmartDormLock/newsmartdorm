import time

from core.hardware.ultrasonic import (
    get_distance
)

from core.hardware.relay import (
    open_door
)

from core.hardware.buzzer import (
    success_beep
)

from core.hardware.lcd import (
    lcd_write
)

from core.utils.firebase_logger import (

    push_access_log,

    update_door_status,

    db
)

from config.device_id import (

    BUILDING_ID,
    ROOM_ID
)

# =========================
# SYSTEM STATE
# =========================

import core.system.system_state as system_state


# ================= CONFIG =================
DETECTION_DISTANCE = 15
COOLDOWN = 5


# ================= GET ROOM OWNER =================
def get_room_owner():

    try:

        users_ref = db.collection(
            "users"
        )

        query = users_ref.where(
            "building",
            "==",
            BUILDING_ID
        ).where(
            "room",
            "==",
            ROOM_ID
        ).limit(1)

        docs = query.stream()

        for doc in docs:

            data = doc.to_dict()

            return {

                "uid": data.get(
                    "uid",
                    ""
                ),

                "name": data.get(
                    "name",
                    "Unknown"
                )
            }

        return {

            "uid": "",

            "name": "Unknown"
        }

    except Exception as e:

        print(
            f"[EXIT USER ERROR] {e}"
        )

        return {

            "uid": "",

            "name": "Unknown"
        }


# ================= LOOP =================
def inside_exit_loop():

    print("Inside Exit Thread Started")

    last_open = 0

    while True:

        try:

            # ================= PAUSE IF AUTH RUNNING =================
            if system_state.AUTH_RUNNING:

                time.sleep(1)
                continue

            # ================= PAUSE IF ENROLL RUNNING =================
            if system_state.ENROLL_RUNNING:

                time.sleep(1)
                continue

            # ================= PAUSE IF DOOR BUSY =================
            if system_state.DOOR_BUSY:

                time.sleep(1)
                continue

            # ================= PAUSE IF EXIT DISABLED =================
            if not system_state.EXIT_ENABLED:

                time.sleep(1)
                continue

            # ================= READ SENSOR =================
            distance = get_distance()

            # ================= INVALID =================
            if distance is None:

                time.sleep(1)
                continue

            print(
                f"[EXIT] {distance} cm"
            )

            # ================= DETECT =================
            if distance < DETECTION_DISTANCE:

                now = time.time()

                # ================= COOLDOWN =================
                if (
                    now - last_open
                    > COOLDOWN
                ):

                    print(
                        "INSIDE EXIT DETECTED"
                    )

                    # ================= GET USER =================
                    owner_data = get_room_owner()

                    user_uid = owner_data["uid"]

                    user_name = owner_data["name"]

                    print(
                        f"[EXIT USER] {user_name}"
                    )

                    # ================= ACCESS LOG =================
                    try:

                        push_access_log(

                            uid=user_uid,

                            user_name=user_name,

                            method="Inside Exit",

                            status="GRANTED",

                            detail=(
                                "Exit detected "
                                "using ultrasonic sensor"
                            )
                        )

                        print(
                            "[EXIT LOG] Access log saved"
                        )

                    except Exception as log_error:

                        print(
                            f"[EXIT LOG ERROR] {log_error}"
                        )

                    # ================= UPDATE DOOR STATUS =================
                    try:

                        update_door_status(

                            BUILDING_ID,

                            ROOM_ID,

                            "OPEN",

                            user_name
                        )

                    except Exception as status_error:

                        print(
                            f"[DOOR STATUS ERROR] {status_error}"
                        )

                    # ================= LCD =================
                    try:

                        lcd_write(

                            "EXIT DETECTED",

                            f"Goodbye {user_name}",

                            ""
                        )

                    except Exception as lcd_error:

                        print(
                            f"[LCD ERROR] {lcd_error}"
                        )

                    # ================= BEEP =================
                    try:

                        success_beep()

                    except Exception as beep_error:

                        print(
                            f"[BUZZER ERROR] {beep_error}"
                        )

                    # ================= OPEN DOOR =================
                    open_door()

                    # ================= LOCK STATUS =================
                    try:

                        update_door_status(

                            BUILDING_ID,

                            ROOM_ID,

                            "LOCKED",

                            user_name
                        )

                    except Exception as status_error:

                        print(
                            f"[DOOR STATUS ERROR] {status_error}"
                        )

                    last_open = now

                    # ================= LCD RESET =================
                    time.sleep(1)

                    try:

                        lcd_write(

                            "SYSTEM READY",

                            "",

                            ""
                        )

                    except Exception as lcd_error:

                        print(
                            f"[LCD ERROR] {lcd_error}"
                        )

            # ================= LOOP DELAY =================
            time.sleep(1)

        except Exception as e:

            print(
                f"[EXIT ERROR] {e}"
            )

            # ================= LCD ERROR =================
            try:

                lcd_write(

                    "EXIT ERROR",

                    "Check Sensor",

                    ""
                )

            except:

                pass

            time.sleep(2)
