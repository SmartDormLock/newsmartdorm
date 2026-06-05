import sys
import time
import adafruit_fingerprint

import core.utils.logger as logger

sys.stdout.reconfigure(encoding="utf-8")

from core.auth.fingerprint_auth import (
    load_users
)

from core.hardware.fingerprint import (
    FingerprintSensor
)

from core.system.system_state import (
    start_enroll,
    stop_enroll
)

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

            print(
                f"⚠️ Connection failed : {e}"
            )

            logger.log_error(
                f"Fingerprint connect failed: {e}"
            )

            time.sleep(2)

    print(
        "\n❌ Fingerprint sensor gagal connect"
    )

    return None


# ================= SAVE FINGERPRINT =================
def save_fingerprint_user(
    fid,
    name
):

    users = load_users()

    # ================= DUPLICATE SLOT =================
    if fid in users:

        print(
            "\n❌ Finger ID already used"
        )

        print(
            f"Slot : {fid}"
        )

        print(
            f"User : {users[fid]}"
        )

        return False

    # ================= DUPLICATE USER =================
    if name in users.values():

        print(
            "\n❌ User already has fingerprint"
        )

        return False

    users[fid] = name

    with open(
        FINGERPRINT_FILE,
        "w"
    ) as f:

        for user_id, username in users.items():

            f.write(
                f"{user_id},{username}\n"
            )

    print(
        "✅ Fingerprint saved"
    )

    return True


# ================= GET EMPTY SLOT =================
def get_next_finger_id(users):

    fid = 1

    while fid in users:

        fid += 1

    return fid


# ================= ENROLL SENSOR =================
def enroll_fingerprint_auto():

    sensor = connect_fingerprint()

    if not sensor:

        return None

    users = load_users()

    finger_id = get_next_finger_id(
        users
    )

    print("\n==============================")
    print(" FINGERPRINT ENROLLMENT")
    print("==============================")

    print(
        f"📌 Auto Slot : {finger_id}"
    )

    # ================= FIRST SCAN =================
    print(
        "\n👉 Tempelkan sidik jari..."
    )

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

                    print(
                        "✅ Scan pertama berhasil"
                    )

                    break

        except Exception as e:

            logger.log_error(
                f"Fingerprint scan error: {e}"
            )

        time.sleep(0.1)

    # ================= REMOVE =================
    print(
        "\n👉 Lepas jari..."
    )

    while (
        sensor.read_image()
        != adafruit_fingerprint.NOFINGER
    ):

        time.sleep(0.1)

    time.sleep(1)

    # ================= SECOND SCAN =================
    print(
        "\n👉 Tempelkan lagi jari yang sama..."
    )

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

                    print(
                        "✅ Scan kedua berhasil"
                    )

                    break

        except Exception as e:

            logger.log_error(
                f"Fingerprint scan error: {e}"
            )

        time.sleep(0.1)

    # ================= CREATE MODEL =================
    result = sensor.create_model()

    if (
        result
        != adafruit_fingerprint.OK
    ):

        print(
            "\n❌ Create model failed"
        )

        return None

    # ================= STORE =================
    result = sensor.store(
        finger_id
    )

    if (
        result
        != adafruit_fingerprint.OK
    ):

        print(
            "\n❌ Store fingerprint failed"
        )

        return None

    print(
        f"\n✅ Fingerprint stored "
        f"in slot {finger_id}"
    )

    return finger_id


# ================= ENROLL ONLY =================
def enroll_fingerprint_only(
    user_name
):

    start_enroll()

    try:

        print("\n================================")
        print("    FINGERPRINT ENROLLMENT")
        print("================================")

        name = user_name.strip()

        if not name:

            print(
                "\n❌ Nama tidak boleh kosong"
            )

            return False

        print(
            f"\n👤 USER : {name}"
        )

        logger.log_enrollment(

            user=name,

            step="FINGERPRINT_ENROLL",

            status="STARTED",

            detail="Fingerprint enrollment started"
        )

        fid = enroll_fingerprint_auto()

        if not fid:

            print(
                "\n❌ Fingerprint enrollment failed"
            )

            return False

        saved = save_fingerprint_user(
            fid,
            name
        )

        if not saved:

            return False

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

        print("\n================================")
        print(" FINGERPRINT ENROLL SUCCESS")
        print("================================")

        print(
            f"User : {name}"
        )

        print(
            f"FID  : {fid}"
        )

        print(
            "================================"
        )

        return True

    except Exception as e:

        logger.log_error(
            f"Fingerprint enrollment error: {e}"
        )

        print(
            f"\n❌ Error : {e}"
        )

        return False

    finally:

        stop_enroll()


# ================= TEST =================
if __name__ == "__main__":

    name = input(
        "\nMasukkan nama user : "
    )

    enroll_fingerprint_only(
        name
    )
