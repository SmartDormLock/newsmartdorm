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

        user_path = os.path.join(FACE_DATASET_PATH, user)

        if not os.path.isdir(user_path):
            continue

        total_images = 0
        folders = []

        for angle in os.listdir(user_path):

            angle_path = os.path.join(user_path, angle)

            if os.path.isdir(angle_path):

                folders.append(angle)

                images = [
                    f for f in os.listdir(angle_path)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))
                ]

                total_images += len(images)

        result[user] = {
            "folders": folders,
            "total_images": total_images
        }

    return result


# ================= MAIN CHECK =================
def check_integrity():

    print("\n========== DATASET INTEGRITY CHECK ==========\n")

    face_users = get_face_users()

    all_users = set()

    # face users
    all_users.update(face_users.keys())

    # master users
    all_users.update(master_users.keys())

    # rfid users
    all_users.update(rfid_cards.values())

    # fingerprint users
    all_users.update(finger_users.values())

    for user in sorted(all_users):

        print(f"\nUSER : {user}")
        print("-" * 40)

        # ================= FACE =================
        if user in face_users:

            data = face_users[user]

            print(f"[FACE]          OK")
            print(f"  Images        : {data['total_images']}")
            print(f"  Folders       : {', '.join(data['folders'])}")

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
            print(f"  RFID UID      : {data['rfid']}")
            print(f"  Finger ID     : {data['finger']}")

        else:
            print("[MASTER]        MISSING")

        # ================= STATUS =================
        if (
            user in face_users
            and rfid_ok
            and finger_ok
            and user in master_users
        ):
            print("\nSTATUS : HEALTHY")
        else:
            print("\nSTATUS : WARNING / INCOMPLETE")

    print("\n=============================================\n")


# ================= ENTRY =================
if __name__ == "__main__":
    check_integrity()
