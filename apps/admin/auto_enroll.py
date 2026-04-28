import subprocess
import time

from core.auth.rfid_auth import scan_rfid
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


# ================= FINGERPRINT AUTO =================
def enroll_fingerprint_auto():
    sensor = connect_fingerprint()

    if not sensor:
        return None

    print("\n👉 Tempelkan sidik jari...")

    # tunggu finger
    while True:
        try:
            if sensor.read_image() == adafruit_fingerprint.OK:
                break
        except:
            print("⚠️ Sensor disconnect, reconnect...")
            sensor = connect_fingerprint()
            if not sensor:
                return None
        time.sleep(0.1)

    if sensor.convert(1) != adafruit_fingerprint.OK:
        print("❌ Gagal baca jari pertama")
        return None

    print("👉 Lepas jari...")
    time.sleep(1)

    # tunggu dilepas
    while sensor.read_image() != adafruit_fingerprint.NOFINGER:
        time.sleep(0.1)

    print("👉 Tempelkan lagi jari yang sama...")

    while True:
        try:
            if sensor.read_image() == adafruit_fingerprint.OK:
                break
        except:
            print("⚠️ Sensor disconnect, reconnect...")
            sensor = connect_fingerprint()
            if not sensor:
                return None
        time.sleep(0.1)

    if sensor.convert(2) != adafruit_fingerprint.OK:
        print("❌ Gagal baca jari kedua")
        return None

    if sensor.create_model() != adafruit_fingerprint.OK:
        print("❌ Gagal create model")
        return None

    # cari slot kosong
    for i in range(1, 128):
        try:
            if sensor.load(i) != adafruit_fingerprint.OK:
                if sensor.store(i) == adafruit_fingerprint.OK:
                    print(f"✅ Fingerprint disimpan di ID {i}")
                    return i
        except:
            print("⚠️ Error saat store, retry...")
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
    subprocess.run([FACE_PY, "-m", FACE_DATASET_MODULE], check=True)

    print("\n🧠 Training wajah...")
    subprocess.run([FACE_PY, "-m", FACE_TRAIN_MODULE], check=True)

    # ================= RFID =================
    print("\n📡 Scan RFID...")
    rfid_name = scan_rfid()

    if not rfid_name:
        print("❌ RFID gagal")
        return

    print(f"✅ RFID terbaca: {rfid_name}")

    # ================= FINGERPRINT =================
    print("\n👉 Enroll fingerprint...")
    fid = enroll_fingerprint_auto()

    if not fid:
        print("❌ Fingerprint gagal")
        return

    # ================= MASTER SYNC =================
    add_master_user(name, rfid_name, fid)

    print("\n🎉 AUTO ENROLL SELESAI!")
    print("====================================")
    print(f"User : {name}")
    print(f"RFID : {rfid_name}")
    print(f"FID  : {fid}")
    print("====================================")


# ================= ENTRY =================
if __name__ == "__main__":
    auto_enroll()
