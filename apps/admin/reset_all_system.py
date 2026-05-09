import os
import shutil

from core.hardware.fingerprint import FingerprintSensor


# ================= PATH CONFIG =================
FACE_DATASET_PATH = "data/face/dataset"
FACE_EMBEDDINGS = "data/face/embeddings.pkl"

RFID_FILE = "data/rfid/cards.txt"
FINGER_FILE = "data/fingerprint/users.txt"
MASTER_FILE = "data/users/master_users.txt"


# ================= RESET FACE =================
def reset_face():

    print("\n?? Reset FACE system...")

    # reset dataset
    if os.path.exists(FACE_DATASET_PATH):

        shutil.rmtree(FACE_DATASET_PATH)

    os.makedirs(FACE_DATASET_PATH, exist_ok=True)

    print("? Face dataset cleared")

    # reset embeddings
    if os.path.exists(FACE_EMBEDDINGS):

        os.remove(FACE_EMBEDDINGS)

        print("? embeddings.pkl deleted")

    else:

        print("?? embeddings.pkl tidak ditemukan")


# ================= RESET RFID =================
def reset_rfid():

    print("\n?? Reset RFID database...")

    os.makedirs(os.path.dirname(RFID_FILE), exist_ok=True)

    with open(RFID_FILE, "w") as f:
        pass

    print("? RFID cleared")


# ================= RESET FINGERPRINT =================
def reset_fingerprint():

    print("\n?? Reset fingerprint sensor...")

    try:

        sensor = FingerprintSensor()

        result = sensor.empty()

        if result == 0:

            print("? Fingerprint sensor cleared")

        else:

            print(f"? Failed clear sensor. Code: {result}")

    except Exception as e:

        print(f"? Sensor error: {e}")

    # reset users.txt
    os.makedirs(os.path.dirname(FINGER_FILE), exist_ok=True)

    with open(FINGER_FILE, "w") as f:
        pass

    print("? Fingerprint users.txt cleared")


# ================= RESET MASTER =================
def reset_master():

    print("\n?? Reset master users...")

    os.makedirs(os.path.dirname(MASTER_FILE), exist_ok=True)

    with open(MASTER_FILE, "w") as f:
        pass

    print("? Master users cleared")


# ================= MAIN =================
def main():

    print("\n========== FULL SYSTEM RESET ==========")

    print("""
?? WARNING:
Semua data berikut akan dihapus:

- Face Dataset
- Face Embeddings
- RFID Database
- Fingerprint Sensor
- Fingerprint Users
- Master Users
""")

    confirm = input("Ketik 'RESET' untuk lanjut: ").strip()

    if confirm != "RESET":

        print("\n? Reset dibatalkan")
        return

    # ================= EXECUTE =================
    reset_face()

    reset_rfid()

    reset_fingerprint()

    reset_master()

    print("\n?? FULL SYSTEM RESET COMPLETE")
    print("=====================================\n")


# ================= ENTRY =================
if __name__ == "__main__":
    main()
