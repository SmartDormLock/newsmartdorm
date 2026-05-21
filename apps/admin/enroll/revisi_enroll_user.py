import sys
import os
import time
import subprocess
import adafruit_fingerprint
import core.utils.logger as logger
sys.stdout.reconfigure(encoding="utf-8")

from core.auth.rfid_auth import (
    scan_new_rfid,
    load_cards,
    save_cards
)

from core.auth.fingerprint_auth import (
    load_users
)

from core.auth.master_user import (
    add_master_user
)

from core.hardware.fingerprint import (
    FingerprintSensor
)

from core.system.system_state import (

    start_enroll,
    stop_enroll
)

# ================= FACE ENV =================
FACE_PY = (
    "/home/raspi5/newsmartdorm/"
    "envs/face_env/bin/python"
)

FACE_DATASET_MODULE = "apps.face.dataset_app"

FACE_TRAIN_MODULE = "apps.face.train_app"


# ================= PATH =================
FINGERPRINT_FILE = (
    "data/fingerprint/users.txt"
)


# ================= CONNECT SENSOR =================
def connect_fingerprint(max_retry=5):

    for i in range(max_retry):

        try:

            print(
                f"🔌 Connecting fingerprint "
                f"({i + 1}/{max_retry})..."
            )

            sensor = FingerprintSensor()

            return sensor

        except Exception as e:

            print(f"⚠️ Connection failed : {e}")

            logger.log_error(
                f"Fingerprint connect failed: {e}"
            )

            time.sleep(2)

    print("\n❌ Fingerprint sensor gagal connect")

    return None


# ================= SAVE RFID =================
def save_rfid_user(uid, name):

    cards = load_cards()

    # ================= DUPLICATE CHECK =================
    if uid in cards:

        print("\n❌ RFID already used")
        print(f"UID : {uid}")
        print(f"User : {cards[uid]}")

        return False

    cards[uid] = name

    save_cards(cards)

    print("✅ RFID saved")

    return True


# ================= SAVE FINGERPRINT =================
def save_fingerprint_user(fid, name):

    users = load_users()

    # ================= DUPLICATE FID =================
    if fid in users:

        print("\n❌ Finger ID already used")
        print(f"Slot : {fid}")
        print(f"User : {users[fid]}")

        return False

    # ================= DUPLICATE USER =================
    if name in users.values():

        print("\n❌ User already has fingerprint")

        return False

    users[fid] = name

    with open(FINGERPRINT_FILE, "w") as f:

        for user_id, username in users.items():

            f.write(
                f"{user_id},"
                f"{username}\n"
            )

    print("✅ Fingerprint saved")

    return True


# ================= GET EMPTY SLOT =================
def get_next_finger_id(users):

    fid = 1

    while fid in users:

        fid += 1

    return fid


# ================= ENROLL FINGERPRINT =================
def enroll_fingerprint_auto():

    sensor = connect_fingerprint()

    if not sensor:

        return None

    users = load_users()

    # ================= AUTO SLOT =================
    finger_id = get_next_finger_id(users)

    print("\n==============================")
    print(" FINGERPRINT ENROLLMENT")
    print("==============================")

    print(f"📌 Auto Slot : {finger_id}")

    # ================= FIRST SCAN =================
    print("\n👉 Tempelkan sidik jari...")

    while True:

        try:

            if (
                sensor.read_image()
                == adafruit_fingerprint.OK
            ):

                if (
                    sensor.convert(1)
                    == adafruit_fingerprint.OK
                ):

                    print("✅ Scan pertama berhasil")

                    break

                else:

                    print(
                        "⚠️ Convert gagal, "
                        "coba lagi..."
                    )

        except Exception as e:

            print(f"⚠️ Sensor error : {e}")

            logger.log_error(
                f"Fingerprint scan error: {e}"
            )

            sensor = connect_fingerprint()

            if not sensor:

                return None

        time.sleep(0.1)

    # ================= REMOVE FINGER =================
    print("\n👉 Lepas jari...")

    while (
        sensor.read_image()
        != adafruit_fingerprint.NOFINGER
    ):

        time.sleep(0.1)

    time.sleep(1)

    # ================= SECOND SCAN =================
    print("\n👉 Tempelkan lagi jari yang sama...")

    while True:

        try:

            if (
                sensor.read_image()
                == adafruit_fingerprint.OK
            ):

                if (
                    sensor.convert(2)
                    == adafruit_fingerprint.OK
                ):

                    print("✅ Scan kedua berhasil")

                    break

                else:

                    print(
                        "⚠️ Convert gagal, "
                        "coba lagi..."
                    )

        except Exception as e:

            print(f"⚠️ Sensor error : {e}")

            logger.log_error(
                f"Fingerprint scan error: {e}"
            )

            sensor = connect_fingerprint()

            if not sensor:

                return None

        time.sleep(0.1)

    # ================= CREATE MODEL =================
    while True:

        try:

            result = sensor.create_model()

            if result == adafruit_fingerprint.OK:

                print(
                    "✅ Fingerprint model created"
                )

                break

            elif (
                result
                == adafruit_fingerprint.ENROLLMISMATCH
            ):

                logger.log_auth(
                    "UNKNOWN",
                    "FINGERPRINT_ENROLL",
                    "MISMATCH"
                )

                print(
                    "⚠️ Sidik jari tidak cocok"
                )

                return None

            else:

                print(
                    "⚠️ Create model failed"
                )

        except Exception as e:

            print(f"⚠️ Create model error : {e}")

            logger.log_error(
                f"Fingerprint create model error: {e}"
            )

        time.sleep(1)

    # ================= STORE =================
    try:

        result = sensor.store(finger_id)

        if result == adafruit_fingerprint.OK:

            print(
                f"✅ Fingerprint stored "
                f"in slot {finger_id}"
            )

            return finger_id

        else:

            logger.log_error(
                f"Fingerprint store failed: {result}"
            )

            print(
                f"❌ Store failed : {result}"
            )

            return None

    except Exception as e:

        logger.log_error(
            f"Fingerprint store error: {e}"
        )

        print(f"❌ Store error : {e}")

        return None


# ================= AUTO ENROLL =================
def auto_enroll(user_name):
    
    start_enroll()
    try:

        print("\n================================")
        print("       AUTO ENROLL USER")
        print("================================")

        # ================= USER NAME =================
        name = user_name.strip()

        if not name:

            print("\n❌ Nama tidak boleh kosong")

            return

        print(f"\n👤 USER : {name}")

        # ================= LOGGER =================
        logger.log_system(
            "Auto enrollment started"
        )

        logger.log_enrollment(

            user=name,

            step="AUTO_ENROLL",

            status="STARTED",

            detail="Enrollment started"
        )

        # ================= FACE DATASET =================
        print("\n================================")
        print(" FACE DATASET CAPTURE")
        print("================================")

        try:

            subprocess.run(
                [
                    FACE_PY,
                    "-m",
                    FACE_DATASET_MODULE,
                    name
                ],
                check=True
            )

            logger.log_enrollment(

                user=name,

                step="FACE_DATASET",

                status="SUCCESS",

                detail="Face dataset saved"
            )

            logger.log_system(
                f"Face dataset success for {name}"
            )

        except Exception as e:

            logger.log_enrollment(

                user=name,

                step="FACE_DATASET",

                status="FAILED",

                detail=str(e)
            )

            logger.log_error(
                f"Face dataset failed: {e}"
            )

            return

        # ================= FACE TRAIN =================
        print("\n================================")
        print(" FACE TRAINING")
        print("================================")

        try:

            subprocess.run(
                [
                    FACE_PY,
                    "-m",
                    FACE_TRAIN_MODULE
                ],
                check=True
            )

            logger.log_enrollment(

                user=name,

                step="FACE_TRAINING",

                status="SUCCESS",

                detail="Face training completed"
            )

            logger.log_system(
                f"Face training success for {name}"
            )

        except Exception as e:

            print("\n❌ Face training failed")
            print(e)

            logger.log_enrollment(

                user=name,

                step="FACE_TRAINING",

                status="FAILED",

                detail=str(e)
            )

            logger.log_error(
                f"FACE TRAINING ERROR: {e}"
            )

            return

        # ================= RFID =================
        print("\n================================")
        print(" RFID ENROLLMENT")
        print("================================")

        rfid_data = scan_new_rfid()

        if not rfid_data:

            print("\n❌ RFID enrollment failed")

            logger.log_enrollment(

                user=name,

                step="RFID",

                status="FAILED",

                detail="RFID enrollment failed"
            )

            logger.log_error(
                f"RFID enrollment failed for {name}"
            )

            return

        rfid_uid = rfid_data["uid"]

        print(f"\n✅ RFID UID : {rfid_uid}")

        # ================= FINGERPRINT =================
        print("\n================================")
        print(" FINGERPRINT ENROLLMENT")
        print("================================")

        fid = enroll_fingerprint_auto()

        if not fid:

            print("\n❌ Fingerprint enrollment failed")

            logger.log_enrollment(

                user=name,

                step="FINGERPRINT",

                status="FAILED",

                detail="Fingerprint enrollment failed"
            )

            logger.log_error(
                f"Fingerprint enrollment failed for {name}"
            )

            return

        # ================= SAVE FINGERPRINT FIRST =================
        fp_saved = save_fingerprint_user(
            fid,
            name
        )

        if not fp_saved:

            logger.log_enrollment(

                user=name,

                step="SAVE_FINGERPRINT",

                status="FAILED",

                detail="Save fingerprint failed"
            )

            logger.log_error(
                f"Save fingerprint failed for {name}"
            )

            return

        logger.log_fingerprint(
            fid=fid,
            user=name,
            status="ENROLLED"
        )

        logger.log_enrollment(

            user=name,

            step="FINGERPRINT",

            status="SUCCESS",

            detail=f"FID={fid}"
        )

        # ================= SAVE RFID SECOND =================
        rfid_saved = save_rfid_user(
            rfid_uid,
            name
        )

        if not rfid_saved:

            logger.log_enrollment(

                user=name,

                step="SAVE_RFID",

                status="FAILED",

                detail="Save RFID failed"
            )

            logger.log_error(
                f"Save RFID failed for {name}"
            )

            return

        logger.log_rfid(
            uid=rfid_uid,
            user=name,
            status="ENROLLED"
        )

        logger.log_enrollment(

            user=name,

            step="RFID",

            status="SUCCESS",

            detail=f"UID={rfid_uid}"
        )

        # ================= MASTER USER =================
        try:

            add_master_user(
                name,
                rfid_uid,
                fid
            )

            logger.log_system(
                f"Master user created: {name}"
            )

        except Exception as e:

            logger.log_error(
                f"Master user save failed: {e}"
            )

            print(
                "\n❌ Master user failed"
            )

            return

        # ================= FINAL SUCCESS =================
        logger.log_enrollment(

            user=name,

            step="COMPLETE",

            status="SUCCESS",

            detail="Auto enrollment completed"
        )

        logger.log_system(
            f"Auto enrollment completed for {name}"
        )

        print("\n================================")
        print("      AUTO ENROLL SUCCESS")
        print("================================")

        print(f"User : {name}")
        print(f"RFID : {rfid_uid}")
        print(f"FID  : {fid}")

        print("================================")
    
    finally: 
        
        stop_enroll()


# ================= ENTRY =================
if __name__ == "__main__":

    print(
        "\n⚠️ Jalankan lewat enrollment_listener.py"
    )
