import os
import shutil
import subprocess

from core.auth.rfid_auth import (
    load_cards,
    save_cards
)

from core.auth.fingerprint_auth import (
    load_users
)

from core.hardware.fingerprint import (
    FingerprintSensor
)

FACE_PY = (
    "/home/raspi5/newsmartdorm/"
    "envs/face_env/bin/python"
)

FACE_TRAIN_MODULE = "apps.face.train_app"

DATASET_PATH = "data/face/dataset"

MASTER_FILE = "data/users/master_users.txt"

FINGERPRINT_FILE = (
    "data/fingerprint/users.txt"
)


# ================= LOAD MASTER =================
def load_master():

    users = {}

    if not os.path.exists(MASTER_FILE):

        return users

    with open(MASTER_FILE, "r") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            try:

                name, rfid_uid, finger_id = (
                    line.split(",")
                )

                users[name] = {
                    "rfid": rfid_uid,
                    "finger": int(finger_id)
                }

            except Exception:

                pass

    return users


# ================= SAVE MASTER =================
def save_master(users):

    with open(MASTER_FILE, "w") as f:

        for name, data in users.items():

            f.write(
                f"{name},"
                f"{data['rfid']},"
                f"{data['finger']}\n"
            )


# ================= GET ALL USERS =================
def get_all_users():

    users = set()

    # ================= DATASET USERS =================
    if os.path.exists(DATASET_PATH):

        for user in os.listdir(DATASET_PATH):

            user_path = os.path.join(
                DATASET_PATH,
                user
            )

            if os.path.isdir(user_path):

                users.add(user)

    # ================= MASTER USERS =================
    master_users = load_master()

    users.update(master_users.keys())

    return sorted(users)


# ================= DELETE FACE =================
def delete_face(name):

    print("\n==============================")
    print(" DELETE FACE DATASET")
    print("==============================")

    user_path = os.path.join(
        DATASET_PATH,
        name
    )

    if os.path.exists(user_path):

        try:

            shutil.rmtree(user_path)

            print("✅ Dataset deleted")
            print(user_path)

            return True

        except Exception as e:

            print("❌ Failed delete dataset")
            print(e)

            return False

    else:

        print("⚠️ Dataset not found")

        return False


# ================= RETRAIN FACE =================
def retrain_face():

    print("\n==============================")
    print(" RETRAIN FACE EMBEDDINGS")
    print("==============================")

    try:

        subprocess.run(
            [
                FACE_PY,
                "-m",
                FACE_TRAIN_MODULE
            ],
            check=True
        )

        print("\n✅ Embeddings retrained")

    except Exception as e:

        print("\n❌ Retrain failed")
        print(e)


# ================= DELETE RFID =================
def delete_rfid(uid):

    print("\n==============================")
    print(" DELETE RFID")
    print("==============================")

    cards = load_cards()

    if uid in cards:

        del cards[uid]

        save_cards(cards)

        print(f"✅ RFID deleted : {uid}")

    else:

        print("⚠️ RFID not found")


# ================= DELETE FINGERPRINT =================
def delete_fingerprint(fid):

    print("\n==============================")
    print(" DELETE FINGERPRINT")
    print("==============================")

    # ================= SENSOR DELETE =================
    try:

        sensor = FingerprintSensor()

        result = sensor.delete(fid)

        if result == 0:

            print(
                f"✅ Fingerprint slot "
                f"{fid} deleted"
            )

        else:

            print(
                f"⚠️ Sensor delete code : "
                f"{result}"
            )

    except Exception as e:

        print("❌ Fingerprint sensor error")
        print(e)

    # ================= UPDATE users.txt =================
    users = load_users()

    if fid in users:

        del users[fid]

    with open(FINGERPRINT_FILE, "w") as f:

        for user_id, username in users.items():

            f.write(
                f"{user_id},"
                f"{username}\n"
            )

    print("✅ Fingerprint users updated")


# ================= DELETE MASTER =================
def delete_master(name):

    print("\n==============================")
    print(" DELETE MASTER USER")
    print("==============================")

    users = load_master()

    if name in users:

        del users[name]

        save_master(users)

        print(f"✅ Master deleted : {name}")

    else:

        print("⚠️ Master user not found")


# ================= MAIN =================
def delete_user():

    print("\n================================")
    print("          DELETE USER")
    print("================================")

    users = get_all_users()

    if not users:

        print("\n❌ Tidak ada user ditemukan\n")

        return

    print("\nRegistered Users:\n")

    for username in users:

        print(f"- {username}")

    print()

    # ================= INPUT USER =================
    name = input(
        "Masukkan nama user yang ingin dihapus : "
    ).strip()

    if name not in users:

        print("\n❌ User tidak ditemukan")

        return

    # ================= LOAD MASTER =================
    master_users = load_master()

    user_data = master_users.get(name)

    # ================= CONFIRM =================
    confirm = input(
        f"\nHapus user '{name}'? (Y/N) : "
    ).strip().lower()

    if confirm != "y":

        print("\n❌ Dibatalkan")

        return

    print("\n================================")
    print(f" Deleting User : {name}")
    print("================================")

    # ================= DELETE FACE =================
    delete_face(name)

    # ================= DELETE RFID =================
    if user_data:

        delete_rfid(user_data["rfid"])

    else:

        print("\n⚠️ RFID skipped")

    # ================= DELETE FINGERPRINT =================
    if user_data:

        delete_fingerprint(
            user_data["finger"]
        )

    else:

        print("\n⚠️ Fingerprint skipped")

    # ================= DELETE MASTER =================
    delete_master(name)

    # ================= RETRAIN =================
    retrain_face()

    # ================= FINISH =================
    print("\n================================")
    print(" USER SUCCESSFULLY DELETED")
    print("================================")


# ================= ENTRY =================
if __name__ == "__main__":
    delete_user()
