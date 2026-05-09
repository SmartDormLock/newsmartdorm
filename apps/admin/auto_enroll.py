import sys
sys.stdout.reconfigure(encoding='utf-8')

import subprocess
import time

from core.auth.rfid_auth import (
    scan_new_rfid,
    load_cards,
    save_cards
)

from core.auth.fingerprint_auth import load_users
from core.auth.master_user import add_master_user
from core.hardware.fingerprint import FingerprintSensor

import adafruit_fingerprint


# 🔥 PATH ke environment face
FACE_PY = "/home/raspi5/newsmartdorm/envs/face_env/bin/python"

# module face
FACE_DATASET_MODULE = "apps.face.dataset_app"
FACE_TRAIN_MODULE = "apps.face.train_app"


# ================= CONNECT SENSOR SAFE =================
def connect_fingerprint(max_retry=5):

    for i in range(max_retry):

        try:
            print(f"🔌 Connecting fingerprint ({i+1}/{max_retry})...")

            sensor = FingerprintSensor()

            return sensor

        except Exception as e:
            print(f"⚠️ Gagal connect: {e}")

            time.sleep(2)

    print("❌ Fingerprint sensor gagal connect total")

    return None


# ================= SAVE RFID =================
def save_rfid_user(uid, name):

    cards = load_cards()

    cards[uid] = name

    save_cards(cards)

    print("✅ RFID berhasil disimpan ke cards.txt")


# ================= SAVE FINGERPRINT =================
def save_fingerprint_user(fid, name):

    users = load_users()

    users[fid] = name

    with open("data/fingerprint/users.txt", "w") as f:

        for user_id, username in users.items():
            f.write(f"{user_id},{username}\n")

    print("✅ Fingerprint berhasil disimpan ke users.txt")


# ================= FINGERPRINT AUTO =================
def enroll_fingerprint_auto():

    sensor = connect_fingerprint()

    if not sensor:
        return None

    print("\n👉 Tempelkan sidik jari...")

    # ================= SCAN PERTAMA =================
    while True:

        try:
            if sensor.read_image() == adafruit_fingerprint.OK:

                if sensor.convert(1) == adafruit_fingerprint.OK:

                    print("✅ Scan pertama berhasil")

                    break

                else:
                    print("⚠️ Gagal convert scan pertama, coba lagi...")

        except Exception as e:

            print(f"⚠️ Error sensor: {e}")

            sensor = connect_fingerprint()

            if not sensor:
                return None

        time.sleep(0.1)

    # ================= LEPAS JARI =================
    print("👉 Lepas jari...")

    while sensor.read_image() != adafruit_fingerprint.NOFINGER:
        time.sleep(0.1)

    time.sleep(1)

    # ================= SCAN KEDUA =================
    print("👉 Tempelkan lagi jari yang sama...")

    while True:

        try:
            if sensor.read_image() == adafruit_fingerprint.OK:

                if sensor.convert(2) == adafruit_fingerprint.OK:

                    print("✅ Scan kedua berhasil")

                    break

                else:
                    print("⚠️ Gagal convert scan kedua, coba lagi...")

        except Exception as e:

            print(f"⚠️ Error sensor: {e}")

            sensor = connect_fingerprint()

            if not sensor:
                return None

        time.sleep(0.1)

    # ================= CREATE MODEL =================
    while True:

        try:
            result = sensor.create_model()

            if result == adafruit_fingerprint.OK:

                print("✅ Model fingerprint berhasil dibuat")

                break

            elif result == adafruit_fingerprint.ENROLLMISMATCH:

                print("⚠️ Sidik jari tidak cocok, scan ulang...")

            else:
                print("⚠️ Gagal create model, retry...")

        except Exception as e:
            print(f"⚠️ Error create model: {e}")

        time.sleep(1)

    # ================= STORE =================
    for i in range(1, 128):

        try:
            result = sensor.store(i)

            if result == adafruit_fingerprint.OK:

                print(f"✅ Fingerprint disimpan di ID {i}")

                return i

        except Exception as e:

            print(f"⚠️ Error saat store: {e}")

            sensor = connect_fingerprint()

            if not sensor:
                return None

    print("❌ Tidak ada slot kosong")

    return None


# ================= AUTO ENROLL =================
def auto_enroll():

    print("\n========== AUTO ENROLL USER ==========")

    name = input("Masukkan nama user: ").strip()

    if not name:

        print("❌ Nama tidak boleh kosong")

        return

    # ================= FACE =================
    print("\n📷 Capture dataset wajah...")

    subprocess.run(
        [FACE_PY, "-m", FACE_DATASET_MODULE],
        check=True
    )

    print("\n🧠 Training wajah...")

    subprocess.run(
        [FACE_PY, "-m", FACE_TRAIN_MODULE],
        check=True
    )

    # ================= RFID =================
    print("\n📡 Scan RFID...")

    rfid_data = scan_new_rfid()

    if not rfid_data:

        print("❌ RFID gagal")

        return

    rfid_uid = rfid_data["uid"]

    print(f"✅ RFID UID: {rfid_uid}")

    # ================= FINGERPRINT =================
    print("\n👉 Enroll fingerprint...")

    fid = enroll_fingerprint_auto()

    if not fid:

        print("❌ Fingerprint gagal")

        return

    # ================= SAVE RFID DB =================
    save_rfid_user(rfid_uid, name)

    # ================= SAVE FINGERPRINT DB =================
    save_fingerprint_user(fid, name)

    # ================= MASTER SYNC =================
    add_master_user(name, rfid_uid, fid)

    print("\n🎉 AUTO ENROLL SELESAI!")
    print("====================================")
    print(f"User : {name}")
    print(f"RFID : {rfid_uid}")
    print(f"FID  : {fid}")
    print("====================================")


# ================= ENTRY =================
if __name__ == "__main__":
    auto_enroll()
