import os

from core.auth.master_user import load_master_users
from core.auth.rfid_auth import load_cards
from core.auth.fingerprint_auth import load_users


FACE_DATASET_PATH = "data/face/dataset"


# ================= LOAD DATA =================
master_users = load_master_users()
rfid_cards = load_cards()
finger_users = load_users()


# ================= GET FACE USERS =================
def get_face_users():

    if not os.path.exists(FACE_DATASET_PATH):
        return {}

    result = {}

    for user in os.listdir(FACE_DATASET_PATH):

        user_path = os.path.join(
            FACE_DATASET_PATH,
            user
        )

        if not os.path.isdir(user_path):
            continue

        total_images = 0

        conditions = set()
        poses = set()

        # ================= RECURSIVE SCAN =================
        for root, dirs, files in os.walk(user_path):

            relative_path = os.path.relpath(
                root,
                user_path
            )

            parts = relative_path.split(os.sep)

            # condition
            if len(parts) >= 1 and parts[0] != ".":

                conditions.add(parts[0])

            # pose
            if len(parts) >= 2:

                poses.add(parts[1])

            # count images
            for file in files:

                if file.lower().endswith((
                    ".jpg",
                    ".jpeg",
                    ".png"
                )):

                    total_images += 1

        result[user] = {
            "conditions": sorted(list(conditions)),
            "poses": sorted(list(poses)),
            "total_images": total_images
        }

    return result


# ================= MAIN CHECK =================
def check_integrity():

    print("\n=============================================")
    print("      DATASET INTEGRITY CHECK")
    print("=============================================")

    face_users = get_face_users()

    all_users = set()

    # ================= COLLECT USERS =================
    all_users.update(face_users.keys())
    all_users.update(master_users.keys())
    all_users.update(rfid_cards.values())
    all_users.update(finger_users.values())

    if not all_users:

        print("\n❌ Tidak ada user ditemukan\n")

        return

    # ================= USER LOOP =================
    for user in sorted(all_users):

        print(f"\nUSER : {user}")

        print("-" * 45)

        # ================= FACE =================
        if user in face_users:

            data = face_users[user]

            print("[FACE]          OK")

            print(
                f"  Images        : "
                f"{data['total_images']}"
            )

            print(
                f"  Conditions    : "
                f"{', '.join(data['conditions'])}"
            )

            print(
                f"  Poses         : "
                f"{', '.join(data['poses'])}"
            )

        else:

            print("[FACE]          MISSING")

        # ================= RFID =================
        rfid_ok = user in rfid_cards.values()

        if rfid_ok:

            print("[RFID]          OK")

        else:

            print("[RFID]          MISSING")

        # ================= FINGERPRINT =================
        finger_ok = user in finger_users.values()

        if finger_ok:

            print("[FINGERPRINT]   OK")

        else:

            print("[FINGERPRINT]   MISSING")

        # ================= MASTER =================
        if user in master_users:

            data = master_users[user]

            print("[MASTER]        OK")

            print(
                f"  RFID UID      : "
                f"{data['rfid']}"
            )

            print(
                f"  Finger ID     : "
                f"{data['finger']}"
            )

        else:

            print("[MASTER]        MISSING")

        # ================= STATUS =================
        healthy = (
            user in face_users
            and rfid_ok
            and finger_ok
            and user in master_users
        )

        if healthy:

            print("\nSTATUS : HEALTHY")

        else:

            print("\nSTATUS : WARNING / INCOMPLETE")

    print("\n=============================================\n")


# ================= ENTRY =================
if __name__ == "__main__":
    check_integrity()
