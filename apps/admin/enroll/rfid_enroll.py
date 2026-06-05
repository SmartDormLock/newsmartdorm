import sys
sys.stdout.reconfigure(encoding="utf-8")

import core.utils.logger as logger

from core.auth.rfid_auth import (
    scan_new_rfid,
    load_cards,
    save_cards
)

from core.auth.master_user import (
    add_master_user
)

from core.system.system_state import (
    start_enroll,
    stop_enroll
)


# ================= SAVE RFID =================
def save_rfid_user(uid, name):

    cards = load_cards()

    # ================= DUPLICATE CHECK =================
    if uid in cards:

        print("\n? RFID already used")
        print(f"UID  : {uid}")
        print(f"User : {cards[uid]}")

        return False

    cards[uid] = name

    save_cards(cards)

    print("? RFID saved")

    return True


# ================= RFID ENROLL =================
def enroll_rfid_only(user_name):

    start_enroll()

    try:

        print("\n================================")
        print("       RFID ENROLLMENT")
        print("================================")

        # ================= USER NAME =================
        name = user_name.strip()

        if not name:

            print("\n? Nama tidak boleh kosong")

            return False

        print(f"\n?? USER : {name}")

        logger.log_system(
            f"RFID enrollment started for {name}"
        )

        logger.log_enrollment(

            user=name,

            step="RFID_ENROLL",

            status="STARTED",

            detail="RFID enrollment started"
        )

        # ================= SCAN RFID =================
        print("\nTempelkan kartu RFID...")

        rfid_data = scan_new_rfid()

        if not rfid_data:

            print("\n? RFID enrollment failed")

            logger.log_enrollment(

                user=name,

                step="RFID_SCAN",

                status="FAILED",

                detail="RFID scan failed"
            )

            logger.log_error(
                f"RFID scan failed for {name}"
            )

            return False

        rfid_uid = rfid_data["uid"]

        print(f"\n? RFID UID : {rfid_uid}")

        # ================= SAVE RFID =================
        saved = save_rfid_user(
            rfid_uid,
            name
        )

        if not saved:

            logger.log_enrollment(

                user=name,

                step="SAVE_RFID",

                status="FAILED",

                detail="RFID already exists"
            )

            return False

        # ================= SAVE MASTER USER =================
        try:

            add_master_user(
                name,
                rfid_uid,
                0
            )

            print(
                "? Master user saved"
            )

        except Exception as e:

            logger.log_error(
                f"Master user save failed: {e}"
            )

            print(
                f"? Master user error : {e}"
            )

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

        logger.log_system(
            f"RFID enrollment success for {name}"
        )

        print("\n================================")
        print("      RFID ENROLL SUCCESS")
        print("================================")

        print(f"User : {name}")
        print(f"RFID : {rfid_uid}")

        print("================================")

        return True

    except Exception as e:

        logger.log_error(
            f"RFID enrollment error: {e}"
        )

        print(f"\n? Error : {e}")

        return False

    finally:

        stop_enroll()


# ================= TEST =================
if __name__ == "__main__":

    name = input(
        "\nMasukkan nama user : "
    )

    enroll_rfid_only(name)
